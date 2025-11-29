import os
import shutil
from PyInstaller.__main__ import run as pyinstaller_run

def clean_build():
    for folder in ("build", "dist", "__pycache__"):
        if os.path.exists(folder):
            shutil.rmtree(folder)
    spec_file = "youtube_to_mp3.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)

def create_exe():
    print(" เริ่มสร้างไฟล์ YouTube-to-MP3.exe ...")
    
    clean_build()

    opts = [
        "--onefile",
        "--windowed",
        "--clean",
        "--name=YouTube-to-MP3",
        "--icon=favicon.ico",
        "--add-data=favicon.ico;.",
        "youtube_to_mp3.py",
    ]

    try:
        pyinstaller_run(opts)
        exe_path = os.path.join("dist", "YouTube-to-MP3.exe")

        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"สร้างสำเร็จ! [{exe_path}] ({size_mb:.2f} MB)")
        else:
            print("ไม่พบไฟล์ .exe หลังการ build")
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการสร้าง .exe: {e}")

if __name__ == "__main__":
    if os.path.exists("youtube_to_mp3.py"):
        create_exe()
    else:
        print("ไม่พบไฟล์ youtube_to_mp3.py")
