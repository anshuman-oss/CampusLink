import pdfplumber
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.permissions import IsStudent, IsStaffRole
from engine.nlp import extract_skills
from engine.scoring import readiness
from .models import StudentProfile
from .serializers import StudentSerializer, StudentAdminSerializer
from .services import refresh_readiness

ROLES = {
    "Backend Developer": ["python", "django", "sql", "rest api", "git", "docker"],
    "Full-Stack Developer": ["javascript", "react", "node", "sql", "rest api", "git"],
    "Cloud Engineer": ["aws", "cloud", "docker", "linux", "git"],
    "Data Analyst": ["sql", "excel", "python", "machine learning", "communication"],
}


class MeView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        p = request.user.profile
        data = StudentSerializer(p).data
        data["breakdown"] = readiness(p)[2]
        return Response(data)

    def patch(self, request):
        p = request.user.profile
        s = StudentSerializer(p, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        data = StudentSerializer(p).data
        data["breakdown"] = refresh_readiness(p)
        data["readiness_score"], data["readiness_level"] = p.readiness_score, p.readiness_level
        return Response(data)


class ResumeView(APIView):
    permission_classes = [IsStudent]

    def post(self, request):
        f = request.FILES["resume"]
        with pdfplumber.open(f) as pdf:
            text = "\n".join((pg.extract_text() or "") for pg in pdf.pages)
        f.seek(0)
        p = request.user.profile
        p.resume_file, p.resume_text = f, text
        p.skills = sorted(set(p.skills) | set(extract_skills(text)))
        p.save()
        parts = refresh_readiness(p)
        return Response({"skills": p.skills, "readiness": p.readiness_score,
                         "level": p.readiness_level, "breakdown": parts})


class SkillGapView(APIView):
    permission_classes = [IsStudent]

    def post(self, request):
        role = request.data.get("role")
        if role not in ROLES:
            return Response({"error": "Unknown role", "roles": list(ROLES)}, status=400)
        p = request.user.profile
        p.target_role = role
        p.save(update_fields=["target_role", "updated_at"])
        have = set(p.skills)
        need = ROLES[role]
        missing = [s for s in need if s not in have]
        return Response({"role": role, "have": [s for s in need if s in have], "missing": missing,
                         "coverage": round(100 * (len(need) - len(missing)) / len(need))})

    def get(self, request):
        return Response({"roles": list(ROLES)})


class StudentViewSet(viewsets.ModelViewSet):
    """Officer/mentor: list, view, update scores, soft-delete students."""
    permission_classes = [IsStaffRole]
    serializer_class = StudentAdminSerializer

    def get_queryset(self):
        qs = StudentProfile.objects.select_related("user")
        if self.request.user.role == "mentor":
            qs = qs.filter(mentor=self.request.user)
        return qs

    def perform_update(self, serializer):
        refresh_readiness(serializer.save())