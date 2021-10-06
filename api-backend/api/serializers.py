from rest_framework import serializers
from .models import Blender, Subtask


class SubtaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subtask
        fields = ['relationship', 'provider', 'status', 'task_data']


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Blender
        fields = ['unique_id', 'status', 'task_args', ]
