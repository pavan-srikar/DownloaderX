import os
import subprocess
import customtkinter as ctk
from tkinter import filedialog
from yt_dlp import YoutubeDL
import pyperclip

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Set the entire window background to ash grey
app = ctk.CTk()
app.title("DownloaderX by PAVAN 💾🔥")
app.geometry("800x450")
app.resizable(False, False)
app.configure(bg="#FFFFFF")  # Use white background

link_var = ctk.StringVar()
output_dir_var = ctk.StringVar(value=os.path.expanduser("~/Documents/Shared Space/DownloaderX"))
format_var = ctk.StringVar(value="mp4")
quality_var = ctk.StringVar(value="1080")

def paste_clipboard_link():
    link_var.set(pyperclip.paste().strip())

def browse_output_dir():
    folder = filedialog.askdirectory()
    if folder:
        output_dir_var.set(folder)

def download_media():
    download_button.configure(text="Downloading...", state="disabled")
    app.update_idletasks()

    link = link_var.get().strip()
    output_dir = output_dir_var.get().strip()
    file_format = format_var.get()
    quality = quality_var.get()

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
                status_label.configure(text=f"✅ Downloaded & converted:\n{output_path}")
            else:
                status_label.configure(text="✅ Download complete!")
    except Exception as e:
        status_label.configure(text=f"❌ Error: {str(e)}")

    download_button.configure(text="⬇️ Download", state="normal")

# === UI Layout ===
main_frame = ctk.CTkFrame(app, fg_color="#FFFFFF", corner_radius=15)  # White background

main_frame.pack(expand=True, fill="both", padx=20, pady=20)

# Title
title_label = ctk.CTkLabel(main_frame, text="DownloaderX", text_color="#4CAF50", font=("Ubuntu", 45, "bold"))
title_label.grid(row=0, column=0, columnspan=3,padx=20, pady=(5, 30), sticky='w')

row_opts = {'padx': 10, 'pady': 10, 'sticky': 'ew'}

# Link Row
link_label = ctk.CTkLabel(main_frame, text="🔗 Link:", font=("Ubuntu", 16))
link_label.grid(row=1, column=0, **row_opts)
link_entry = ctk.CTkEntry(main_frame, textvariable=link_var, font=("Ubuntu", 16), width=400)
link_entry.grid(row=1, column=1, **row_opts)
paste_button = ctk.CTkButton(main_frame, text="📋 Paste", command=paste_clipboard_link, width=120,
                             fg_color="#00509E", hover_color="#003D7A", font=("Ubuntu", 16))
paste_button.grid(row=1, column=2, **row_opts)

# Output Dir Row
out_label = ctk.CTkLabel(main_frame, text="📁 Output Dir:", font=("Ubuntu", 16))
out_label.grid(row=2, column=0, **row_opts)
out_entry = ctk.CTkEntry(main_frame, textvariable=output_dir_var, font=("Ubuntu", 16), width=400)
out_entry.grid(row=2, column=1, **row_opts)
browse_button = ctk.CTkButton(main_frame, text="📂 Browse", command=browse_output_dir, width=120,
                              fg_color="#00509E", hover_color="#003D7A", font=("Ubuntu", 16))
browse_button.grid(row=2, column=2, **row_opts)

# Format & Quality Row (With 10px Gap)
format_label = ctk.CTkLabel(main_frame, text="🎬 Format:", font=("Ubuntu", 16))
format_label.grid(row=3, column=0, sticky='e', padx=(10, 10), pady=10)  # Aligned to the right

format_menu = ctk.CTkComboBox(main_frame, values=["mp4", "mp3"], variable=format_var, font=("Ubuntu", 16), width=100)
format_menu.grid(row=3, column=1, sticky='w', padx=(0, 10), pady=10)  # Added 10px gap

quality_label = ctk.CTkLabel(main_frame, text="📶 Quality:", font=("Ubuntu", 16))
quality_label.grid(row=3, column=1, sticky='e', padx=(10, 10), pady=10)  # Added 10px gap

quality_menu = ctk.CTkComboBox(main_frame, values=["144", "240", "360", "480", "720", "1080"], variable=quality_var,
                               font=("Ubuntu", 16), width=100)
quality_menu.grid(row=3, column=2, sticky='w', pady=10)

# Download Button
download_button = ctk.CTkButton(main_frame, text="⬇️ Download", command=download_media, width=350, height=60,
                                 fg_color="#4CAF50", hover_color="#45a049", font=("Ubuntu", 18, "bold"))
download_button.grid(row=4, column=0, columnspan=3, pady=20)

# Status Label
status_label = ctk.CTkLabel(main_frame, text="", text_color="black", wraplength=700, justify="center", font=("Ubuntu", 14))
status_label.grid(row=5, column=0, columnspan=3, pady=5)

# Expand columns to center horizontally
main_frame.grid_columnconfigure((0, 1, 2), weight=1)

app.mainloop()
