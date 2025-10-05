import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def convert_video(file_path):
    if not os.path.exists('converted'):
        os.makedirs('converted')

    filename = os.path.basename(file_path)
    name, _ = os.path.splitext(filename)
    output_path = os.path.join('converted', f"{name}_c.mp4")

    cmd = [
    'ffmpeg',
    '-i', file_path,
    '-vcodec', 'libx264',
    '-acodec', 'aac',
    '-preset', 'fast',
    '-crf', '28',
    '-vf', "scale='min(640,iw)':'min(480,ih)':force_original_aspect_ratio=decrease,pad=ceil(iw/2)*2:ceil(ih/2)*2",
    '-movflags', '+faststart',
    output_path
]


    try:
        subprocess.run(cmd, check=True)
        messagebox.showinfo("Success", f"Converted video saved to:\n{output_path}")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Failed to convert video.")

def select_file():
    file_path = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=[("Video Files", "*.mp4 *.mkv *.avi *.mov *.flv *.wmv *.webm")]
    )
    if file_path:
        convert_video(file_path)

app = tk.Tk()
app.title("WhatsApp Video Converter")

btn = tk.Button(app, text="Select Video to Convert", command=select_file, padx=10, pady=5)
btn.pack(pady=20)

app.mainloop()
