from django.contrib import admin
from core.admin import SoftDeleteAdmin
from .models import Offer
@admin.register(Offer)
class OfferAdmin(SoftDeleteAdmin):
    list_display = ("student", "job", "ctc_lpa", "status", "docs_status", "is_ppo", "is_active")
    list_filter = ("is_active", "status", "docs_status", "is_ppo")