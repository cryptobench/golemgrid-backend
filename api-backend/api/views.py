from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Blender
import os
from django.http import HttpResponse
import json
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import parser_classes


@api_view(['POST'])
@parser_classes([MultiPartParser])
def create_blender_task(request):
    if request.method == 'POST':
        scene = request.FILES['scene_file']
        construct_json = {
            "scene_file": "/golem/resource/" + request.FILES['scene_file'].name,
            "resolution": [request.data["resolutionx"], request.data["resolutiony"]],
            "use_compositing": request.data["compositing"],
            "crops": [request.data["borderleft"], request.data["borderright"], request.data["borderup"], request.data["borderdown"]],
            "samples": request.data["samples"],
            "frames": request.data["frames"],
            "output_format": request.data["output"],
            "RESOURCES_DIR": "/golem/resources",
            "WORK_DIR": "/golem/work",
            "OUTPUT_DIR": "/golem/output",
        }
        Blender.objects.create(task_args=json.dumps(
            construct_json), scene_file=scene)
