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


class Blender(models.Model):
    scene_file = models.FileField(max_length=150)
    resolution = ArrayField(ArrayField(models.CharField(max_length=10)))
    compositing = models.BooleanField()
    crops = ArrayField(models.CharField(max_length=30))
    samples = models.PositiveIntegerField()
    frames = ArrayField(models.CharField(max_length=30))
    output_format = models.CharField(max_length=6)
    resources_dir = models.FilePathField()
    work_dir = models.FilePathField()
    output_dir = models.FilePathField()
    unique_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=12,
                              choices=TASK_STATUS,
                              default="Not Started")
