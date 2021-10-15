# Generated by Django 3.2.8 on 2021-10-15 10:44

import api.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Blender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scene_file', models.FileField(upload_to=api.models.blender_scene_path)),
                ('task_args', models.JSONField(null=True)),
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('status', models.CharField(default='Not Started', max_length=12)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Subtask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(blank=True, max_length=12, null=True)),
                ('provider', models.CharField(blank=True, max_length=42, null=True)),
                ('provider_id', models.CharField(blank=True, max_length=42, null=True)),
                ('task_data', models.IntegerField()),
                ('relationship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.blender')),
            ],
        ),
    ]
