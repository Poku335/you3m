import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import os
import sys
import threading
from pathlib import Path
import shutil

class YouTubeToMP3Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("แปลง YouTube เป็น MP3")
        self.root.geometry("600x350")
        self.root.resizable(True, True)
        
        self.set_icon()
        self.center_window()
        
        self.download_path = str(Path.home() / "Downloads")
        self.ffmpeg_available = shutil.which('ffmpeg') is not None
        self.cookies_file = None
        
        self.setup_ui()
        
    def set_icon(self):
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(base_path, "favicon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
    def center_window(self):
        self.root.update_idletasks()
        
        window_width = 600
        window_height = 350
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        title_text = "แปลง YouTube เป็น MP3"
        title_label = ttk.Label(main_frame, text=title_text, 
                               font=("Segoe UI", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        ttk.Label(main_frame, text="ลิงก์ YouTube:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50, font=("Segoe UI", 10))
        self.url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(main_frame, text="บันทึกที่:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.path_var = tk.StringVar(value=self.download_path)
        self.path_entry = ttk.Entry(main_frame, textvariable=self.path_var, width=40, font=("Segoe UI", 9))
        self.path_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 5))
        
        self.browse_button = ttk.Button(main_frame, text="เลือกโฟลเดอร์", command=self.browse_folder)
        self.browse_button.grid(row=2, column=2, pady=5)
        
        ttk.Label(main_frame, text="Cookies:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.cookies_var = tk.StringVar(value="ไม่ได้เลือก (ใช้ browser cookies)")
        self.cookies_entry = ttk.Entry(main_frame, textvariable=self.cookies_var, width=40, font=("Segoe UI", 9), state='readonly')
        self.cookies_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 5))
        
        self.cookies_button = ttk.Button(main_frame, text="เลือกไฟล์ Cookies", command=self.browse_cookies)
        self.cookies_button.grid(row=3, column=2, pady=5)
        
        convert_text = "แปลงเป็น MP3" if self.ffmpeg_available else "ดาวน์โหลดเสียง"
        self.convert_button = ttk.Button(main_frame, text=convert_text, 
                                       command=self.start_conversion)
        self.convert_button.grid(row=4, column=0, columnspan=3, pady=20)
        
        self.progress_var = tk.StringVar(value="พร้อมใช้งาน")
        ttk.Label(main_frame, text="สถานะ:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.status_label = ttk.Label(main_frame, textvariable=self.progress_var, font=("Segoe UI", 9))
        self.status_label.grid(row=5, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate', maximum=100)
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        

        
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.path_var.set(folder)
            self.download_path = folder
    
    def browse_cookies(self):
        file = filedialog.askopenfilename(
            title="เลือกไฟล์ Cookies",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=str(Path.home())
        )
        if file:
            if os.path.exists(file):
                self.cookies_file = file
                filename = os.path.basename(file)
                self.cookies_var.set(f"✓ {filename}")
                messagebox.showinfo("สำเร็จ", f"เลือกไฟล์ cookies: {filename}")
            else:
                messagebox.showerror("ข้อผิดพลาด", "ไม่พบไฟล์ที่เลือก")
            
    def start_conversion(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("ข้อผิดพลาด", "กรุณาใส่ลิงก์ YouTube")
            return
            
        if not os.path.exists(self.download_path):
            messagebox.showerror("ข้อผิดพลาด", "ไม่พบโฟลเดอร์ที่เลือก")
            return
            
        self.convert_button.config(state='disabled')
        self.progress_bar['value'] = 0
        self.progress_var.set("เริ่มต้น...")
        
        thread = threading.Thread(target=self.convert_video, args=(url,))
        thread.daemon = True
        thread.start()
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                downloaded = d['downloaded_bytes']
                total = d['total_bytes']
                percent = (downloaded / total) * 100
                downloaded_mb = downloaded / (1024 * 1024)
                total_mb = total / (1024 * 1024)
                speed = d.get('speed', 0)
                speed_mb = speed / (1024 * 1024) if speed else 0
                
                status_text = f"ดาวน์โหลด: {downloaded_mb:.1f}/{total_mb:.1f} MB ({percent:.1f}%) - {speed_mb:.1f} MB/s"
                self.root.after(0, self.update_progress, percent, status_text)
            elif '_percent_str' in d:
                percent_str = d['_percent_str'].strip().strip('%')
                try:
                    percent = float(percent_str)
                    speed = d.get('speed', 0)
                    speed_mb = speed / (1024 * 1024) if speed else 0
                    status_text = f"ดาวน์โหลด: {percent:.1f}% - {speed_mb:.1f} MB/s"
                    self.root.after(0, self.update_progress, percent, status_text)
                except:
                    self.root.after(0, self.update_progress, 50, "กำลังดาวน์โหลด...")
        elif d['status'] == 'finished':
            if self.ffmpeg_available:
                self.root.after(0, self.update_progress, 100, "กำลังแปลงเป็น MP3...")
            else:
                self.root.after(0, self.update_progress, 100, "ดาวน์โหลดเสร็จสิ้น!")
    
    def update_progress(self, value, status):
        self.progress_bar['value'] = value
        self.progress_var.set(status)
        
    def convert_video(self, url):
        try:
            self.root.after(0, self.update_progress, 5, "เตรียมข้อมูล...")
            
            base_opts = {
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'writeinfojson': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'progress_hooks': [self.progress_hook],
                'no_warnings': True,
                'quiet': True,
            }
            
            # ใช้ไฟล์ cookies ถ้าผู้ใช้เลือกไว้
            if self.cookies_file and os.path.exists(self.cookies_file):
                base_opts['cookiefile'] = self.cookies_file
                self.root.after(0, self.update_progress, 8, "ใช้ cookies จากไฟล์...")
            else:
                # พยายามใช้ cookies จาก browser ต่างๆ เพื่อรองรับวิดีโอที่จำกัดอายุ
                # แต่ไม่แสดง error ถ้าเข้าถึงไม่ได้
                for browser in ['brave', 'chrome', 'firefox', 'edge', 'opera']:
                    try:
                        base_opts['cookiesfrombrowser'] = (browser,)
                        break
                    except:
                        # เงียบๆ ถ้าเข้าถึง browser cookies ไม่ได้
                        continue
            
            if self.ffmpeg_available:
                ydl_opts = {
                    **base_opts,
                    'format': 'bestaudio/best',
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
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',
                }
            
            self.root.after(0, self.update_progress, 10, "ดึงข้อมูลวิดีโอ...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'ไม่ทราบชื่อ')
                
                self.root.after(0, self.update_progress, 0, f"เริ่มดาวน์โหลด: {title[:40]}...")
                
                ydl.download([url])
                
            self.root.after(0, self.update_progress, 100, "เสร็จสิ้น!")
            self.root.after(0, self.conversion_complete, True)
            
        except Exception as e:
            error_str = str(e)
            if "Sign in to confirm your age" in error_str or "inappropriate" in error_str or "age" in error_str.lower():
                error_msg = ("ไม่สามารถดาวน์โหลดวิดีโอที่จำกัดอายุได้\n\n"
                           "วิธีแก้ไข:\n"
                           "1. ติดตั้ง Extension 'Get cookies.txt LOCALLY' ใน Chrome/Brave\n"
                           "2. เปิด YouTube และเข้าสู่ระบบ\n"
                           "3. ใช้ Extension ส่งออกไฟล์ cookies.txt\n"
                           "4. กดปุ่ม 'เลือกไฟล์ Cookies' ในโปรแกรมนี้\n"
                           "5. เลือกไฟล์ cookies.txt ที่ส่งออกมา\n"
                           "6. ลองดาวน์โหลดอีกครั้ง")
            elif "cookie" in error_str.lower():
                # ซ่อน error เกี่ยวกับ cookie database
                error_msg = ("ไม่สามารถเข้าถึง browser cookies ได้\n\n"
                           "แนะนำ: ใช้ไฟล์ cookies.txt แทน\n"
                           "1. ติดตั้ง Extension 'Get cookies.txt LOCALLY'\n"
                           "2. ส่งออก cookies จาก YouTube\n"
                           "3. กดปุ่ม 'เลือกไฟล์ Cookies' ในโปรแกรม")
            else:
                error_msg = f"เกิดข้อผิดพลาด: {error_str}"
            self.root.after(0, self.conversion_complete, False, error_msg)
            
    def conversion_complete(self, success, error_msg=None):
        self.convert_button.config(state='normal')
        
        if success:
            self.progress_bar['value'] = 100
            self.progress_var.set("แปลงเสร็จสิ้น! (100%)")
            if self.ffmpeg_available:
                messagebox.showinfo("สำเร็จ", "แปลงเป็น MP3 เสร็จสิ้น!")
            else:
                messagebox.showinfo("สำเร็จ", "ดาวน์โหลดเสร็จสิ้น")
        else:
            self.progress_bar['value'] = 0
            self.progress_var.set("เกิดข้อผิดพลาด!")
            messagebox.showerror("ข้อผิดพลาด", error_msg or "ไม่สามารถแปลงไฟล์ได้")

def main():
    root = tk.Tk()
    app = YouTubeToMP3Converter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
