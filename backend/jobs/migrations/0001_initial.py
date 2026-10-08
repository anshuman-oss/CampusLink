import django.db.models.deletion
import django.db.models.manager
from django.conf import settings
from django.db import migrations, models
class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('students', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('deleted_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('industry', models.CharField(blank=True, max_length=60)),
                ('contact_email', models.EmailField(blank=True, max_length=254)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='company', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'companies',
                'abstract': False,
                'base_manager_name': 'all_objects',
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('all_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='JobDescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('deleted_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=120)),
                ('description', models.TextField()),
                ('job_type', models.CharField(choices=[('fulltime', 'Full-time'), ('internship', 'Internship')], default='fulltime', max_length=12)),
                ('status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed')], default='open', max_length=8)),
                ('location', models.CharField(blank=True, max_length=80)),
                ('openings', models.PositiveSmallIntegerField(default=1)),
                ('min_cgpa', models.DecimalField(decimal_places=2, default=6.0, max_digits=4)),
                ('max_backlogs', models.PositiveSmallIntegerField(default=0)),
                ('allowed_branches', models.JSONField(blank=True, default=list)),
                ('required_skills', models.JSONField(blank=True, default=list)),
                ('mock_benchmark', models.PositiveSmallIntegerField(default=60)),
                ('ctc_lpa', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='jobs.company')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
                'base_manager_name': 'all_objects',
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('all_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('deleted_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('fit_score', models.FloatField()),
                ('level', models.CharField(max_length=20)),
                ('eligible', models.BooleanField(default=True)),
                ('status', models.CharField(max_length=20)),
                ('explanation', models.JSONField(blank=True, default=dict)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='jobs.jobdescription')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matches', to='students.studentprofile')),
            ],
            options={
                'ordering': ['-fit_score'],
                'abstract': False,
                'base_manager_name': 'all_objects',
                'unique_together': {('job', 'student')},
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('all_objects', django.db.models.manager.Manager()),
            ],
        ),
    ]
