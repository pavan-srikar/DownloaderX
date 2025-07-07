import tkinter as tk
from tkinter import messagebox, filedialog
import os
import threading
import subprocess

def download_song():
    url = url_entry.get()
    if not url.strip():
        messagebox.showerror("Error", "Please enter a Spotify URL.")
        return

    output_folder = folder_path.get()
    if not output_folder.strip():
        messagebox.showerror("Error", "Please select a folder to save the downloaded song.")
        return

    download_button.config(state=tk.DISABLED)
    status_label.config(text="Downloading...")

    def download_thread():
        try:
            command = ["spotdl", "download", url, "--output", output_folder]
            subprocess.run(command, check=True)
            status_label.config(text="Download Complete!")
        except Exception as e:
            status_label.config(text="Error: " + str(e))
        finally:
            download_button.config(state=tk.NORMAL)

    threading.Thread(target=download_thread).start()

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_path.set(folder)

# Create the main GUI window
root = tk.Tk()
root.title("Spotify Downloader")
root.geometry("500x250")
root.resizable(False, False)

# URL Entry
url_label = tk.Label(root, text="Spotify URL:")
url_label.pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Folder Selection
folder_label = tk.Label(root, text="Save To:")
folder_label.pack(pady=5)

folder_frame = tk.Frame(root)
folder_frame.pack(pady=5)

folder_path = tk.StringVar()
folder_entry = tk.Entry(folder_frame, textvariable=folder_path, width=40)
folder_entry.pack(side=tk.LEFT, padx=5)

browse_button = tk.Button(folder_frame, text="Browse", command=browse_folder)
browse_button.pack(side=tk.LEFT)

# Download Button
download_button = tk.Button(root, text="Download", command=download_song)
download_button.pack(pady=10)

# Status Label
status_label = tk.Label(root, text="", fg="blue")
status_label.pack(pady=10)

# Run the main event loop
root.mainloop()