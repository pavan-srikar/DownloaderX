import os
import subprocess
import customtkinter as ctk
from tkinter import filedialog
from yt_dlp import YoutubeDL
import pyperclip
import time
import platform
import ctypes
from ctypes import wintypes

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("DownloaderX by PAVAN 💾🔥 v4.67")
app.geometry("800x450")
app.resizable(False, False)
app.configure(bg="#FFFFFF")

link_var = ctk.StringVar()
output_dir_var = ctk.StringVar(value=os.path.expanduser("~/Documents/Shared Space/DownloaderX"))
format_var = ctk.StringVar(value="mp4")
quality_var = ctk.IntVar(value=1080)

def set_file_timestamp_now(path):
    now = time.time()
    os.utime(path, (now, now))
    if platform.system() == "Windows":
        FILE_WRITE_ATTRIBUTES = 0x100
        FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
        OPEN_EXISTING = 3
        handle = ctypes.windll.kernel32.CreateFileW(
            path, FILE_WRITE_ATTRIBUTES, 0, None, OPEN_EXISTING,
            FILE_FLAG_BACKUP_SEMANTICS, None
        )
        if handle != -1:
            class FILETIME(ctypes.Structure):
                _fields_ = [("dwLowDateTime", wintypes.DWORD), ("dwHighDateTime", wintypes.DWORD)]
            now_windows = int((now + 11644473600) * 10000000)
            ft = FILETIME(now_windows & 0xFFFFFFFF, now_windows >> 32)
            ctypes.windll.kernel32.SetFileTime(handle, ctypes.byref(ft), None, ctypes.byref(ft))
            ctypes.windll.kernel32.CloseHandle(handle)

def get_unique_path(base_path):
    if not os.path.exists(base_path):
        return base_path
    root, ext = os.path.splitext(base_path)
    i = 1
    while True:
        new_path = f"{root}({i}){ext}"
        if not os.path.exists(new_path):
            return new_path
        i += 1

def paste_clipboard_link():
    link_var.set(pyperclip.paste().strip())

def browse_output_dir():
    folder = filedialog.askdirectory()
    if folder:
        output_dir_var.set(folder)

def update_format(val):
    format_var.set("mp4" if val == "MP4" else "mp3")

def update_quality_display(val):
    quality_display.configure(text=f"{int(float(val))}p")
    quality_var.set(int(float(val)))

def download_media():
    download_button.configure(text="Downloading...", state="disabled")
    app.update_idletasks()

    link = link_var.get().strip()
    output_dir = output_dir_var.get().strip()
    file_format = format_var.get()
    quality = str(quality_var.get())

    if not link:
        status_label.configure(text="❌ Error: Please enter a valid link.")
        download_button.configure(text="⬇️ Download", state="normal")
        return

    options = {
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'postprocessors': []
    }

    if file_format == "mp4":
        options['format'] = f'bestvideo[height<={quality}]+bestaudio/best'
        options['merge_output_format'] = 'mp4'
    elif file_format == "mp3":
        options['format'] = 'bestaudio/best'
        options['postprocessors'].extend([
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'}
        ])
        options['writethumbnail'] = True

    try:
        with YoutubeDL(options) as ydl:
            result = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(result)

            if file_format == "mp4":
                input_path = filename
                if not input_path.endswith(".mp4"):
                    input_path = input_path.rsplit('.', 1)[0] + ".mp4"

                base_output_path = os.path.join(output_dir, "converted_" + os.path.basename(input_path))
                output_path = get_unique_path(base_output_path)

                ffmpeg_cmd = [
                    "ffmpeg", "-y",
                    "-i", input_path,
                    "-c:v", "libx264",
                    "-preset", "fast",
                    "-c:a", "aac",
                    "-b:a", "128k",
                    "-movflags", "+faststart",
                    output_path
                ]

                subprocess.run(ffmpeg_cmd, check=True)
                os.remove(input_path)
                set_file_timestamp_now(output_path)
                status_label.configure(text=f"✅ Downloaded & converted:\n{output_path}")
            else:
                output_path = filename.rsplit('.', 1)[0] + ".mp3"
                if not os.path.exists(output_path):
                    for ext in [".mp3", ".webm", ".m4a"]:
                        alt = filename.rsplit('.', 1)[0] + ext
                        if os.path.exists(alt):
                            output_path = alt
                            break
                unique_path = get_unique_path(output_path)
                if output_path != unique_path:
                    os.rename(output_path, unique_path)
                    output_path = unique_path
                set_file_timestamp_now(output_path)
                status_label.configure(text=f"✅ Downloaded:\n{output_path}")
    except Exception as e:
        status_label.configure(text=f"❌ Error: {str(e)}")

    download_button.configure(text="⬇️ Download", state="normal")


# === UI Layout ===
main_frame = ctk.CTkFrame(app, fg_color="#FFFFFF", corner_radius=15)
main_frame.pack(expand=True, fill="both", padx=20, pady=20)

title_label = ctk.CTkLabel(main_frame, text="DownloaderX", text_color="#4CAF50", font=("Ubuntu", 45, "bold"))
title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(5, 30), sticky='w')

row_opts = {'padx': 10, 'pady': 10, 'sticky': 'ew'}

# Link input
link_label = ctk.CTkLabel(main_frame, text="🔗 Link:", font=("Ubuntu", 16))
link_label.grid(row=1, column=0, **row_opts)
link_entry = ctk.CTkEntry(main_frame, textvariable=link_var, font=("Ubuntu", 16), width=400)
link_entry.grid(row=1, column=1, **row_opts)
paste_button = ctk.CTkButton(main_frame, text="📋 Paste", command=paste_clipboard_link, width=120,
                             fg_color="#00509E", hover_color="#003D7A", font=("Ubuntu", 16))
paste_button.grid(row=1, column=2, **row_opts)

# Output dir
out_label = ctk.CTkLabel(main_frame, text="📁 Output Dir:", font=("Ubuntu", 16))
out_label.grid(row=2, column=0, **row_opts)
out_entry = ctk.CTkEntry(main_frame, textvariable=output_dir_var, font=("Ubuntu", 16), width=400)
out_entry.grid(row=2, column=1, **row_opts)
browse_button = ctk.CTkButton(main_frame, text="📂 Browse", command=browse_output_dir, width=120,
                              fg_color="#00509E", hover_color="#003D7A", font=("Ubuntu", 16))
browse_button.grid(row=2, column=2, **row_opts)

# Format toggle
format_label = ctk.CTkLabel(main_frame, text="🎬 Format:", font=("Ubuntu", 16))
format_label.grid(row=3, column=0, sticky='e', padx=(10, 10), pady=10)

format_toggle = ctk.CTkSegmentedButton(main_frame, values=["MP4", "MP3"], command=update_format)
format_toggle.set("MP4")
format_toggle.grid(row=3, column=1, sticky='w', padx=(0, 10), pady=(10, 0))

# Quality slider under toggle
quality_slider = ctk.CTkSlider(main_frame, from_=144, to=1080, number_of_steps=5,
                               command=update_quality_display, variable=quality_var, width=200)
quality_slider.grid(row=4, column=1, sticky='w', padx=(20, 0), pady=(0, 5))

quality_display = ctk.CTkLabel(main_frame, text=f"{quality_var.get()}p", font=("Ubuntu", 14))
quality_display.grid(row=4, column=1, sticky='e', padx=(0, 20))

# Download button
download_button = ctk.CTkButton(main_frame, text="⬇️ Download", command=download_media, width=350, height=60,
                                 fg_color="#4CAF50", hover_color="#45a049", font=("Ubuntu", 18, "bold"))
download_button.grid(row=5, column=0, columnspan=3, pady=20)

# Status
status_label = ctk.CTkLabel(main_frame, text="", text_color="black", wraplength=700, justify="center", font=("Ubuntu", 14))
status_label.grid(row=6, column=0, columnspan=3, pady=5)

main_frame.grid_columnconfigure((0, 1, 2), weight=1)

app.mainloop()
