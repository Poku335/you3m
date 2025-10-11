import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import os
import threading
from pathlib import Path
import shutil

class YouTubeToMP3Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("แปลง YouTube เป็น MP3")
        self.root.geometry("600x300")
        self.root.resizable(True, True)
        
        self.set_icon()
        self.center_window()
        
        self.download_path = str(Path.home() / "Downloads")
        self.ffmpeg_available = shutil.which('ffmpeg') is not None
        
        self.setup_ui()
        
    def set_icon(self):
        try:
            if os.path.exists("my_app_icon.ico"):
                self.root.iconbitmap("my_app_icon.ico")
                return
        except:
            pass
        
        try:
            icon_path = os.path.abspath("my_app_icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
                return
        except:
            pass
        
        try:
            if os.path.exists("my_app_icon.ico"):
                self.root.iconbitmap("my_app_icon.ico")
                return
        except:
            pass
        
    def center_window(self):
        self.root.update_idletasks()
        
        window_width = 600
        window_height = 300
        
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
        
        convert_text = "แปลงเป็น MP3" if self.ffmpeg_available else "ดาวน์โหลดเสียง"
        self.convert_button = ttk.Button(main_frame, text=convert_text, 
                                       command=self.start_conversion)
        self.convert_button.grid(row=3, column=0, columnspan=3, pady=20)
        
        self.progress_var = tk.StringVar(value="พร้อมใช้งาน")
        ttk.Label(main_frame, text="สถานะ:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.status_label = ttk.Label(main_frame, textvariable=self.progress_var, font=("Segoe UI", 9))
        self.status_label.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate', maximum=100)
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        

        
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.path_var.set(folder)
            self.download_path = folder
            
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
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 60
                self.root.after(0, self.update_progress, percent, f"ดาวน์โหลด... {percent:.1f}%")
            elif '_percent_str' in d:
                percent_str = d['_percent_str'].strip('%')
                try:
                    percent = float(percent_str) * 0.6
                    self.root.after(0, self.update_progress, percent, f"ดาวน์โหลด... {percent:.1f}%")
                except:
                    self.root.after(0, self.update_progress, 30, "กำลังดาวน์โหลด...")
        elif d['status'] == 'finished':
            if self.ffmpeg_available:
                self.root.after(0, self.update_progress, 60, "เริ่มแปลงไฟล์...")
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
                
                self.root.after(0, self.update_progress, 15, f"{title[:30]}...")
                
                ydl.download([url])
                
                if self.ffmpeg_available:
                    for i in range(65, 95, 10):
                        self.root.after(0, self.update_progress, i, f"แปลงเป็น MP3... {i}%")
                        import time
                        time.sleep(0.1)
                
            self.root.after(0, self.update_progress, 100, "เสร็จสิ้น!")
            self.root.after(0, self.conversion_complete, True)
            
        except Exception as e:
            error_msg = f"เกิดข้อผิดพลาด: {str(e)}"
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
