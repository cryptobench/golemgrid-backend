from rest_framework import serializers
from .models import Blender, Subtask, BlenderResult


class SubtaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subtask
        fields = ['relationship', 'provider',
                  'status', 'task_data', 'provider_id']


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Blender
        fields = ['unique_id', 'status', 'task_args', ]


class ResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlenderResult
        fields = ['file']
