from django.db.models.fields.related import RelatedField
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from .models import Blender, Subtask
from .serializers import SubtaskSerializer, TaskSerializer
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
        response = {'task_id': e.unique_id}
        return JsonResponse(response)


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
        provider_id = request.data['provider_id']
        print(provider, task_data, status)
        db = Blender.objects.get(unique_id=task_id)
        obj, created = Subtask.objects.get_or_create(
            relationship=db, task_data=task_data, provider_id=provider_id)
        obj.status = status
        obj.provider = provider
        obj.save()
    return HttpResponse('bam')


@api_view(['GET'])
def retrieve_subtask_status(request, task_id):
    if request.method == 'GET':
        task = Blender.objects.get(unique_id=task_id)
        data = Subtask.objects.filter(relationship=task)
        serializer = SubtaskSerializer(data, many=True)
        return JsonResponse(serializer.data, safe=False, json_dumps_params={'indent': 4})
    else:
        return HttpResponse(status=400)


@api_view(['GET'])
def retrieve_task_status(request, task_id):
    if request.method == 'GET':
        task = Blender.objects.get(unique_id=task_id)
        serializer = TaskSerializer(task)
        return JsonResponse(serializer.data, safe=False, json_dumps_params={'indent': 4})
    else:
        return HttpResponse(status=400)
