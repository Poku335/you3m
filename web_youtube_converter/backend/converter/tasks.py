from celery import shared_task
import yt_dlp
import os
from django.conf import settings
from .models import ConversionTask
import shutil
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def convert_youtube_to_mp3(self, task_id, youtube_url):
    try:
        task = ConversionTask.objects.get(id=task_id)
        task.status = 'processing'
        task.progress = 0
        task.save()
        
        # สร้างโฟลเดอร์สำหรับเก็บไฟล์
        download_dir = os.path.join(settings.MEDIA_ROOT, 'downloads')
        os.makedirs(download_dir, exist_ok=True)
        
        def progress_hook(d):
            try:
                if d['status'] == 'downloading':
                    if 'total_bytes' in d and d['total_bytes']:
                        percent = int((d['downloaded_bytes'] / d['total_bytes']) * 60)
                        task.progress = percent
                        task.save()
                        # อัพเดท Celery task progress
                        self.update_state(state='PROGRESS', meta={'progress': percent})
                    elif '_percent_str' in d:
                        try:
                            percent_str = d['_percent_str'].strip('%')
                            percent = int(float(percent_str) * 0.6)
                            task.progress = percent
                            task.save()
                            self.update_state(state='PROGRESS', meta={'progress': percent})
                        except:
                            pass
                elif d['status'] == 'finished':
                    task.progress = 80
                    task.save()
                    self.update_state(state='PROGRESS', meta={'progress': 80})
            except Exception as e:
                logger.error(f"Progress hook error: {e}")
        
        # ตรวจสอบว่ามี ffmpeg หรือไม่
        ffmpeg_available = shutil.which('ffmpeg') is not None
        
        base_opts = {
            'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'progress_hooks': [progress_hook],
            'no_warnings': True,
            'quiet': True,
            # แก้ไขปัญหา HTTP 416
            'http_chunk_size': 10485760,  # 10MB chunks
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'keep_fragments': False,
            # เพิ่ม headers เพื่อหลีกเลี่ยงการบล็อก
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }
        
        if ffmpeg_available:
            ydl_opts = {
                **base_opts,
                'format': 'bestaudio[ext=m4a]/bestaudio/best[height<=720]',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'postprocessor_args': [
                    '-ar', '44100', '-ac', '2', '-b:a', '192k'
                ],
            }
        else:
            ydl_opts = {
                **base_opts,
                'format': 'bestaudio[ext=m4a]/bestaudio/best[height<=720]',
            }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ดึงข้อมูลวิดีโอ
            info = ydl.extract_info(youtube_url, download=False)
            title = info.get('title', 'Unknown')
            
            task.title = title
            task.progress = 10
            task.save()
            
            # ดาวน์โหลดและแปลง
            ydl.download([youtube_url])
            
            # หาไฟล์ที่ดาวน์โหลดมา
            if ffmpeg_available:
                file_extension = 'mp3'
            else:
                file_extension = 'm4a'
            
            expected_filename = f"{title}.{file_extension}"
            file_path = os.path.join(download_dir, expected_filename)
            
            # ตรวจสอบไฟล์ที่สร้างขึ้น
            if os.path.exists(file_path):
                task.file_path = file_path
                task.status = 'completed'
                task.progress = 100
            else:
                # หาไฟล์ที่มีชื่อคล้ายกัน
                for filename in os.listdir(download_dir):
                    if title in filename and filename.endswith(('.mp3', '.m4a', '.webm', '.mp4')):
                        task.file_path = os.path.join(download_dir, filename)
                        task.status = 'completed'
                        task.progress = 100
                        break
                else:
                    task.status = 'failed'
                    task.error_message = 'ไม่พบไฟล์ที่ดาวน์โหลด'
            
            task.save()
            
    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        task.save()
        
    return task_id

def convert_youtube_to_mp3_sync(task_id, youtube_url):
    """Synchronous version สำหรับโหมดไม่ใช้ Celery"""
    try:
        task = ConversionTask.objects.get(id=task_id)
        task.status = 'processing'
        task.progress = 0
        task.save()
        
        # สร้างโฟลเดอร์สำหรับเก็บไฟล์
        download_dir = os.path.join(settings.MEDIA_ROOT, 'downloads')
        os.makedirs(download_dir, exist_ok=True)
        
        def progress_hook(d):
            try:
                if d['status'] == 'downloading':
                    if 'total_bytes' in d and d['total_bytes']:
                        percent = int((d['downloaded_bytes'] / d['total_bytes']) * 60)
                        task.progress = percent
                        task.save()
                    elif '_percent_str' in d:
                        try:
                            percent_str = d['_percent_str'].strip('%')
                            percent = int(float(percent_str) * 0.6)
                            task.progress = percent
                            task.save()
                        except:
                            pass
                elif d['status'] == 'finished':
                    task.progress = 80
                    task.save()
            except Exception as e:
                logger.error(f"Progress hook error: {e}")
        
        # ตรวจสอบว่ามี ffmpeg หรือไม่
        ffmpeg_available = shutil.which('ffmpeg') is not None
        
        base_opts = {
            'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'progress_hooks': [progress_hook],
            'no_warnings': True,
            'quiet': True,
            # แก้ไขปัญหา HTTP 416
            'http_chunk_size': 10485760,  # 10MB chunks
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'keep_fragments': False,
            # เพิ่ม headers เพื่อหลีกเลี่ยงการบล็อก
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }
        
        if ffmpeg_available:
            ydl_opts = {
                **base_opts,
                'format': 'bestaudio[ext=m4a]/bestaudio/best[height<=720]',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'postprocessor_args': [
                    '-ar', '44100', '-ac', '2', '-b:a', '192k'
                ],
            }
        else:
            ydl_opts = {
                **base_opts,
                'format': 'bestaudio[ext=m4a]/bestaudio/best[height<=720]',
            }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ดึงข้อมูลวิดีโอ
            info = ydl.extract_info(youtube_url, download=False)
            title = info.get('title', 'Unknown')
            
            task.title = title
            task.progress = 10
            task.save()
            
            # ดาวน์โหลดและแปลง
            ydl.download([youtube_url])
            
            # หาไฟล์ที่ดาวน์โหลดมา
            if ffmpeg_available:
                file_extension = 'mp3'
            else:
                file_extension = 'm4a'
            
            expected_filename = f"{title}.{file_extension}"
            file_path = os.path.join(download_dir, expected_filename)
            
            # ตรวจสอบไฟล์ที่สร้างขึ้น - ปรับปรุงการค้นหา
            found_file = None
            
            # ลองหาไฟล์ตามชื่อที่คาดหวัง
            if os.path.exists(file_path):
                found_file = file_path
            else:
                # หาไฟล์ในโฟลเดอร์ download
                if os.path.exists(download_dir):
                    files = os.listdir(download_dir)
                    logger.info(f"Files in download dir: {files}")
                    
                    # หาไฟล์ที่มีชื่อคล้ายกัน
                    for filename in files:
                        # ข้าม .mhtml และไฟล์ที่ไม่ใช่เสียง
                        if filename.endswith(('.mp3', '.m4a', '.webm', '.mp4', '.opus')) and not filename.endswith('.mhtml'):
                            # ตรวจสอบว่าชื่อไฟล์มีส่วนของ title หรือไม่
                            clean_title = title.replace('/', '_').replace('\\', '_').replace(':', '_').replace('?', '_').replace('*', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_').replace('｜', '_')
                            clean_filename = filename.replace('/', '_').replace('\\', '_').replace('｜', '_').replace('|', '_')
                            
                            if any(word in clean_filename.lower() for word in clean_title.lower().split() if len(word) > 2):
                                found_file = os.path.join(download_dir, filename)
                                break
                    
                    # ถ้ายังไม่เจอ ใช้ไฟล์ล่าสุด
                    if not found_file and files:
                        audio_files = [f for f in files if f.endswith(('.mp3', '.m4a', '.webm', '.mp4', '.opus'))]
                        if audio_files:
                            # เรียงตามเวลาแก้ไขล่าสุด
                            audio_files.sort(key=lambda x: os.path.getmtime(os.path.join(download_dir, x)), reverse=True)
                            found_file = os.path.join(download_dir, audio_files[0])
            
            if found_file and os.path.exists(found_file):
                task.file_path = found_file
                task.status = 'completed'
                task.progress = 100
                logger.info(f"Successfully found file: {found_file}")
            else:
                task.status = 'failed'
                task.error_message = f'ไม่พบไฟล์ที่ดาวน์โหลด ในโฟลเดอร์: {download_dir}'
                logger.error(f"File not found. Expected: {file_path}, Download dir: {download_dir}")
                if os.path.exists(download_dir):
                    logger.error(f"Files in dir: {os.listdir(download_dir)}")
            
            task.save()
            
    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        task.save()
        logger.error(f"Error in sync conversion: {e}")
        raise e
        
    return task_id