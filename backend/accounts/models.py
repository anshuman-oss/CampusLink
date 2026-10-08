from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import SoftDeleteModel


class User(AbstractUser):
    ROLES = [("student", "Student"), ("officer", "Placement Officer"),
             ("recruiter", "Recruiter"), ("mentor", "Mentor")]
    role = models.CharField(max_length=12, choices=ROLES, default="student")
    phone = models.CharField(max_length=15, blank=True)
    is_approved = models.BooleanField(default=True)    # recruiters start as False

    def save(self, *args, **kwargs):
        if self.is_superuser:                           # superusers are always officers
            self.role = "officer"
            self.is_approved = True
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):   # soft delete: also blocks login
        self.is_active = False
        self.save(update_fields=["is_active"])
        for rel in ("profile", "company"):
            child = getattr(self, rel, None)
            if child and child.is_active:
                child.delete()

    def restore(self):
        self.is_active = True
        self.save(update_fields=["is_active"])
        for rel in ("profile", "company"):
            child = getattr(self, rel, None)
            if child and not child.is_active:
                child.restore()


class Notification(SoftDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField(max_length=120)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta(SoftDeleteModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.title}"