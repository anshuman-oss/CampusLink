import csv
import io
import logging
import pdfplumber
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.permissions import IsOfficer, IsStaffRole, IsStudent
from engine.matcher import rematch_student
from engine.nlp import SKILLS, extract_skills
from engine.scoring import readiness
from jobs.models import Match
from .models import StudentProfile
from .serializers import RosterSerializer, StudentSerializer
from .services import refresh_readiness

log = logging.getLogger(__name__)

ROLES = {
    "Backend Developer": ["python", "django", "sql", "rest api", "git", "docker"],
    "Full-Stack Developer": ["javascript", "react", "node", "sql", "rest api", "git"],
    "Cloud Engineer": ["aws", "cloud", "docker", "linux", "git"],
    "Data Analyst": ["sql", "excel", "python", "machine learning", "communication"],
}


def rematch(p):
    try:
        rematch_student(p)
    except Exception:
        log.exception("Could not refresh matches for %s", p.roll_no)


def me_payload(p):
    data = StudentSerializer(p).data
    data["breakdown"] = readiness(p)[2]
    data["skill_options"] = sorted(SKILLS)
    return data


class MeView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        return Response(me_payload(request.user.profile))

    def patch(self, request):
        p = request.user.profile
        s = StudentSerializer(p, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        v = s.validated_data
        if "skills" in v:                      # only skills the matching engine understands
            v["skills"] = [x for x in dict.fromkeys(str(i).lower().strip() for i in v["skills"]) if x in SKILLS]
        if "certifications" in v:
            v["certifications"] = [str(c).strip()[:80] for c in v["certifications"] if str(c).strip()][:20]
        if "projects" in v:
            v["projects"] = [{"title": str(x.get("title", "")).strip()[:80], "desc": str(x.get("desc", "")).strip()[:300]}
                             for x in v["projects"] if isinstance(x, dict) and str(x.get("title", "")).strip()][:10]
        s.save()
        refresh_readiness(p)
        rematch(p)
        return Response(me_payload(p))


class ResumeView(APIView):
    permission_classes = [IsStudent]

    def post(self, request):
        f = request.FILES.get("resume")
        if not f:
            return Response({"detail": "Choose a PDF file."}, status=400)
        try:
            with pdfplumber.open(f) as pdf:
                text = "\n".join((pg.extract_text() or "") for pg in pdf.pages)
        except Exception:
            return Response({"detail": "Could not read this PDF."}, status=400)
        f.seek(0)
        p = request.user.profile
        p.resume_file, p.resume_text = f, text
        p.skills = sorted(set(p.skills) | set(extract_skills(text)))
        p.save()
        parts = refresh_readiness(p)
        rematch(p)
        return Response({"skills": p.skills, "readiness": p.readiness_score,
                         "level": p.readiness_level, "breakdown": parts})


class SkillGapView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        return Response({"roles": list(ROLES)})

    def post(self, request):
        role = request.data.get("role")
        if role not in ROLES:
            return Response({"error": "Unknown role", "roles": list(ROLES)}, status=400)
        p = request.user.profile
        p.target_role = role
        p.save(update_fields=["target_role", "updated_at"])
        have, need = set(p.skills), ROLES[role]
        missing = [s for s in need if s not in have]
        return Response({"role": role, "have": [s for s in need if s in have], "missing": missing,
                         "coverage": round(100 * (len(need) - len(missing)) / len(need))})


class MyMatchesView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        ms = (Match.objects.filter(student=request.user.profile)
              .select_related("job__company").order_by("-fit_score")[:10])
        return Response([{"id": m.id, "company": m.job.company.name, "title": m.job.title,
                          "ctc_lpa": m.job.ctc_lpa, "fit_score": m.fit_score, "status": m.status,
                          "explanation": m.explanation} for m in ms])


class RosterViewSet(viewsets.ModelViewSet):
    """Officer: add, import, edit and soft-delete students. Mentors: read-only on their mentees."""
    serializer_class = RosterSerializer

    def get_permissions(self):
        return [IsStaffRole()] if self.action in ("list", "retrieve") else [IsOfficer()]

    def get_queryset(self):
        qs = StudentProfile.objects.select_related("user", "mentor").order_by("roll_no")
        if self.request.user.role == "mentor":
            qs = qs.filter(mentor=self.request.user)
        return qs

    def perform_destroy(self, inst):
        inst.user.delete()                  # soft delete: blocks login and hides the profile

    @action(detail=True, methods=["post"], url_path="test-email")
    def test_email(self, request, pk=None):
        """Officer: send a test email to one student and report the real result."""
        p = self.get_object()
        to = p.user.email
        if not to:
            return Response({"detail": "This student has no email address."}, status=400)
        backend = settings.MAILERS["default"]["BACKEND"]
        try:
            send_mail("CampusLink test email",
                      f"Hello {p.user.first_name or p.roll_no},\n\nThis is a test email from CampusLink. "
                      "If you can read this, email notifications work for your account.",
                      getattr(settings, "NOTIFY_FROM", "placements@campuslink.local"), [to])
        except Exception as e:
            return Response({"detail": f"The email could not be sent: {e}"}, status=502)
        if "console" in backend:
            return Response({"console": True, "detail":
                f"Email mode is 'console', so nothing was delivered to {to}. The message was printed in the "
                "server terminal. Add your Gmail details to the .env file to send real emails."})
        return Response({"console": False, "detail":
            f"Test email sent to {to}. Check the inbox, and the Spam folder, within a minute."})

    @action(detail=False, methods=["post"], url_path="import", parser_classes=[MultiPartParser, FormParser])
    def import_csv(self, request):
        f = request.FILES.get("file")
        if not f:
            return Response({"detail": "Choose a CSV file."}, status=400)
        try:
            rows = list(csv.DictReader(io.StringIO(f.read().decode("utf-8-sig"))))
        except UnicodeDecodeError:
            return Response({"detail": "File must be a UTF-8 CSV."}, status=400)
        added, errors = 0, []
        for i, r in enumerate(rows, start=2):
            data = {k.strip(): (v or "").strip() for k, v in r.items() if k}
            data = {k: v for k, v in data.items() if v != ""}
            s = RosterSerializer(data=data)
            if s.is_valid():
                s.save()
                added += 1
            else:
                msg = "; ".join(f"{k}: {' '.join(map(str, v))}" for k, v in s.errors.items())
                errors.append({"row": i, "roll_no": data.get("roll_no", ""), "error": msg})
        return Response({"added": added, "errors": errors})