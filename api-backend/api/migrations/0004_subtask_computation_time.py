# Generated by Django 3.2.10 on 2021-12-25 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_blenderresult_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtask',
            name='computation_time',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
