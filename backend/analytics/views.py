from django.db.models import Avg, Count, Max, Q
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.permissions import IsStaffRole
from drives.models import Drive
from engine.nlp import SKILLS
from engine.risk import at_risk
from jobs.models import Company, JobDescription
from offers.models import Offer
from students.models import StudentProfile


class SummaryView(APIView):
    permission_classes = [IsStaffRole]

    def get(self, request):
        S = StudentProfile.objects
        br = S.values("branch").annotate(t=Count("id"), p=Count("id", filter=Q(placed=True)))
        skill = {k: [0, 0] for k in SKILLS}
        for p in S.all():
            for s in p.skills:
                if s in skill:
                    skill[s][0] += 1
                    skill[s][1] += p.placed
        ofr = Offer.objects
        return Response({
            "total": S.count(),
            "ready": S.filter(readiness_score__gte=60).count(),
            "placed": S.filter(placed=True).count(),
            "active_jobs": JobDescription.objects.filter(status="open").count(),
            "upcoming_drives": Drive.objects.filter(status="scheduled").count(),
            "branch_conversion": [{"branch": b["branch"], "rate": round(100 * b["p"] / b["t"])} for b in br],
            "skill_conversion": sorted(
                [{"skill": k, "rate": round(100 * v[1] / v[0])} for k, v in skill.items() if v[0] >= 10],
                key=lambda x: -x["rate"])[:10],
            "offers": ofr.aggregate(avg=Avg("ctc_lpa"), top=Max("ctc_lpa"), total=Count("id")),
            "offer_status": list(ofr.values("status").annotate(n=Count("id"))),
            "docs_status": list(ofr.values("docs_status").annotate(n=Count("id"))),
            "package_by_company": list(ofr.values(company=("job__company__name")).annotate(avg=Avg("ctc_lpa"))),
            "pipeline": list(Company.objects.annotate(
                jobs_n=Count("jobs", distinct=True), offers_n=Count("jobs__offers", distinct=True)
            ).values("name", "jobs_n", "offers_n")),
        })


class AtRiskView(APIView):
    permission_classes = [IsStaffRole]

    def get(self, request):
        return Response(at_risk())