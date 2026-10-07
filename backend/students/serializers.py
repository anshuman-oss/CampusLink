from rest_framework import serializers
from .models import StudentProfile


class StudentSerializer(serializers.ModelSerializer):
    """Student's own view: only target_role, skills, projects, certifications are editable."""
    name = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = ["id", "name", "roll_no", "branch", "cgpa", "backlogs", "aptitude_score",
                  "mock_score", "soft_score", "target_role", "skills", "projects",
                  "certifications", "readiness_score", "readiness_level", "placed", "batch"]
        read_only_fields = ["roll_no", "branch", "cgpa", "backlogs", "aptitude_score",
                            "mock_score", "soft_score", "readiness_score", "readiness_level",
                            "placed", "batch"]

    def get_name(self, o):
        return o.user.get_full_name() or o.user.username


class StudentAdminSerializer(StudentSerializer):
    """Officer view: assessment scores are editable too."""
    class Meta(StudentSerializer.Meta):
        read_only_fields = ["roll_no", "readiness_score", "readiness_level", "placed", "batch"]