from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
import uuid

# Create your models here.

TASK_STATUS = (
    ("Not Started", "Not Started"),
    ("Sent", "Sent"),
    ("Computing", "March"),
    ("Error", "Error"),
    ("Finished", "Finished"),
)


def blender_scene_path(instance, filename):
    generate_uuid = uuid.uuid4()
    return '{0}/{1}'.format(str(generate_uuid), filename)


class Blender(models.Model):
    scene_file = models.FileField(upload_to=blender_scene_path)
    task_args = models.JSONField(null=True)
    unique_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=12,
                              choices=TASK_STATUS,
                              default="Not Started")
