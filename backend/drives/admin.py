from django.contrib import admin
from core.admin import SoftDeleteAdmin
from .models import Drive
@admin.register(Drive)
class DriveAdmin(SoftDeleteAdmin):
    list_display = ("job", "venue", "panel", "date", "start_time", "end_time", "status", "is_active")