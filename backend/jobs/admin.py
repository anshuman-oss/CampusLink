from django.contrib import admin
from core.admin import SoftDeleteAdmin
from .models import Company, JobDescription, Match
@admin.register(Company)
class CompanyAdmin(SoftDeleteAdmin):
    list_display = ("name", "industry", "contact_email", "is_active")
@admin.register(JobDescription)
class JobAdmin(SoftDeleteAdmin):
    list_display = ("title", "company", "status", "min_cgpa", "ctc_lpa", "is_active")
    list_filter = ("is_active", "status", "job_type")
@admin.register(Match)
class MatchAdmin(SoftDeleteAdmin):
    list_display = ("student", "job", "fit_score", "level", "status", "is_active")
    list_filter = ("is_active", "status", "level", "job")