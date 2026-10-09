from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Notification, User
from .permissions import IsOfficer
from accounts.mailer import send_email
from .serializers import (NotificationSerializer, ProfileUpdateSerializer, RegisterSerializer,
                          StaffCreateSerializer, strong_password)


class AuthThrottle(AnonRateThrottle):
    scope = "auth"                 # 30 requests per minute (see settings)


# ---------- login / register / logout ----------
class RoleToken(TokenObtainPairSerializer):
    def validate(self, attrs):
        u = User.objects.filter(username=attrs.get("username")).first()
        if u and u.role == "recruiter" and not u.is_approved and u.check_password(attrs.get("password", "")):
            raise AuthenticationFailed("Your account is waiting for approval by the placement officer.")
        data = super().validate(attrs)            # rejects wrong passwords and inactive users
        data["role"] = self.user.role
        data["name"] = self.user.get_full_name() or self.user.username
        return data


class LoginView(TokenObtainPairView):
    serializer_class = RoleToken
    throttle_classes = [AuthThrottle]


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []                   # an old expired token must not block signup
    throttle_classes = [AuthThrottle]

    def post(self, request):
        s = RegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        u = s.save()
        msg = ("Account activated. You can now log in." if u.role == "student"
               else "Registration received. You can log in after the placement officer approves your account.")
        return Response({"detail": msg, "role": u.role}, status=201)


class LogoutView(APIView):
    def post(self, request):
        try:
            RefreshToken(request.data.get("refresh", "")).blacklist()
        except TokenError:
            pass                                   # already invalid: nothing to do
        return Response({"detail": "Logged out."})


# ---------- profile ----------
def me_payload(u):
    d = {"id": u.id, "username": u.username, "first_name": u.first_name, "last_name": u.last_name,
         "name": u.get_full_name() or u.username, "email": u.email, "phone": u.phone,
         "role": u.role, "role_label": u.get_role_display(),
         "date_joined": u.date_joined, "last_login": u.last_login}
    if u.role == "student":
        p = getattr(u, "profile", None)
        if p:
            d["student"] = {"roll_no": p.roll_no, "branch": p.branch, "cgpa": float(p.cgpa),
                            "backlogs": p.backlogs, "readiness_score": p.readiness_score,
                            "readiness_level": p.readiness_level, "placed": p.placed, "batch": p.batch,
                            "mentor": (p.mentor.get_full_name() or p.mentor.username) if p.mentor else None}
    elif u.role == "recruiter":
        c = getattr(u, "company", None)
        d["approved"] = u.is_approved
        if c:
            d["company"] = {"name": c.name, "industry": c.industry,
                            "contact_email": c.contact_email, "jobs": c.jobs.count()}
    elif u.role == "mentor":
        d["mentees"] = u.mentees.count()
    return d


class MeView(APIView):
    def get(self, request):
        return Response(me_payload(request.user))

    def patch(self, request):
        s = ProfileUpdateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d, u = s.validated_data, request.user
        if "email" in d and User.objects.filter(email__iexact=d["email"]).exclude(pk=u.pk).exists():
            raise ValidationError({"email": "This email is used by another account."})
        for f in ("first_name", "last_name", "email", "phone"):
            if f in d:
                setattr(u, f, d[f])
        u.save()
        c = getattr(u, "company", None)
        if u.role == "recruiter" and c:
            if d.get("company_name"):
                c.name = d["company_name"]
            if "industry" in d:
                c.industry = d["industry"]
            c.save()
        return Response(me_payload(u))


class ChangePasswordView(APIView):
    def post(self, request):
        old, new = request.data.get("old_password", ""), request.data.get("new_password", "")
        if not request.user.check_password(old):
            raise ValidationError({"old_password": "Current password is incorrect."})
        strong_password(new, "new_password")
        request.user.set_password(new)
        request.user.save(update_fields=["password"])
        return Response({"detail": "Password changed. Please log in again."})


# ---------- notifications ----------
class NotificationListView(ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationReadView(APIView):
    def post(self, request, pk):
        Notification.objects.filter(pk=pk, user=request.user).update(is_read=True)
        return Response({"ok": True})


# ---------- officer: approvals and staff ----------
class PendingView(APIView):
    permission_classes = [IsOfficer]

    def get(self, request):
        qs = User.objects.filter(role="recruiter", is_approved=False, is_active=True).order_by("date_joined")
        out = []
        for u in qs:
            c = getattr(u, "company", None)
            out.append({"id": u.id, "username": u.username, "name": u.get_full_name(), "email": u.email,
                        "phone": u.phone, "company": c.name if c else "", "date_joined": u.date_joined})
        return Response(out)


class ApproveView(APIView):
    permission_classes = [IsOfficer]

    def post(self, request, pk):
        u = User.objects.filter(pk=pk, role="recruiter", is_approved=False, is_active=True).first()
        if not u:
            return Response({"detail": "No pending recruiter with this id."}, status=404)
        if request.data.get("approve") in (True, "true", "True", 1, "1"):
            u.is_approved = True
            u.save(update_fields=["is_approved"])
            return Response({"detail": f"{u.username} approved."})
        u.delete()                                 # reject = soft delete, login blocked
        return Response({"detail": f"{u.username} rejected."})


class StaffView(APIView):
    permission_classes = [IsOfficer]

    def get(self, request):
        qs = User.objects.filter(role__in=["mentor", "officer"], is_active=True).order_by("role", "username")
        return Response([{"id": u.id, "username": u.username, "name": u.get_full_name() or u.username,
                          "email": u.email, "role": u.role,
                          "mentees": u.mentees.count() if u.role == "mentor" else 0} for u in qs])

    def post(self, request):
        s = StaffCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        u = s.save()
        return Response({"id": u.id, "username": u.username, "role": u.role}, status=201)
    
class LogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []        # works even if the access token has already expired

    def post(self, request):
        try:
            RefreshToken(request.data.get("refresh", "")).blacklist()
        except TokenError:
            pass                       # already invalid: nothing to do
        return Response({"detail": "Logged out."})
    
# @action(detail=True, methods=["post"], url_path="test-email")
# def test_email(self, request, pk=None):
#         """Officer: send a test email to one student and report the real result."""
#         p = self.get_object()
#         to = p.user.email
#         if not to:
#             return Response({"detail": "This student has no email address."}, status=400)
#         try:
#             send_email(to, "CampusLink test email",
#                        f"Hello {p.user.first_name or p.roll_no},\n\nThis is a test email from CampusLink. "
#                        "If you can read this, email notifications work for your account.")
#         except Exception as e:
#             return Response({"detail": f"The email could not be sent: {e}"}, status=502)
#         return Response({"console": False, "detail":
#             f"Test email sent to {to}. Check the inbox, and the Spam folder, within a minute."})   
