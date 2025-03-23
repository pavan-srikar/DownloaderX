import os
from tkinter import Tk, Label, Entry, Button, StringVar, Radiobutton, filedialog, OptionMenu
from yt_dlp import YoutubeDL

# Default output directory
DEFAULT_OUTPUT_DIR = "/home/pavan/Documents/Shared Space/DownloaderX"

def download_media():
    # Update the button text to "Downloading..."
    download_button.config(text="Downloading...", state="disabled")
    root.update_idletasks()  # Force GUI to update immediately

    link = link_var.get()
    output_dir = output_dir_var.get()
    file_format = format_var.get()
    quality = quality_var.get()

    if not link.strip():
        status_label.config(text="Error: Please enter a valid link.")
        download_button.config(text="Download", state="normal")  # Reset button
        return

    # yt_dlp options
    options = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best' if file_format == "mp4" else 'bestaudio/best',
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
    }
    if file_format == "mp3":
        options['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        with YoutubeDL(options) as ydl:
            ydl.download([link])
        status_label.config(text="Download complete!")
    except Exception as e:
        status_label.config(text=f"Error: {e}")

    # Reset the button text and state after completion
    download_button.config(text="Download", state="normal")

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_dir_var.set(folder)

# Create the GUI
root = Tk()
root.title("Media Downloader")
root.geometry("600x400")
root.resizable(True, True)

# Link input
Label(root, text="Enter Link:", anchor="w").pack(pady=5, padx=10, anchor="w")
link_var = StringVar()
Entry(root, textvariable=link_var, width=60).pack(pady=5, padx=10)

# Format selection
Label(root, text="Select Format:", anchor="w").pack(pady=5, padx=10, anchor="w")
format_var = StringVar(value="mp4")
Radiobutton(root, text="MP4", variable=format_var, value="mp4").pack(anchor="w", padx=20)
Radiobutton(root, text="MP3", variable=format_var, value="mp3").pack(anchor="w", padx=20)

# Quality selection
Label(root, text="Select Quality:", anchor="w").pack(pady=5, padx=10, anchor="w")
quality_var = StringVar(value="1080")
quality_options = ["480", "720", "1080"]
OptionMenu(root, quality_var, *quality_options).pack(anchor="w", padx=20)

# Output directory
Label(root, text="Output Location:", anchor="w").pack(pady=5, padx=10, anchor="w")
output_dir_var = StringVar(value=DEFAULT_OUTPUT_DIR)
Entry(root, textvariable=output_dir_var, width=50).pack(pady=5, padx=10, anchor="w")
Button(root, text="Browse", command=browse_folder).pack(pady=5, padx=10, anchor="w")

# Download button
download_button = Button(root, text="Download", command=download_media, bg="green", fg="white")
download_button.pack(pady=20)

# Status label
status_label = Label(root, text="", fg="blue")
status_label.pack(pady=5)

root.mainloop()
