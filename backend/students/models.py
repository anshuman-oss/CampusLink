from django.conf import settings
from django.db import models
from core.models import SoftDeleteModel
class StudentProfile(SoftDeleteModel):
    soft_cascade = ("matches", "offers")
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="profile")
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                               on_delete=models.SET_NULL, related_name="mentees",
                               limit_choices_to={"role": "mentor"})
    roll_no = models.CharField(max_length=20, unique=True)
    branch = models.CharField(max_length=10) 
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    backlogs = models.PositiveSmallIntegerField(default=0)
    target_role = models.CharField(max_length=60, blank=True)
    aptitude_score = models.PositiveSmallIntegerField(default=0) 
    mock_score = models.PositiveSmallIntegerField(default=0)   
    soft_score = models.PositiveSmallIntegerField(default=0)     
    resume_file = models.FileField(upload_to="resumes/", blank=True, null=True)
    resume_text = models.TextField(blank=True)
    skills = models.JSONField(default=list, blank=True)          
    projects = models.JSONField(default=list, blank=True)    
    certifications = models.JSONField(default=list, blank=True)
    readiness_score = models.FloatField(default=0)
    readiness_level = models.CharField(max_length=20, default="Not Ready")
    placed = models.BooleanField(default=False)
    batch = models.PositiveSmallIntegerField(default=2026)
    consent_given = models.BooleanField(default=True)
    
    class Meta(SoftDeleteModel.Meta):
        ordering = ["roll_no"]
    def __str__(self):
        return f"{self.roll_no} - {self.user.get_full_name() or self.user.username}"