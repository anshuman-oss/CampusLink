import django.db.models.deletion
import django.db.models.manager
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('deleted_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('roll_no', models.CharField(max_length=20, unique=True)),
                ('branch', models.CharField(max_length=10)),
                ('cgpa', models.DecimalField(decimal_places=2, default=0, max_digits=4)),
                ('backlogs', models.PositiveSmallIntegerField(default=0)),
                ('target_role', models.CharField(blank=True, max_length=60)),
                ('aptitude_score', models.PositiveSmallIntegerField(default=0)),
                ('mock_score', models.PositiveSmallIntegerField(default=0)),
                ('soft_score', models.PositiveSmallIntegerField(default=0)),
                ('resume_file', models.FileField(blank=True, null=True, upload_to='resumes/')),
                ('resume_text', models.TextField(blank=True)),
                ('skills', models.JSONField(blank=True, default=list)),
                ('projects', models.JSONField(blank=True, default=list)),
                ('certifications', models.JSONField(blank=True, default=list)),
                ('readiness_score', models.FloatField(default=0)),
                ('readiness_level', models.CharField(default='Not Ready', max_length=20)),
                ('placed', models.BooleanField(default=False)),
                ('batch', models.PositiveSmallIntegerField(default=2026)),
                ('consent_given', models.BooleanField(default=True)),
                ('mentor', models.ForeignKey(blank=True, limit_choices_to={'role': 'mentor'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mentees', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['roll_no'],
                'abstract': False,
                'base_manager_name': 'all_objects',
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('all_objects', django.db.models.manager.Manager()),
            ],
        ),
    ]
