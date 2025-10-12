# YouTube to MP3 Converter

เว็บแอปพลิเคชันสำหรับแปลง YouTube เป็น MP3

## วิธีใช้งาน

### 1. ติดตั้งครั้งแรก
```bash
.\setup.bat
```

### 2. รันระบบ
เปิด 2 หน้าต่าง Command Prompt:

**หน้าต่างที่ 1:**
```bash
.\run_without_celery.bat
```

**หน้าต่างที่ 2:**
```bash
.\run_frontend.bat
```

### 3. เปิดเว็บ
http://localhost:3000

## Features
- ดึงข้อมูลวิดีโอ (ชื่อ, รูปปก)
- แปลง YouTube เป็น MP3
- ดาวน์โหลดไฟล์ผ่านเว็บ
- UI สวยงามด้วย Tailwind CSS

## Requirements
- Python 3.8+
- Node.js 16+
- FFmpeg (สำหรับแปลงเป็น MP3)