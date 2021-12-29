from django.db import models
from django.contrib.postgres.fields import ArrayField
import uuid
from django.conf import settings
from pprint import pprint


# Create your models here.


def blender_scene_path(instance, filename):
    generate_uuid = uuid.uuid4()
    return '{0}/{1}'.format(str(generate_uuid), filename)


def blender_output_path(instance, filename):
    obj = Blender.objects.get(id=instance.task_id)
    print(obj)
    return '{0}/{1}'.format(obj.unique_id, filename)


class Blender(models.Model):
    scene_file = models.FileField(upload_to=blender_scene_path)
    task_args = models.JSONField(null=True)
    unique_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=12, default="Not Started")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )


class BlenderResult(models.Model):
    file = models.FileField(upload_to=blender_output_path)
    task = models.ForeignKey(Blender,
                             on_delete=models.CASCADE,
                             )


class Subtask(models.Model):
    relationship = models.ForeignKey(
        Blender, on_delete=models.CASCADE)
    status = models.CharField(null=True, blank=True, max_length=12)
    provider = models.CharField(null=True, blank=True, max_length=42)
    provider_id = models.CharField(null=True, blank=True, max_length=42)
    computation_time = models.CharField(null=True, blank=True, max_length=20)
    task_data = models.IntegerField()
