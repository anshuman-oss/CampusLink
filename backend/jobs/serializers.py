from rest_framework import serializers
from .models import JobDescription, Match


class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    shortlisted = serializers.SerializerMethodField()

    class Meta:
        model = JobDescription
        exclude = ["company", "is_active", "deleted_at", "updated_at"]
        read_only_fields = ["created_at"]

    def get_shortlisted(self, o):
        return o.matches.filter(status="shortlisted").count()


class MatchSerializer(serializers.ModelSerializer):
    candidate_id = serializers.SerializerMethodField()          # anonymised for recruiters
    branch = serializers.CharField(source="student.branch")
    cgpa = serializers.DecimalField(source="student.cgpa", max_digits=4, decimal_places=2)
    skills = serializers.ListField(source="student.skills")

    class Meta:
        model = Match
        fields = ["id", "candidate_id", "branch", "cgpa", "skills", "fit_score", "level",
                  "status", "eligible", "explanation"]

    def get_candidate_id(self, m):
        return f"CAND-{m.student_id:04d}"

    def to_representation(self, m):
        data = super().to_representation(m)
        if self.context["request"].user.role == "officer":     # only the officer sees identity
            data["student_id"] = m.student_id
            data["roll_no"] = m.student.roll_no
            data["name"] = m.student.user.get_full_name() or m.student.user.username
        return data