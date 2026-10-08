import django.db.models.deletion
import django.db.models.manager
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('jobs', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Drive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('deleted_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('venue', models.CharField(max_length=60)),
                ('panel', models.CharField(max_length=60)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('status', models.CharField(choices=[('scheduled', 'Scheduled'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='scheduled', max_length=12)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='drives', to='jobs.jobdescription')),
            ],
            options={
                'ordering': ['date', 'start_time'],
                'abstract': False,
                'base_manager_name': 'all_objects',
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('all_objects', django.db.models.manager.Manager()),
            ],
        ),
    ]
