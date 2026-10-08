from django.db import models
from core.models import SoftDeleteModel
class Offer(SoftDeleteModel):
    STATUS = [("issued", "Issued"), ("accepted", "Accepted"), ("deferred", "Deferred"),
              ("withdrawn", "Withdrawn"), ("joined", "Joined")]
    DOCS = [("pending", "Pending"), ("submitted", "Submitted"), ("verified", "Verified")]
    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE,
                                related_name="offers")
    job = models.ForeignKey("jobs.JobDescription", on_delete=models.CASCADE,
                            related_name="offers")
    ctc_lpa = models.DecimalField(max_digits=5, decimal_places=2)
    is_ppo = models.BooleanField(default=False)
    status = models.CharField(max_length=12, choices=STATUS, default="issued")
    docs_status = models.CharField(max_length=12, choices=DOCS, default="pending")
    bond_signed = models.BooleanField(default=False)
    offer_letter = models.FileField(upload_to="offers/", blank=True, null=True)
    doc_deadline = models.DateField(null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    remarks = models.CharField(max_length=200, blank=True)
    
    class Meta(SoftDeleteModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.roll_no} - {self.job.title} ({self.status})"