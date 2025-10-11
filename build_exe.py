import subprocess
import sys
import os

def create_exe():
    print("กำลังสร้าง YouTube-to-MP3.exe...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "YouTube-to-MP3",
        "youtube_to_mp3.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        
        exe_path = os.path.join("dist", "YouTube-to-MP3.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"✓ สร้าง YouTube-to-MP3.exe สำเร็จ ({file_size:.1f} MB)")
            return True
        else:
            print("✗ ไม่พบไฟล์ .exe ที่สร้าง")
            return False
            
    except subprocess.CalledProcessError:
        print("✗ เกิดข้อผิดพลาดในการสร้าง .exe")
        return False

if __name__ == "__main__":
    if os.path.exists("youtube_to_mp3.py"):
        create_exe()
    else:
        print("✗ ไม่พบไฟล์ youtube_to_mp3.py")