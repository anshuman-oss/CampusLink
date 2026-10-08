from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.notify import notify
from accounts.permissions import IsOfficer
from jobs.models import Match
from .models import Drive
from .scheduler import find_conflicts, suggest_slot
from .serializers import DriveSerializer

class DriveViewSet(viewsets.ModelViewSet):
    queryset = Drive.objects.select_related("job__company")
    serializer_class = DriveSerializer
    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        return [IsOfficer()]
    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        draft = Drive(**s.validated_data)
        conflicts = find_conflicts(draft)
        if conflicts:
            return Response({"saved": False, "conflicts": conflicts,
                             "suggested_slot": suggest_slot(draft)}, status=409)
        drive = s.save()
        for m in Match.objects.filter(job=drive.job, status="shortlisted").select_related("student__user"):
            notify(m.student.user, "Interview scheduled",
                   f"{drive.job.title}: {drive.date} at {drive.start_time}, {drive.venue}")
        return Response({"saved": True, "id": drive.id}, status=201)