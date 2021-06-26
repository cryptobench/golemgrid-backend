from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from .models import Blender
import os
from django.http import HttpResponse
import json
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import parser_classes
import requests


@api_view(['POST'])
@parser_classes([MultiPartParser])
def create_blender_task(request):
    if request.method == 'POST':
        scene = request.FILES['scene_file']
        construct_json = {
            "scene_file": "/golem/resource/" + request.FILES['scene_file'].name,
            "resolution1": request.data["resolutionx"],
            "resolution2":  request.data["resolutiony"],
            "use_compositing": request.data["compositing"],
            "crops": [request.data["borderleft"], request.data["borderright"], request.data["borderup"], request.data["borderdown"]],
            "samples": request.data["samples"],
            "frames": request.data["frames"],
            "output_format": request.data["output"],
            "RESOURCES_DIR": "/golem/resources",
            "WORK_DIR": "/golem/work",
            "OUTPUT_DIR": "/golem/output",
        }
        e = Blender.objects.create(task_args=json.dumps(
            construct_json), scene_file=scene)
        url = "http://container-manager-api:8003/v1/start/blender"
        files = {'file': open(
            settings.MEDIA_ROOT + str(e.scene_file), 'rb')}

        r = requests.post(url, files=files, data=construct_json)
