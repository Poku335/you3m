import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import os
import sys
import threading
from pathlib import Path
import shutil
 
 
class YouTubeToMP4Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("แปลง YouTube เป็น MP4")
        self.root.geometry("600x320")
        self.root.resizable(True, True)
 
        self.set_icon()
        self.center_window()
 
        self.download_path = str(Path.home() / "Downloads")
        self.ffmpeg_available = shutil.which('ffmpeg') is not None
 
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
        window_height = 320
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
 
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
 
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
 
        # Title
        ttk.Label(main_frame, text="แปลง YouTube เป็น MP4",
                  font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, columnspan=3, pady=(0, 20))
 
        # URL input
        ttk.Label(main_frame, text="ลิงก์ YouTube:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.url_var, width=50,
                  font=("Segoe UI", 10)).grid(
            row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
 
        # Quality selector
        ttk.Label(main_frame, text="คุณภาพ:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.StringVar(value="1080p")
        quality_combo = ttk.Combobox(main_frame, textvariable=self.quality_var,
                                     values=["2160p (4K)", "1440p", "1080p", "720p", "480p", "360p", "สูงสุด"],
                                     state="readonly", width=15)
        quality_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
 
        # Save path
        ttk.Label(main_frame, text="บันทึกที่:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.path_var = tk.StringVar(value=self.download_path)
        ttk.Entry(main_frame, textvariable=self.path_var, width=40,
                  font=("Segoe UI", 9)).grid(
            row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 5))
        ttk.Button(main_frame, text="เลือกโฟลเดอร์",
                   command=self.browse_folder).grid(row=3, column=2, pady=5)
 
        # Download button
        self.convert_button = ttk.Button(main_frame, text="ดาวน์โหลด MP4",
                                         command=self.start_conversion)
        self.convert_button.grid(row=4, column=0, columnspan=3, pady=20)
 
        # Status
        ttk.Label(main_frame, text="สถานะ:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.progress_var = tk.StringVar(value="พร้อมใช้งาน")
        ttk.Label(main_frame, textvariable=self.progress_var,
                  font=("Segoe UI", 9)).grid(
            row=5, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(10, 0))
 
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate', maximum=100)
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
 
        # ffmpeg warning
        if not self.ffmpeg_available:
            ttk.Label(
                main_frame,
                text="⚠ ไม่พบ ffmpeg — อาจได้ไฟล์ .webm แทน MP4 หรือคุณภาพต่ำลง",
                foreground="orange",
                font=("Segoe UI", 8)
            ).grid(row=7, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
 
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.path_var.set(folder)
            self.download_path = folder
 
    def get_format_string(self):
        q = self.quality_var.get()
        height_map = {
            "2160p (4K)": "2160",
            "1440p": "1440",
            "1080p": "1080",
            "720p": "720",
            "480p": "480",
            "360p": "360",
        }
        if q == "สูงสุด":
            if self.ffmpeg_available:
                return "bestvideo+bestaudio/best"
            else:
                return "best[ext=mp4]/best"
 
        height = height_map.get(q, "1080")
        if self.ffmpeg_available:
            return (
                f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/"
                f"bestvideo[height<={height}]+bestaudio/"
                f"best[height<={height}]"
            )
        else:
            return f"best[height<={height}][ext=mp4]/best[height<={height}]/best"
 
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
 
        thread = threading.Thread(target=self.download_video, args=(url,))
        thread.daemon = True
        thread.start()
 
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if d.get('total_bytes'):
                downloaded = d['downloaded_bytes']
                total = d['total_bytes']
                percent = (downloaded / total) * 100
                dl_mb = downloaded / (1024 * 1024)
                tot_mb = total / (1024 * 1024)
                spd_mb = (d.get('speed') or 0) / (1024 * 1024)
                text = f"ดาวน์โหลด: {dl_mb:.1f}/{tot_mb:.1f} MB ({percent:.1f}%) — {spd_mb:.1f} MB/s"
                self.root.after(0, self.update_progress, percent, text)
            elif d.get('_percent_str'):
                try:
                    percent = float(d['_percent_str'].strip().strip('%'))
                    spd_mb = (d.get('speed') or 0) / (1024 * 1024)
                    text = f"ดาวน์โหลด: {percent:.1f}% — {spd_mb:.1f} MB/s"
                    self.root.after(0, self.update_progress, percent, text)
                except:
                    self.root.after(0, self.update_progress, 50, "กำลังดาวน์โหลด...")
        elif d['status'] == 'finished':
            msg = "กำลังรวมไฟล์วิดีโอ+เสียง..." if self.ffmpeg_available else "ดาวน์โหลดเสร็จสิ้น!"
            self.root.after(0, self.update_progress, 100, msg)
 
    def update_progress(self, value, status):
        self.progress_bar['value'] = value
        self.progress_var.set(status)
 
    def download_video(self, url):
        try:
            self.root.after(0, self.update_progress, 5, "เตรียมข้อมูล...")
 
            ydl_opts = {
                'format': self.get_format_string(),
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4',
                'progress_hooks': [self.progress_hook],
                'no_warnings': True,
                'quiet': True,
                'noplaylist': True,
            }
 
            self.root.after(0, self.update_progress, 10, "ดึงข้อมูลวิดีโอ...")
 
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'ไม่ทราบชื่อ')
                self.root.after(0, self.update_progress, 0,
                                f"เริ่มดาวน์โหลด: {title[:40]}...")
                ydl.download([url])
 
            self.root.after(0, self.update_progress, 100, "เสร็จสิ้น!")
            self.root.after(0, self.download_complete, True)
 
        except Exception as e:
            error_str = str(e)
            if any(k in error_str.lower() for k in ("sign in", "age", "inappropriate", "private")):
                error_msg = (
                    "ไม่สามารถดาวน์โหลดวิดีโอนี้ได้\n\n"
                    "วิดีโออาจ:\n"
                    "• จำกัดอายุ (Age-restricted)\n"
                    "• เป็น Private\n"
                    "• ถูกลบหรือไม่พร้อมใช้งานในภูมิภาคนี้\n\n"
                    "กรุณาลองลิงก์อื่น"
                )
            elif "unavailable" in error_str.lower() or "not available" in error_str.lower():
                error_msg = "วิดีโอนี้ไม่พร้อมใช้งาน หรืออาจถูกลบไปแล้ว"
            else:
                error_msg = f"เกิดข้อผิดพลาด:\n{error_str}"
 
            self.root.after(0, self.download_complete, False, error_msg)
 
    def download_complete(self, success, error_msg=None):
        self.convert_button.config(state='normal')
        if success:
            self.progress_bar['value'] = 100
            self.progress_var.set("ดาวน์โหลด MP4 เสร็จสิ้น! (100%)")
            messagebox.showinfo("สำเร็จ", f"ดาวน์โหลด MP4 เสร็จสิ้น!\nบันทึกที่: {self.download_path}")
        else:
            self.progress_bar['value'] = 0
            self.progress_var.set("เกิดข้อผิดพลาด!")
            messagebox.showerror("ข้อผิดพลาด", error_msg or "ไม่สามารถดาวน์โหลดได้")
 
 
def main():
    root = tk.Tk()
    YouTubeToMP4Converter(root)
    root.mainloop()
 
 
if __name__ == "__main__":
    main()