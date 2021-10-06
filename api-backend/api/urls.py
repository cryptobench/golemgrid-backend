from django.urls import path
from django.shortcuts import render
from . import views

app_name = 'api'

urlpatterns = [
    path('submit/blender', views.create_blender_task),
    path('status/task/blender', views.blender_task_logs),
    path('status/subtask/blender', views.blender_subtask_logs),
    path('subtask/<task_id>', views.retrieve_subtask_status),
    path('task/<task_id>', views.retrieve_task_status),
]
