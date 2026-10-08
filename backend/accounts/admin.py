from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.admin import SoftDeleteAdmin, restore_selected, log
from .models import User, Notification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role", "phone", "is_approved")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Role", {"fields": ("role", "phone", "is_approved")}),)
    list_display = ("username", "first_name", "last_name", "role", "is_approved", "is_active")
    list_filter = ("role", "is_approved", "is_active")
    actions = [restore_selected]

    def delete_model(self, request, obj):
        log(request, "DELETE", obj)
        obj.delete()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            log(request, "DELETE", obj)
            obj.delete()


@admin.register(Notification)
class NotificationAdmin(SoftDeleteAdmin):
    list_display = ("user", "title", "is_read", "created_at", "is_active")