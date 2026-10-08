from django.contrib import admin
from core.admin import SoftDeleteAdmin
from .models import StudentProfile
@admin.register(StudentProfile)
class StudentProfileAdmin(SoftDeleteAdmin):
    list_display = ("roll_no", "branch", "cgpa", "readiness_score", "readiness_level",
                    "placed", "batch", "is_active")
    list_filter = ("is_active", "branch", "readiness_level", "placed", "batch")
    search_fields = ("roll_no", "user__username", "user__first_name")