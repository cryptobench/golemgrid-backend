from django.db.models.fields.related import RelatedField
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from .models import Blender, Subtask
from .serializers import SubtaskSerializer
import os
from django.http import HttpResponse, JsonResponse
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
        construct_json["scene_file"] = str(e.scene_file),
        construct_json["scene_name"] = str(scene),
        construct_json["task_id"] = str(e.unique_id)
        url = "http://container-manager-api:8003/v1/start/blender"
        files = {'file': open(
            settings.MEDIA_ROOT + str(e.scene_file), 'rb')}

        r = requests.post(url, data=construct_json)
        return HttpResponse('bam')


@api_view(['POST'])
def blender_task_logs(request):
    if request.method == 'POST':
        task_id = request.data['id']
        status = request.data['status']
        db = Blender.objects.get(unique_id=task_id)
        db.status = status
        db.save()
        print("Overall task status: ", db.status)
    return HttpResponse('bam')


@api_view(['POST'])
def blender_subtask_logs(request):
    if request.method == 'POST':
        task_id = request.data['id']
        status = request.data['status']
        task_data = request.data['task_data']
        provider = request.data['provider']
        db = Blender.objects.get(unique_id=task_id)
        subtask = Subtask.objects.create(
            relationship=db, status=status, task_data=task_data, provider=provider)
    return HttpResponse('bam')


@api_view(['GET'])
def display_blender_task(request):
    if request.method == 'GET':
        data = Subtask.objects.all()
        serializer = SubtaskSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False, json_dumps_params={'indent': 4})
    else:
        return HttpResponse(status=400)
