from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from accounts.permissions import IsRecruiter
from engine.matcher import run_match
from engine.nlp import parse_jd
from .models import JobDescription, Match
from .serializers import JobSerializer, MatchSerializer


class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    permission_classes = [IsRecruiter]

    def get_queryset(self):
        qs = JobDescription.objects.select_related("company")
        u = self.request.user
        return qs.filter(company__user=u) if u.role == "recruiter" else qs

    def perform_create(self, serializer):
        company = getattr(self.request.user, "company", None)
        if company is None:
            raise ValidationError("Only recruiter accounts with a company can post jobs.")
        parsed = parse_jd(self.request.data.get("description", ""))
        extra = {k: v for k, v in parsed.items() if k not in self.request.data}
        serializer.save(company=company, **extra)           # NLP fills skills, CGPA, branches

    @action(detail=True, methods=["post"])
    def match(self, request, pk=None):
        return Response({"matched": run_match(self.get_object())})

    @action(detail=True, methods=["get"])
    def matches(self, request, pk=None):
        job = self.get_object()
        qs = Match.objects.filter(job=job).select_related("student__user")
        return Response(MatchSerializer(qs, many=True, context={"request": request}).data)

    @action(detail=True, methods=["get"])
    def fairness(self, request, pk=None):
        """Shortlisting rate per branch among eligible students (the '80% rule')."""
        job = self.get_object()
        rows = {}
        for m in Match.objects.filter(job=job, eligible=True).select_related("student"):
            r = rows.setdefault(m.student.branch, [0, 0])
            r[0] += 1
            r[1] += int(m.status == "shortlisted")
        rates = {b: round(100 * s / t) for b, (t, s) in rows.items() if t >= 3}
        top = max(rates.values()) if rates else 0
        ratio = round(min(rates.values()) / top, 2) if top else 1
        return Response({"rates": [{"branch": b, "rate": r} for b, r in sorted(rates.items())],
                         "ratio": ratio, "flag": ratio < 0.8})