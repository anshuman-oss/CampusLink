from django.conf import settings
from django.db import models
from django.utils import timezone

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):                      
        return super().update(is_active=False, deleted_at=timezone.now())

    def hard_delete(self):                 
        return super().delete()

    def restore(self):
        return super().update(is_active=True, deleted_at=None)

class ActiveManager(models.Manager):       
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_active=True)

class AllManager(models.Manager):        
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db)

class SoftDeleteModel(models.Model):
    is_active = models.BooleanField(default=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ActiveManager()
    all_objects = AllManager()
    soft_cascade = ()       

    class Meta:
        abstract = True
        base_manager_name = "all_objects"  

    def _children(self, rel):
        f = self._meta.get_field(rel)
        return f.related_model.all_objects.filter(**{f.field.name: self})

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_active", "deleted_at", "updated_at"])
        for rel in self.soft_cascade:
            for child in self._children(rel).filter(is_active=True):
                child.delete()

    def restore(self):
        self.is_active = True
        self.deleted_at = None
        self.save(update_fields=["is_active", "deleted_at", "updated_at"])
        for rel in self.soft_cascade:
            for child in self._children(rel).filter(is_active=False):
                child.restore()

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=10)          # DELETE / RESTORE
    model_name = models.CharField(max_length=60)
    object_id = models.CharField(max_length=20)
    object_repr = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-timestamp"]