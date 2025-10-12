# 🚂 Deploy YouTube Converter บน Railway

## ขั้นตอนการ Deploy

### 1. เตรียม Repository
```bash
# สร้าง Git repository
git init
git add .
git commit -m "Initial commit for Railway deployment"

# Push ไป GitHub
git remote add origin https://github.com/[username]/[repo-name].git
git push -u origin main
```

### 2. Deploy บน Railway

1. ไปที่ [railway.app](https://railway.app)
2. เข้าสู่ระบบด้วย GitHub
3. คลิก "New Project"
4. เลือก "Deploy from GitHub repo"
5. เลือก repository ของคุณ
6. Railway จะ auto-detect Dockerfile และ deploy อัตโนมัติ

### 3. เพิ่ม Database (ถ้าต้องการ)
1. ใน Railway dashboard คลิก "New"
2. เลือก "Database" → "PostgreSQL"
3. Railway จะสร้าง DATABASE_URL ให้อัตโนมัติ

### 4. ตั้งค่า Environment Variables
ไม่จำเป็นต้องตั้งเพิ่ม Railway จัดการให้หมดแล้ว!

### 5. Custom Domain (ถ้าต้องการ)
1. ไปที่ Settings → Domains
2. เพิ่ม custom domain หรือใช้ .railway.app ฟรี

## 🎯 ข้อดีของ Railway

✅ **รองรับ yt-dlp เต็มที่**  
✅ **ฟรี $5/เดือน credit**  
✅ **Auto-deploy จาก Git**  
✅ **Built-in PostgreSQL**  
✅ **ไม่มี timeout limit**  
✅ **รองรับ Docker**  

## 🔧 การแก้ไขปัญหา

### ปัญหา: Build failed
```bash
# ตรวจสอบ logs ใน Railway dashboard
# มักเกิดจาก missing dependencies
```

### ปัญหา: Static files ไม่โหลด
```bash
# ตรวจสอบ STATIC_ROOT ใน settings_production.py
# Railway จัดการ static files ให้อัตโนมัติ
```

### ปัญหา: Database connection
```bash
# Railway สร้าง DATABASE_URL ให้อัตโนมัติ
# ไม่ต้องตั้งค่าเพิ่ม
```

## 📱 ทดสอบ

หลัง deploy เสร็จ:
1. เปิด URL ที่ Railway ให้มา
2. ทดสอบใส่ YouTube URL
3. ตรวจสอบการดาวน์โหลด MP3

## 💰 ค่าใช้จ่าย

- **Hobby Plan**: ฟรี $5/เดือน
- **Pro Plan**: $20/เดือน (unlimited usage)

สำหรับทดสอบกับเพื่อน ฟรี $5 น่าจะเพียงพอ!

## 🚀 Next Steps

หลัง deploy สำเร็จแล้ว สามารถ:
- เพิ่ม custom domain
- ตั้งค่า monitoring
- เพิ่มฟีเจอร์ใหม่ๆ
- Scale up เมื่อมีผู้ใช้เยอะ