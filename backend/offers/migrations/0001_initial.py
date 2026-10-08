import django.db.models.deletion
import django.db.models.manager
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('jobs', '0001_initial'),
        ('students', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('deleted_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ctc_lpa', models.DecimalField(decimal_places=2, max_digits=5)),
                ('is_ppo', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('issued', 'Issued'), ('accepted', 'Accepted'), ('deferred', 'Deferred'), ('withdrawn', 'Withdrawn'), ('joined', 'Joined')], default='issued', max_length=12)),
                ('docs_status', models.CharField(choices=[('pending', 'Pending'), ('submitted', 'Submitted'), ('verified', 'Verified')], default='pending', max_length=12)),
                ('bond_signed', models.BooleanField(default=False)),
                ('offer_letter', models.FileField(blank=True, null=True, upload_to='offers/')),
                ('doc_deadline', models.DateField(blank=True, null=True)),
                ('joining_date', models.DateField(blank=True, null=True)),
                ('remarks', models.CharField(blank=True, max_length=200)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='jobs.jobdescription')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='students.studentprofile')),
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
    ]
