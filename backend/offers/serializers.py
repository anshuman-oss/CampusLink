from rest_framework import serializers
from .models import Offer


class OfferSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    roll_no = serializers.CharField(source="student.roll_no", read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)
    company = serializers.CharField(source="job.company.name", read_only=True)

    class Meta:
        model = Offer
        fields = ["id", "student", "student_name", "roll_no", "job", "job_title", "company",
                  "ctc_lpa", "is_ppo", "status", "docs_status", "bond_signed",
                  "doc_deadline", "joining_date", "remarks", "created_at"]
        read_only_fields = ["created_at"]

    def get_student_name(self, o):
        return o.student.user.get_full_name() or o.student.user.username

    def validate(self, d):
        if self.instance is None and Offer.objects.filter(student=d["student"], job=d["job"]).exists():
            raise serializers.ValidationError("An offer for this student and job already exists.")
        return d