# 🚀 Deploy YouTube Converter บน Vercel

## ขั้นตอนการ Deploy

### 1. เตรียม Repository
```bash
# สร้าง Git repository
git init
git add .
git commit -m "Initial commit"

# Push ไป GitHub
git remote add origin https://github.com/[username]/[repo-name].git
git push -u origin main
```

### 2. Deploy บน Vercel

1. ไปที่ [vercel.com](https://vercel.com)
2. เข้าสู่ระบบด้วย GitHub
3. คลิก "New Project"
4. เลือก repository ของคุณ
5. ตั้งค่า:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (ค่าเริ่มต้น)
   - **Build Command**: `npm run build`
   - **Output Directory**: `frontend/build`

### 3. Environment Variables (ถ้าจำเป็น)
ไม่จำเป็นสำหรับ basic setup

### 4. ข้อจำกัดของ Vercel Functions
- **Timeout**: สูงสุด 10 วินาที (Hobby plan)
- **Memory**: 1024 MB
- **File Size**: สูงสุด 50 MB

## 🔧 การแก้ไขปัญหา

### ปัญหา: yt-dlp ไม่ทำงาน
**วิธีแก้**: Vercel ไม่รองรับ binary executables
ต้องใช้ alternative approach:

1. ใช้ YouTube API แทน
2. ใช้ external service
3. Deploy backend บน Railway/Render แทน

### ปัญหา: Function timeout
**วิธีแก้**: 
- ใช้ Vercel Pro ($20/เดือน) สำหรับ timeout 60 วินาที
- หรือแยก backend ไป service อื่น

## 🎯 Alternative: Frontend Only + External API

หากต้องการใช้ Vercel ฟรี แนะนำให้:
1. Deploy แค่ frontend บน Vercel
2. Backend ใช้ Railway/Render (ฟรี)
3. ปรับ API_BASE_URL ใน App.js

```javascript
const API_BASE_URL = 'https://your-backend.railway.app/api';
```

## 📝 หมายเหตุ
- Vercel เหมาะกับ static sites และ serverless functions
- สำหรับ YouTube conversion ที่ใช้เวลานาน แนะนำ Railway หรือ Render