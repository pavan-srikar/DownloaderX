import os
import subprocess
import time
import platform
import ctypes
from ctypes import wintypes
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, ExtractorError
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from keep_alive import keep_alive
keep_alive()

# Load env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# === file timestamp adjust ===
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

# === download logic with exception handling ===
def download_media(link: str, file_format="mp4", quality=1080, output_dir="downloads"):
    os.makedirs(output_dir, exist_ok=True)

    options = {
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'postprocessors': [],
        'quiet': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': True,
        'retries': 2,
        'fragment_retries': 2,
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
            if not result:
                raise RuntimeError("Invalid link or no video found")
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
                return output_path
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
                return output_path

    except (DownloadError, ExtractorError) as e:
        raise RuntimeError(f"Yo nigga, can’t download this: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Yo nigga, something went wrong: {str(e)}")

# === Telegram bot handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "yo nigga 👋 Send me any link like:\n"
        "/mp4 <link> → get video\n"
        "/mp3 <link> → get audio\n"
        "You can download YouTube, Insta, and X (i mean Twitter) videos\n"
        "➡️ DONT SEND LIKE 1HR LONG VIDEOS YOur DADDY ISNT PAYING SERVER monEY⬅️\n"
        "made by the legend pavan himself 🥀🥀 github>/pavan-srikar"
    )

async def mp4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /mp4 <link>")
        return
    link = context.args[0]
    await update.message.reply_text("⬇️ Downloading your video, hold up nigga…")
    try:
        file_path = download_media(link, file_format="mp4", quality=1080)
        await update.message.reply_document(open(file_path, "rb"))
        os.remove(file_path)  # cleanup
    except RuntimeError as e:
        await update.message.reply_text(str(e))

async def mp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /mp3 <link>")
        return
    link = context.args[0]
    await update.message.reply_text("🎵 Fetching yo bitch ass audio wait a sec…")
    try:
        file_path = download_media(link, file_format="mp3")
        await update.message.reply_audio(open(file_path, "rb"))
        os.remove(file_path)  # cleanup
    except RuntimeError as e:
        await update.message.reply_text(str(e))

def main():
    if not TOKEN:
        raise RuntimeError("No TELEGRAM_TOKEN found in .env")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mp4", mp4))
    app.add_handler(CommandHandler("mp3", mp3))
    app.run_polling()

if __name__ == "__main__":
    main()
