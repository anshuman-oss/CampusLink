from rest_framework import serializers
from .models import Drive
class DriveSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    company = serializers.CharField(source="job.company.name", read_only=True)
    class Meta:
        model = Drive
        fields = ["id", "job", "job_title", "company", "venue", "panel", "date",
                  "start_time", "end_time", "status"]
    def validate(self, d):
        if d["start_time"] >= d["end_time"]:
            raise serializers.ValidationError("End time must be after start time.")
        return d