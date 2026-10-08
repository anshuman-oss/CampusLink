from django.contrib import admin, messages
from .models import AuditLog
def log(request, action, obj):
    AuditLog.objects.create(user=request.user, action=action, model_name=obj._meta.label,
                            object_id=str(obj.pk), object_repr=str(obj)[:200])
@admin.action(description="Restore selected records")
def restore_selected(modeladmin, request, queryset):
    for obj in queryset:
        obj.restore()
        log(request, "RESTORE", obj)
    modeladmin.message_user(request, f"{queryset.count()} record(s) restored.", messages.SUCCESS)
class SoftDeleteAdmin(admin.ModelAdmin):
    list_filter = ("is_active",)
    actions = [restore_selected]

    def get_queryset(self, request):      
        qs = self.model.all_objects.all()
        ordering = self.get_ordering(request)
        return qs.order_by(*ordering) if ordering else qs

    def delete_model(self, request, obj):
        log(request, "DELETE", obj)
        obj.delete()
        
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            log(request, "DELETE", obj)
            obj.delete()
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "action", "model_name", "object_repr")
    list_filter = ("action", "model_name")
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False