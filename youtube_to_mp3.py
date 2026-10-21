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
        self.root.title("YouTube Downloader (MP4 / M4A / MP3)")
        self.root.geometry("620x360")
        self.root.resizable(True, True)

        self.set_icon()
        self.center_window()

        self.download_path = str(Path.home() / "Downloads")
        self.ffmpeg_available = shutil.which('ffmpeg') is not None
        
        # Check for aria2c in PATH or Winget directory
        self.aria2c_path = shutil.which('aria2c')
        if not self.aria2c_path:
            winget_path = Path(os.environ.get('LOCALAPPDATA', '')) / 'Microsoft' / 'WinGet' / 'Packages'
            if winget_path.exists():
                for p in winget_path.rglob('aria2c.exe'):
                    self.aria2c_path = str(p)
                    break
        self.aria2c_available = self.aria2c_path is not None

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
        window_width = 620
        window_height = 360
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
        ttk.Label(main_frame, text="YouTube Downloader (MP4 / M4A / MP3)",
                  font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, columnspan=3, pady=(0, 20))

        # URL input
        ttk.Label(main_frame, text="ลิงก์ YouTube:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.url_var, width=50,
                  font=("Segoe UI", 10)).grid(
            row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        # Format selector
        ttk.Label(main_frame, text="รูปแบบ:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar(value="MP4")
        self.format_var.trace_add("write", self.on_format_change)
        
        format_frame = ttk.Frame(main_frame)
        format_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(10, 0))
        
        self.mp4_radio = ttk.Radiobutton(format_frame, text="MP4 (วิดีโอ)", variable=self.format_var, value="MP4")
        self.mp4_radio.pack(side=tk.LEFT, padx=(0, 15))
        
        self.m4a_radio = ttk.Radiobutton(format_frame, text="M4A (เสียงต้นฉบับ)", variable=self.format_var, value="M4A")
        self.m4a_radio.pack(side=tk.LEFT, padx=(0, 15))

        self.mp3_radio = ttk.Radiobutton(format_frame, text="MP3 (เสียง)", variable=self.format_var, value="MP3")
        self.mp3_radio.pack(side=tk.LEFT)

        # Quality selector
        ttk.Label(main_frame, text="คุณภาพ:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.StringVar(value="1080p" if self.ffmpeg_available else "ความชัดสูงสุดที่มีเสียง")
        default_qualities = ["2160p (4K)", "1440p", "1080p", "720p", "480p", "360p", "สูงสุด"] if self.ffmpeg_available else ["ความชัดสูงสุดที่มีเสียง", "720p", "360p"]
        self.quality_combo = ttk.Combobox(main_frame, textvariable=self.quality_var,
                                         values=default_qualities,
                                         state="readonly", width=25)
        self.quality_combo.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # Save path
        ttk.Label(main_frame, text="บันทึกที่:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.path_var = tk.StringVar(value=self.download_path)
        ttk.Entry(main_frame, textvariable=self.path_var, width=40,
                  font=("Segoe UI", 9)).grid(
            row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 5))
        ttk.Button(main_frame, text="เลือกโฟลเดอร์",
                   command=self.browse_folder).grid(row=4, column=2, pady=5)

        # Download button
        self.convert_button = ttk.Button(main_frame, text="ดาวน์โหลด MP4 (วิดีโอ)",
                                         command=self.start_conversion)
        self.convert_button.grid(row=5, column=0, columnspan=3, pady=15)

        # Status
        ttk.Label(main_frame, text="สถานะ:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.progress_var = tk.StringVar(value="พร้อมใช้งาน")
        ttk.Label(main_frame, textvariable=self.progress_var,
                  font=("Segoe UI", 9)).grid(
            row=6, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(10, 0))

        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate', maximum=100)
        self.progress_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

        # System info label
        if self.ffmpeg_available:
            status_text = "🟢 ระบบพร้อมใช้งานเต็มรูปแบบ (ตรวจพบ ffmpeg ในเครื่อง)"
            status_color = "#2e7d32"
        else:
            status_text = "🟢 โหมดสแตนด์อโลน (ดาวน์โหลด M4A และ MP4 ได้ทันทีโดยไม่ต้องมี ffmpeg)"
            status_color = "#1565c0"

        self.status_info_label = ttk.Label(
            main_frame,
            text=status_text,
            foreground=status_color,
            font=("Segoe UI", 8)
        )
        self.status_info_label.grid(row=8, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))

    def on_format_change(self, *args):
        fmt = self.format_var.get()
        if fmt == "MP4":
            if self.ffmpeg_available:
                self.quality_combo.config(values=["2160p (4K)", "1440p", "1080p", "720p", "480p", "360p", "สูงสุด"])
                self.quality_var.set("1080p")
            else:
                self.quality_combo.config(values=["ความชัดสูงสุดที่มีเสียง", "720p", "360p"])
                self.quality_var.set("ความชัดสูงสุดที่มีเสียง")
            self.convert_button.config(text="ดาวน์โหลด MP4 (วิดีโอ)")
        elif fmt == "M4A":
            self.quality_combo.config(values=["คุณภาพเสียงต้นฉบับ (AAC Stereo)"])
            self.quality_var.set("คุณภาพเสียงต้นฉบับ (AAC Stereo)")
            self.convert_button.config(text="ดาวน์โหลด M4A (ไฟล์เสียง)")
        elif fmt == "MP3":
            if not self.ffmpeg_available:
                messagebox.showinfo(
                    "แนะนำ M4A",
                    "เครื่องนี้ไม่มี ffmpeg สำหรับการแปลงเป็น MP3\n\n"
                    "ระบบจะสลับเป็น 'M4A' ให้แทน ซึ่งเป็นไฟล์เสียงต้นฉบับจาก YouTube\n"
                    "เปิดฟังได้ทันทีในคอมฯ และมือถือทุกรุ่นโดยไม่ต้องติดตั้ง ffmpeg ครับ"
                )
                self.format_var.set("M4A")
                return
            self.quality_combo.config(values=["320 kbps (สูงสุด)", "256 kbps", "192 kbps (มาตรฐาน)", "128 kbps"])
            self.quality_var.set("192 kbps (มาตรฐาน)")
            self.convert_button.config(text="ดาวน์โหลด MP3 (ไฟล์เสียง)")

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.path_var.set(folder)
            self.download_path = folder

    def get_format_string(self):
        if self.ffmpeg_available:
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
                return "bestvideo+bestaudio/best"

            height = height_map.get(q, "1080")
            return (
                f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/"
                f"bestvideo[height<={height}]+bestaudio/"
                f"best[height<={height}]"
            )
        else:
            q = self.quality_var.get()
            if "360" in q:
                return "best[height<=360][ext=mp4]/best[height<=360]/best"
            elif "720" in q:
                return "best[height<=720][ext=mp4]/best[height<=720]/best"
            return "best[ext=mp4]/best"

    def start_conversion(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("ข้อผิดพลาด", "กรุณาใส่ลิงก์ YouTube")
            return
        if not os.path.exists(self.download_path):
            messagebox.showerror("ข้อผิดพลาด", "ไม่พบโฟลเดอร์ที่เลือก")
            return
        if self.format_var.get() == "MP3" and not self.ffmpeg_available:
            ans = messagebox.askyesno(
                "ไม่พบ ffmpeg",
                "ไม่พบ ffmpeg ในระบบสำหรับการแปลงเป็น MP3\n\n"
                "คุณต้องการดาวน์โหลดเป็น 'M4A' แทนหรือไม่?\n"
                "(M4A เป็นไฟล์เสียงต้นฉบับ เปิดฟังได้ทันทีโดยไม่ต้องใช้ ffmpeg)"
            )
            if ans:
                self.format_var.set("M4A")
            else:
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
            fmt = self.format_var.get()
            if fmt == "M4A":
                msg = "ดาวน์โหลดไฟล์เสียง M4A เสร็จสิ้น!"
            elif fmt == "MP3":
                msg = "กำลังแปลงไฟล์เป็น MP3..."
            elif fmt == "MP4" and self.ffmpeg_available:
                msg = "กำลังรวมไฟล์วิดีโอ+เสียง..."
            else:
                msg = "ดาวน์โหลดเสร็จสิ้น!"
            self.root.after(0, self.update_progress, 100, msg)

    def update_progress(self, value, status):
        self.progress_bar['value'] = value
        self.progress_var.set(status)

    def download_video(self, url):
        try:
            self.root.after(0, self.update_progress, 5, "เตรียมข้อมูล...")
            
            fmt = self.format_var.get()
            
            # High-performance base options
            ydl_opts = {
                'outtmpl': os.path.join(self.download_path, '%(title).100B.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'no_warnings': True,
                'quiet': True,
                'noplaylist': True,
                'buffersize': 1024 * 64,             # 64 KB buffer for fast network I/O
                'http_chunk_size': 10485760,         # 10 MB chunk size for maximum throughput
                'concurrent_fragment_downloads': 5,  # Safe concurrency
                'retries': 5,
                'socket_timeout': 15,
                'windowsfilenames': True,
                'extractor_args': {'youtube': {'player_client': ['web_creator', 'default']}}
            }

            if fmt == "M4A":
                ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio/best'
            elif fmt == "MP3":
                q_str = self.quality_var.get()
                kbps = "192"
                if "320" in q_str:
                    kbps = "320"
                elif "256" in q_str:
                    kbps = "256"
                elif "128" in q_str:
                    kbps = "128"

                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': kbps,
                }]
            else: # MP4
                ydl_opts['format'] = self.get_format_string()
                if self.ffmpeg_available:
                    ydl_opts['merge_output_format'] = 'mp4'

            self.root.after(0, self.update_progress, 15, "เริ่มเชื่อมต่อและดาวน์โหลดความเร็วสูง...")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)

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
            elif "live event has ended" in error_str.lower():
                error_msg = (
                    "การถ่ายทอดสดนี้เพิ่งสิ้นสุดลง (Live Ended)\n\n"
                    "สาเหตุที่คุณยังเปิดดูบนเบราว์เซอร์ได้:\n"
                    "• เบราว์เซอร์กำลังเล่นจากหน่วยความจำแคชย้อนหลัง (DVR Buffer)\n"
                    "• ขณะนี้ระบบ YouTube กำลังอยู่ในขั้นตอนแปลงไฟล์ไลฟ์เป็นวิดีโอย้อนหลัง (Processing VOD) ทำให้ยังไม่มีไฟล์วิดีโอสมบูรณ์ให้ดาวน์โหลด\n\n"
                    "💡 คำแนะนำ: กรุณารอ YouTube ประมวลผลไฟล์สักครู่ (ประมาณ 15–30 นาที)\n"
                    "เมื่อสตรีมถูกแปลงเป็นคลิปย้อนหลังปกติแล้ว จะสามารถนำลิงก์มาดาวน์โหลดได้ทันทีครับ"
                )
            elif "unavailable" in error_str.lower() or "not available" in error_str.lower():
                error_msg = "วิดีโอนี้ไม่พร้อมใช้งาน หรืออาจถูกลบไปแล้ว"
            else:
                error_msg = f"เกิดข้อผิดพลาด:\n{error_str}"

            self.root.after(0, self.download_complete, False, error_msg)

    def download_complete(self, success, error_msg=None):
        self.convert_button.config(state='normal')
        fmt = self.format_var.get()
        if success:
            self.progress_bar['value'] = 100
            self.progress_var.set(f"ดาวน์โหลด {fmt} เสร็จสิ้น! (100%)")
            messagebox.showinfo("สำเร็จ", f"ดาวน์โหลด {fmt} เสร็จสิ้น!\nบันทึกที่: {self.download_path}")
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