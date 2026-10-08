from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from accounts.notify import notify
from accounts.permissions import IsOfficer
from .models import Offer
from .serializers import OfferSerializer
class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    def get_permissions(self):
        return [IsAuthenticated()] if self.action in ("list", "retrieve") else [IsOfficer()]
    def get_queryset(self):
        qs = Offer.objects.select_related("student__user", "job__company")
        u = self.request.user
        if u.role == "student":
            return qs.filter(student__user=u)
        if u.role == "recruiter":
            return qs.filter(job__company__user=u)
        return qs
    def perform_create(self, serializer):
        o = serializer.save()
        notify(o.student.user, "Offer issued", f"{o.job.title} at {o.ctc_lpa} LPA")
    def perform_update(self, serializer):
        o = serializer.save()
        notify(o.student.user, "Offer update", f"Status: {o.status}, documents: {o.docs_status}")
        if o.status in ("accepted", "joined") and not o.student.placed:
            o.student.placed = True
            o.student.save(update_fields=["placed", "updated_at"])