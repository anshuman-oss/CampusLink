from django.conf import settings
from django.db import models
from core.models import SoftDeleteModel

class Company(SoftDeleteModel):
    soft_cascade = ("jobs",)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="company")
    name = models.CharField(max_length=100)
    industry = models.CharField(max_length=60, blank=True)
    contact_email = models.EmailField(blank=True)

    class Meta(SoftDeleteModel.Meta):
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name
    
class JobDescription(SoftDeleteModel):
    soft_cascade = ("matches", "drives", "offers")
    TYPES = [("fulltime", "Full-time"), ("internship", "Internship")]
    STATUS = [("open", "Open"), ("closed", "Closed")]
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=120)
    description = models.TextField()
    job_type = models.CharField(max_length=12, choices=TYPES, default="fulltime")
    status = models.CharField(max_length=8, choices=STATUS, default="open")
    location = models.CharField(max_length=80, blank=True)
    openings = models.PositiveSmallIntegerField(default=1)
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=6.0)
    max_backlogs = models.PositiveSmallIntegerField(default=0)
    allowed_branches = models.JSONField(default=list, blank=True) 
    required_skills = models.JSONField(default=list, blank=True)   
    mock_benchmark = models.PositiveSmallIntegerField(default=60)
    ctc_lpa = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta(SoftDeleteModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.company.name} - {self.title}"

class Match(SoftDeleteModel):
    job = models.ForeignKey(JobDescription, on_delete=models.CASCADE, related_name="matches")
    student = models.ForeignKey("students.StudentProfile", on_delete=models.CASCADE,
                                related_name="matches")
    fit_score = models.FloatField()
    level = models.CharField(max_length=20)
    eligible = models.BooleanField(default=True)
    status = models.CharField(max_length=20)  
    explanation = models.JSONField(default=dict, blank=True)

    class Meta(SoftDeleteModel.Meta):
        unique_together = ("job", "student")
        ordering = ["-fit_score"]

    def __str__(self):
        return f"{self.student.roll_no} -> {self.job.title}: {self.fit_score}"