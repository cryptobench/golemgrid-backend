from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Blender
import os
import json


@api_view(['POST'])
def create_blender_task(request):
    if request.method == 'POST':
        construct_json = {
            "scene_file": "/golem/resource/" + request.FILES['scene_file'].name,
            "resolution": (request.POST.get("resolution")),
            "use_compositing": request.POST.get("use_compositing"),
            "crops": request.POST.get("crops"),
            "samples": request.POST.get("samples"),
            "frames": request.POST.get("frame"),
            "output_format": request.POST.get("output_format"),
            "RESOURCES_DIR": "/golem/resources",
            "WORK_DIR": "/golem/work",
            "OUTPUT_DIR": "/golem/output",
        }
        Blender.objects.create(task_args=json.dumps(
            construct_json), scene_file=request.FILES['scene_file'])
