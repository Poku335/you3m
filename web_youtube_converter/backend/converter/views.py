from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import ConversionTask
from .serializers import ConversionTaskSerializer, ConversionStatusSerializer
import os
import os

@api_view(['POST'])
def start_conversion(request):
    """เริ่มการแปลง YouTube เป็น MP3"""
    serializer = ConversionTaskSerializer(data=request.data)
    if serializer.is_valid():
        task = serializer.save()
        
        # ตรวจสอบว่าใช้โหมด synchronous หรือไม่
        if getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False):
            # โหมด synchronous - ทำงานทันที
            from .tasks_large_file import convert_youtube_to_mp3_sync
            try:
                convert_youtube_to_mp3_sync(str(task.id), task.youtube_url)
            except Exception as e:
                task.status = 'failed'
                task.error_message = str(e)
                task.save()
        else:
            # โหมด Celery - ใช้ background processing
            from .tasks import convert_youtube_to_mp3
            from celery.result import AsyncResult
            celery_task = convert_youtube_to_mp3.delay(str(task.id), task.youtube_url)
            task.celery_task_id = celery_task.id
            task.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def check_status(request, task_id):
    """ตรวจสอบสถานะการแปลง"""
    try:
        task = ConversionTask.objects.get(id=task_id)
        
        # ตรวจสอบสถานะจาก Celery เฉพาะเมื่อไม่ใช่โหมด synchronous
        if not getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False):
            if hasattr(task, 'celery_task_id') and task.celery_task_id:
                from celery.result import AsyncResult
                celery_result = AsyncResult(task.celery_task_id)
                
                # อัพเดทสถานะจาก Celery
                if celery_result.state == 'PROGRESS':
                    if celery_result.info and 'progress' in celery_result.info:
                        task.progress = celery_result.info['progress']
                        task.save()
                elif celery_result.state == 'SUCCESS':
                    if task.status != 'completed':
                        task.status = 'completed'
                        task.progress = 100
                        task.save()
                elif celery_result.state == 'FAILURE':
                    if task.status != 'failed':
                        task.status = 'failed'
                        task.error_message = str(celery_result.info)
                        task.save()
        
        serializer = ConversionStatusSerializer(task)
        return Response(serializer.data)
    except ConversionTask.DoesNotExist:
        return Response({'error': 'ไม่พบงานที่ระบุ'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def download_file(request, task_id):
    """ดาวน์โหลดไฟล์ MP3"""
    task = get_object_or_404(ConversionTask, id=task_id)
    
    if task.status != 'completed' or not task.file_path:
        return Response({'error': 'ไฟล์ยังไม่พร้อม'}, status=status.HTTP_400_BAD_REQUEST)
    
    if not os.path.exists(task.file_path):
        return Response({'error': 'ไม่พบไฟล์'}, status=status.HTTP_404_NOT_FOUND)
    
    filename = os.path.basename(task.file_path)
    response = FileResponse(
        open(task.file_path, 'rb'),
        as_attachment=True,
        filename=filename
    )
    return response

@api_view(['GET'])
def list_tasks(request):
    """แสดงรายการงานทั้งหมด"""
    tasks = ConversionTask.objects.all().order_by('-created_at')[:20]
    serializer = ConversionStatusSerializer(tasks, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def get_video_info(request):
    """ดึงข้อมูลวิดีโอ (ชื่อ + รูปปก) โดยไม่ดาวน์โหลด"""
    try:
        youtube_url = request.data.get('youtube_url')
        if not youtube_url:
            return Response({'error': 'ไม่พบ URL'}, status=status.HTTP_400_BAD_REQUEST)
        
        import yt_dlp
        
        with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            
            return Response({
                'title': info.get('title', 'ไม่ทราบชื่อ'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'ไม่ทราบผู้อัพโหลด'),
                'view_count': info.get('view_count', 0),
            })
            
    except Exception as e:
        return Response({'error': f'ไม่สามารถดึงข้อมูลวิดีโอได้: {str(e)}'}, 
                       status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def clear_all_tasks(request):
    """ล้างงานทั้งหมดและลบไฟล์"""
    try:
        tasks = ConversionTask.objects.all()
        deleted_files = 0
        
        for task in tasks:
            if task.file_path and os.path.exists(task.file_path):
                try:
                    os.remove(task.file_path)
                    deleted_files += 1
                except:
                    pass
        
        task_count = tasks.count()
        tasks.delete()
        
        download_dir = os.path.join(settings.MEDIA_ROOT, 'downloads')
        if os.path.exists(download_dir):
            for filename in os.listdir(download_dir):
                file_path = os.path.join(download_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        deleted_files += 1
                except:
                    pass
        
        return Response({
            'deleted_tasks': task_count,
            'deleted_files': deleted_files
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)