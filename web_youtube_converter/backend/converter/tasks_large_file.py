import yt_dlp
import os
from django.conf import settings
from .models import ConversionTask
import shutil
import logging

logger = logging.getLogger(__name__)

def convert_youtube_to_mp3_sync(task_id, youtube_url):
    """Synchronous version สำหรับโหมดไม่ใช้ Celery - ปรับปรุงสำหรับไฟล์ใหญ่"""
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
                        # ดาวน์โหลด = 0-50%
                        download_percent = (d['downloaded_bytes'] / d['total_bytes']) * 50
                        task.progress = int(download_percent)
                        task.save()
                        # แสดง log ทุก 10%
                        if int(download_percent) % 10 == 0:
                            mb_downloaded = d['downloaded_bytes'] / (1024 * 1024)
                            mb_total = d['total_bytes'] / (1024 * 1024)
                            print(f"📥 ดาวน์โหลด: {int(download_percent)}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)")
                    elif '_percent_str' in d:
                        try:
                            percent_str = d['_percent_str'].strip('%')
                            download_percent = float(percent_str) * 0.5  # 0-50%
                            task.progress = int(download_percent)
                            task.save()
                        except:
                            pass
                elif d['status'] == 'finished':
                    task.progress = 50  # ดาวน์โหลดเสร็จ = 50%
                    task.save()
                    print(f"✅ ดาวน์โหลดเสร็จ (50%): {d.get('filename', 'unknown')}")
                elif d['status'] == 'error':
                    print(f"❌ เกิดข้อผิดพลาดในการดาวน์โหลด: {d.get('error', 'unknown error')}")
            except Exception as e:
                logger.error(f"Progress hook error: {e}")
        
        # ตรวจสอบว่ามี ffmpeg หรือไม่
        ffmpeg_available = shutil.which('ffmpeg') is not None
        
        # การตั้งค่าสำหรับไฟล์ใหญ่
        ydl_opts = {
            'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
            'format': 'bestaudio[filesize<150M]/bestaudio/best',  # จำกัดขนาดไฟล์
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writethumbnail': False,
            'progress_hooks': [progress_hook],
            'no_warnings': False,
            'quiet': False,
            'extract_flat': False,
            'ignoreerrors': False,
            # การตั้งค่าสำหรับไฟล์ใหญ่
            'socket_timeout': 120,  # timeout 2 นาที
            'http_chunk_size': 5242880,  # 5MB chunks (เล็กกว่าเดิม)
            'retries': 3,
            'fragment_retries': 3,
            'file_access_retries': 3,
            'skip_unavailable_fragments': True,
            'keep_fragments': False,
            'max_filesize': 200 * 1024 * 1024,  # จำกัด 200MB
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            'noplaylist': True,
        }
        
        # เพิ่ม postprocessor สำหรับแปลงเป็น MP3 ถ้ามี ffmpeg
        if ffmpeg_available:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',  # ลดคุณภาพเป็น 128k สำหรับไฟล์ใหญ่
            }]
            ydl_opts['postprocessor_args'] = [
                '-ar', '44100', '-ac', '2', '-b:a', '128k'
            ]
        
        print(f"Starting download for large file: {youtube_url}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ดึงข้อมูลวิดีโอ
            info = ydl.extract_info(youtube_url, download=False)
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)
            
            # ตรวจสอบความยาววิดีโอ
            if duration > 10800:  # มากกว่า 3 ชั่วโมง
                task.status = 'failed'
                task.error_message = 'วิดีโอยาวเกิน 3 ชั่วโมง กรุณาเลือกวิดีโอที่สั้นกว่า'
                task.save()
                return task_id
            
            task.title = title
            task.progress = 10
            task.save()
            
            print(f"🎬 เริ่มดาวน์โหลด: {title}")
            print(f"⏱️  ความยาว: {duration//60}:{duration%60:02d} นาที")
            print(f"🎵 คุณภาพ: {'MP3 128k (มี FFmpeg)' if ffmpeg_available else 'M4A (ไม่มี FFmpeg)'}")
            
            # ดาวน์โหลดและแปลง
            ydl.download([youtube_url])
            
            # อัพเดทสถานะหลังดาวน์โหลดเสร็จ (50%)
            task.progress = 50
            task.save()
            print("🔄 ดาวน์โหลดเสร็จ (50%) กำลังแปลงไฟล์...")
            
            if ffmpeg_available:
                print("🎛️  FFmpeg กำลังแปลงเป็น MP3... (50-100%)")
                # อัพเดทเป็น 80% ทันที
                task.progress = 80
                task.save()
                print("🔄 กำลังแปลงเสียง... 80%")
            else:
                print("📁 กำลังจัดเตรียมไฟล์ M4A... (50-100%)")
                task.progress = 80
                task.save()
            
            # รอให้ post-processing เสร็จ (FFmpeg) - ลดเวลาลง
            import time
            time.sleep(1)  # รอแค่ 1 วินาที
            
            # หาไฟล์ที่ดาวน์โหลดมา
            found_file = None
            
            if os.path.exists(download_dir):
                files = os.listdir(download_dir)
                print(f"Files in download dir: {files}")
                
                # หาไฟล์เสียงที่ดาวน์โหลดมา
                for filename in files:
                    if filename.endswith(('.mp3', '.m4a', '.webm', '.mp4', '.opus')) and not filename.endswith('.mhtml'):
                        file_path = os.path.join(download_dir, filename)
                        if os.path.exists(file_path):
                            # ตรวจสอบขนาดไฟล์
                            file_size = os.path.getsize(file_path)
                            if file_size > 1024:  # มากกว่า 1KB
                                found_file = file_path
                                break
                
                # ถ้าไม่เจอ ใช้ไฟล์ล่าสุด
                if not found_file:
                    audio_files = [f for f in files if f.endswith(('.mp3', '.m4a', '.webm', '.mp4', '.opus')) and not f.endswith('.mhtml')]
                    if audio_files:
                        audio_files.sort(key=lambda x: os.path.getmtime(os.path.join(download_dir, x)), reverse=True)
                        found_file = os.path.join(download_dir, audio_files[0])
            
            # รอให้ไฟล์ถูกสร้างเสร็จ
            max_wait = 60  # รอสูงสุด 60 วินาที
            wait_count = 0
            
            while wait_count < max_wait:
                if os.path.exists(download_dir):
                    files = os.listdir(download_dir)
                    print(f"Files in directory: {files}")
                    
                    # หาไฟล์ MP3 ที่สร้างเสร็จแล้ว
                    for filename in files:
                        if filename.endswith('.mp3'):
                            file_path = os.path.join(download_dir, filename)
                            try:
                                if os.path.exists(file_path):
                                    # ลองเปิดไฟล์เพื่อตรวจสอบว่าไม่ถูกใช้งานอยู่
                                    with open(file_path, 'rb') as f:
                                        f.read(1)  # อ่าน 1 byte เพื่อทดสอบ
                                    
                                    file_size = os.path.getsize(file_path)
                                    print(f"Found MP3 file: {filename} ({file_size} bytes)")
                                    if file_size > 10240:  # มากกว่า 10KB
                                        found_file = file_path
                                        break
                            except (OSError, IOError) as e:
                                print(f"File {filename} is still being processed: {e}")
                                continue
                    
                    # ถ้าไม่เจอ MP3 ลองหา m4a (แต่ต้องไม่ถูกใช้งานอยู่)
                    if not found_file:
                        for filename in files:
                            if filename.endswith('.m4a') and not filename.endswith('.mhtml'):
                                file_path = os.path.join(download_dir, filename)
                                try:
                                    if os.path.exists(file_path):
                                        # ลองเปิดไฟล์เพื่อตรวจสอบว่าไม่ถูกใช้งานอยู่
                                        with open(file_path, 'rb') as f:
                                            f.read(1)  # อ่าน 1 byte เพื่อทดสอบ
                                        
                                        file_size = os.path.getsize(file_path)
                                        print(f"Found M4A file: {filename} ({file_size} bytes)")
                                        if file_size > 10240:  # มากกว่า 10KB
                                            found_file = file_path
                                            break
                                except (OSError, IOError) as e:
                                    print(f"File {filename} is still being processed: {e}")
                                    continue
                    
                    if found_file:
                        print(f"File found: {found_file}")
                        break
                
                time.sleep(2)  # รอ 2 วินาที
                wait_count += 2
                # แปลงไฟล์ = 90-99%
                conversion_progress = 90 + (wait_count * 9 // max_wait)  # 90-99%
                task.progress = min(conversion_progress, 99)  # ไม่เกิน 99% จนกว่าจะเสร็จจริง
                task.save()
                
                # แสดง log ที่เข้าใจง่าย
                if wait_count <= 10:
                    print(f"⏳ รอไฟล์ MP3... ({wait_count}/{max_wait}s) - {conversion_progress}%")
                elif wait_count <= 30:
                    print(f"🔄 กำลังสร้างไฟล์สุดท้าย... ({wait_count}/{max_wait}s) - {conversion_progress}%")
                else:
                    print(f"⌛ กำลังสร้างไฟล์ขนาดใหญ่... ({wait_count}/{max_wait}s) - {conversion_progress}%")
            
            if found_file and os.path.exists(found_file):
                file_size = os.path.getsize(found_file) / (1024 * 1024)  # MB
                task.file_path = found_file
                task.status = 'completed'
                task.progress = 100  # แปลงไฟล์เสร็จ = 100%
                task.save()
                print(f"🎉 แปลงไฟล์เสร็จสิ้น (100%): {found_file} ({file_size:.1f}MB)")
                print(f"📁 ไฟล์พร้อมดาวน์โหลด!")
            else:
                task.status = 'failed'
                task.error_message = f'ไม่พบไฟล์เสียงที่ดาวน์โหลด ในโฟลเดอร์: {download_dir}'
                task.save()
                print(f"❌ แปลงไฟล์ล้มเหลว. ไฟล์ที่พบ: {files if 'files' in locals() else 'ไม่มี'}")
            
    except Exception as e:
        task.status = 'failed'
        # ปรับข้อความ error ให้เข้าใจง่าย
        if "WinError 32" in str(e):
            task.error_message = 'ไฟล์กำลังถูกประมวลผลอยู่ กรุณารอสักครู่'
        elif "process cannot access the file" in str(e):
            task.error_message = 'ไฟล์กำลังถูกใช้งานอยู่ กรุณาลองใหม่อีกครั้ง'
        else:
            task.error_message = f'เกิดข้อผิดพลาด: {str(e)}'
        task.save()
        print(f"Error in conversion: {e}")
        return task_id  # ไม่ raise error เพื่อไม่ให้ crash
        
    return task_id