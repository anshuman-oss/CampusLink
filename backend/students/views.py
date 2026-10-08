import csv
import io
import pdfplumber
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.permissions import IsOfficer, IsStaffRole, IsStudent
from engine.nlp import extract_skills
from engine.scoring import readiness
from jobs.models import Match
from .models import StudentProfile
from .serializers import RosterSerializer, StudentSerializer
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
        inst.user.delete()               # soft delete: blocks login and hides the profile

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
            data = {k: v for k, v in data.items() if v != ""}        # blank cells use defaults
            s = RosterSerializer(data=data)
            if s.is_valid():
                s.save()
                added += 1
            else:
                msg = "; ".join(f"{k}: {' '.join(map(str, v))}" for k, v in s.errors.items())
                errors.append({"row": i, "roll_no": data.get("roll_no", ""), "error": msg})
        return Response({"added": added, "errors": errors})