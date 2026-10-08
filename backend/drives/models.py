from django.db import models
from core.models import SoftDeleteModel
class Drive(SoftDeleteModel):
    STATUS = [("scheduled", "Scheduled"), ("completed", "Completed"), ("cancelled", "Cancelled")]
    job = models.ForeignKey("jobs.JobDescription", on_delete=models.CASCADE,
                            related_name="drives")
    venue = models.CharField(max_length=60)
    panel = models.CharField(max_length=60)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=12, choices=STATUS, default="scheduled")
    class Meta(SoftDeleteModel.Meta):
        ordering = ["date", "start_time"]
    def __str__(self):
        return f"{self.job.title} on {self.date} {self.start_time}"