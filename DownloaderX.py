import os
import subprocess
import tkinter as tk
from tkinter import filedialog, ttk
from yt_dlp import YoutubeDL
import pyperclip

# Main window
root = tk.Tk()
root.title("DownloaderX by PAVAN 💾🔥")
root.geometry("650x400")

# Variables
link_var = tk.StringVar()
output_dir_var = tk.StringVar(value=os.path.expanduser("~/Documents/Shared Space/DownloaderX"))
format_var = tk.StringVar(value="mp4")
quality_var = tk.StringVar(value="1080")

# 🔥 Functions
def paste_clipboard_link():
    new_link = pyperclip.paste().strip()
    link_entry.delete(0, tk.END)
    link_entry.insert(0, new_link)

def browse_output_dir():
    folder = filedialog.askdirectory()
    if folder:
        output_dir_var.set(folder)

def download_media():
    download_button.config(text="Downloading...", state="disabled")
    root.update_idletasks()

    link = link_var.get().strip()
    output_dir = output_dir_var.get().strip()
    file_format = format_var.get()
    quality = quality_var.get()

    if not link:
        status_label.config(text="❌ Error: Please enter a valid link.")
        download_button.config(text="Download", state="normal")
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
            info = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info)

        if file_format == "mp4":
            input_path = filename
            if not input_path.endswith(".mp4"):
                input_path = input_path.rsplit('.', 1)[0] + ".mp4"
            output_path = os.path.join(output_dir, "converted_" + os.path.basename(input_path))

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
            os.remove(input_path)  # Cleanup original
            status_label.config(text=f"✅ Downloaded & converted:\n{output_path}")
        else:
            status_label.config(text="✅ Download complete!")

    except Exception as e:
        status_label.config(text=f"❌ Error: {str(e)}")

    download_button.config(text="Download", state="normal")

# 🔧 UI Layout

# Link + Paste
link_frame = tk.Frame(root)
link_frame.pack(pady=10)

tk.Label(link_frame, text="🔗 Link:").pack(side="left", padx=5)

link_entry = tk.Entry(link_frame, textvariable=link_var, width=50)
link_entry.pack(side="left", padx=5)

paste_button = tk.Button(link_frame, text="📋 Paste", command=paste_clipboard_link)
paste_button.pack(side="left", padx=5)

# Output dir
output_frame = tk.Frame(root)
output_frame.pack(pady=5)

tk.Label(output_frame, text="📁 Output Dir:").pack(side="left", padx=5)

output_entry = tk.Entry(output_frame, textvariable=output_dir_var, width=50)
output_entry.pack(side="left", padx=5)

browse_button = tk.Button(output_frame, text="📂 Browse", command=browse_output_dir)
browse_button.pack(side="left")

# Format and quality
options_frame = tk.Frame(root)
options_frame.pack(pady=10)

tk.Label(options_frame, text="🎞️ Format:").pack(side="left", padx=5)
ttk.Combobox(options_frame, textvariable=format_var, values=["mp4", "mp3"], width=6).pack(side="left")

tk.Label(options_frame, text="📶 Quality:").pack(side="left", padx=15)
ttk.Combobox(options_frame, textvariable=quality_var, values=["144", "240", "360", "480", "720", "1080"], width=6).pack(side="left")

# Download button
download_button = tk.Button(root, text="⬇️ Download", command=download_media, height=2, width=20, bg="#4CAF50", fg="white")
download_button.pack(pady=15)

# Status label
status_label = tk.Label(root, text="", wraplength=600, justify="left", fg="blue")
status_label.pack(pady=10)

root.mainloop()
