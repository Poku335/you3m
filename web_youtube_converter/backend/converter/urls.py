from django.urls import path
from . import views

urlpatterns = [
    path('video-info/', views.get_video_info, name='get_video_info'),
    path('convert/', views.start_conversion, name='start_conversion'),
    path('status/<uuid:task_id>/', views.check_status, name='check_status'),
    path('download/<uuid:task_id>/', views.download_file, name='download_file'),
    path('tasks/', views.list_tasks, name='list_tasks'),
    path('clear/', views.clear_all_tasks, name='clear_all_tasks'),
]