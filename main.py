import os
import sys
import threading
import winsound
import re
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import yt_dlp
from tkinter import filedialog

from packaging.licenses import EXCEPTIONS

# ---------- App Setup ----------
TITLE = "YT DLP Next"
WIDTH = 960
HEIGHT = 480

root = ctk.CTk()
root.title(TITLE)
root.geometry(f"{WIDTH}x{HEIGHT}")
root.minsize(WIDTH, HEIGHT)
root.grid_columnconfigure(0, weight=1)

try:
    root.iconbitmap("icon.ico")
except Exception as e:
    print("Error: Missing icon.ico, Make sure you downloaded it with this executable.")
    print("")
    print(f"More details: {e}")
    error_msg = CTkMessagebox(master=root, title="Something went wrong", message="Error: Missing icon.ico, Make sure you downloaded it with this executable.\n"
                                       "\n"
                                       f"More details: {e}", icon="cancel")
    winsound.MessageBeep(winsound.MB_ICONHAND)
    if error_msg.get() == "OK":
        sys.exit()

PADX = 15
PADY = 8

# ---------- Main Content Frame ----------
main_frame = ctk.CTkFrame(root, corner_radius=10)
main_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
main_frame.grid_columnconfigure((0, 1), weight=1, uniform="columns")
main_frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

# ---------- URL Entry ----------
url_frame = ctk.CTkFrame(main_frame, corner_radius=8)
url_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=PADX, pady=PADY)
url_frame.grid_columnconfigure(0, weight=1)

url_entry = ctk.CTkEntry(url_frame, placeholder_text="YouTube URL (Video/Playlist/Channel)",
                         height=40, font=("Arial", 12))
url_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

# ---------- Mode & Quality Selection (Horizontal) ----------
mode_quality_frame = ctk.CTkFrame(main_frame, corner_radius=8)
mode_quality_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=PADX, pady=PADY)
mode_quality_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="cols")

# Mode Selection
mode_frame = ctk.CTkFrame(mode_quality_frame, fg_color="transparent")
mode_frame.grid(row=0, column=0, sticky="w", padx=10, pady=5)

ctk.CTkLabel(mode_frame, text="Mode:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")

mode_var = ctk.StringVar(value="video")
video_radio = ctk.CTkRadioButton(mode_frame, text="Video", variable=mode_var, value="video",
                                 command=lambda: update_quality_format())
audio_radio = ctk.CTkRadioButton(mode_frame, text="Audio", variable=mode_var, value="audio",
                                 command=lambda: update_quality_format())
video_radio.grid(row=0, column=1, sticky="w", padx=(10, 5))
audio_radio.grid(row=0, column=2, sticky="w", padx=5)

# Quality Selection
quality_frame = ctk.CTkFrame(mode_quality_frame, fg_color="transparent")
quality_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=5)

ctk.CTkLabel(quality_frame, text="Quality:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")

video_qualities = ["Best", "144p", "240p", "360p", "480p", "720p HD", "1080p FHD", "1440p QHD", "2160p 4K", "4320p 8K"]
audio_qualities = ["Best", "64kbps", "96kbps", "128kbps", "192kbps", "256kbps", "320kbps", "Lossless"]
quality_var = ctk.StringVar(value="Best")
quality_menu = ctk.CTkOptionMenu(quality_frame, variable=quality_var, values=video_qualities, width=120)
quality_menu.grid(row=0, column=1, sticky="w", padx=(10, 0))

# Format Selection
format_frame = ctk.CTkFrame(mode_quality_frame, fg_color="transparent")
format_frame.grid(row=0, column=2, sticky="ew", padx=10, pady=5)

ctk.CTkLabel(format_frame, text="Format:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")

video_formats = ["mp4", "mkv", "webm", "flv", "avi", "mov"]
audio_formats = ["mp3", "wav", "flac", "m4a", "ogg", "opus", "aac"]
format_var = ctk.StringVar(value="mp4")
format_menu = ctk.CTkOptionMenu(format_frame, variable=format_var, values=video_formats, width=80)
format_menu.grid(row=0, column=1, sticky="w", padx=(10, 0))

def update_quality_format():
    if mode_var.get() == "video":
        quality_menu.configure(values=video_qualities)
        format_menu.configure(values=video_formats)
        format_var.set("mp4")
    else:
        quality_menu.configure(values=audio_qualities)
        format_menu.configure(values=audio_formats)
        format_var.set("mp3")
    quality_var.set("Best")

# ---------- Advanced Options (Horizontal) ----------
advanced_frame = ctk.CTkFrame(main_frame, corner_radius=8)
advanced_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=PADX, pady=PADY)
advanced_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="cols")

# Subtitle Options
subs_frame = ctk.CTkFrame(advanced_frame, fg_color="transparent")
subs_frame.grid(row=0, column=0, sticky="w", padx=10, pady=5)

download_subs_var = ctk.BooleanVar(value=False)
subs_checkbox = ctk.CTkCheckBox(subs_frame, text="Subtitles", variable=download_subs_var,
                               command=lambda: toggle_subs_dropdown())
subs_checkbox.grid(row=0, column=0, sticky="w")

subtitle_lang_var = ctk.StringVar(value="en")
subtitle_lang_menu = ctk.CTkOptionMenu(subs_frame, variable=subtitle_lang_var,
                                     values=["en", "es", "fr", "de", "pt", "it", "ru", "ja", "zh", "auto"], width=80)
subtitle_lang_menu.grid(row=0, column=1, sticky="w", padx=(10, 0))
subtitle_lang_menu.configure(state="disabled")

def toggle_subs_dropdown():
    if download_subs_var.get():
        subtitle_lang_menu.configure(state="normal")
    else:
        subtitle_lang_menu.configure(state="disabled")

# Embed Options
embed_frame = ctk.CTkFrame(advanced_frame, fg_color="transparent")
embed_frame.grid(row=0, column=1, sticky="w", padx=10, pady=5)

embed_thumbnail_var = ctk.BooleanVar(value=False)
ctk.CTkCheckBox(embed_frame, text="Thumbnail", variable=embed_thumbnail_var).grid(row=0, column=0, sticky="w", padx=5)

embed_metadata_var = ctk.BooleanVar(value=False)
ctk.CTkCheckBox(embed_frame, text="Metadata", variable=embed_metadata_var).grid(row=0, column=1, sticky="w", padx=5)

# Playlist Options
playlist_frame = ctk.CTkFrame(advanced_frame, fg_color="transparent")
playlist_frame.grid(row=0, column=2, sticky="ew", padx=10, pady=5)

no_playlist_var = ctk.BooleanVar(value=False)
ctk.CTkCheckBox(playlist_frame, text="No Playlist", variable=no_playlist_var).grid(row=0, column=0, sticky="w")

ctk.CTkLabel(playlist_frame, text="Items:").grid(row=0, column=1, sticky="w", padx=(15, 5))
playlist_start_var = ctk.StringVar(value="")
ctk.CTkEntry(playlist_frame, placeholder_text="Start", textvariable=playlist_start_var, width=50).grid(row=0, column=2, sticky="w")

ctk.CTkLabel(playlist_frame, text="to").grid(row=0, column=3, sticky="w", padx=5)
playlist_end_var = ctk.StringVar(value="")
ctk.CTkEntry(playlist_frame, placeholder_text="End", textvariable=playlist_end_var, width=50).grid(row=0, column=4, sticky="w", padx=(0, 10))

# ---------- Output Options (Horizontal) ----------
output_frame = ctk.CTkFrame(main_frame, corner_radius=8)
output_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=PADX, pady=PADY)
output_frame.grid_columnconfigure(1, weight=1)

ctk.CTkLabel(output_frame, text="Output:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=(10, 5))

output_path_var = ctk.StringVar(value=os.path.expanduser("~/Downloads"))
output_path_entry = ctk.CTkEntry(output_frame, textvariable=output_path_var)
output_path_entry.grid(row=0, column=1, sticky="ew", padx=5)

def browse_output():
    path = filedialog.askdirectory(initialdir=output_path_var.get())
    if path:
        output_path_var.set(path)

browse_btn = ctk.CTkButton(output_frame, text="Browse", width=80, command=browse_output)
browse_btn.grid(row=0, column=2, padx=5)

output_template_var = ctk.StringVar(value="%(title)s.%(ext)s")
output_entry = ctk.CTkEntry(output_frame, placeholder_text="Filename Template", textvariable=output_template_var)
output_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

# ---------- Progress / Status ----------
status_frame = ctk.CTkFrame(main_frame, corner_radius=8)
status_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=PADX, pady=PADY)
status_frame.grid_columnconfigure(0, weight=1)

progress = ctk.CTkProgressBar(status_frame, mode="determinate", height=18, progress_color="#1abc9c")
progress.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
progress.set(0)

status_label = ctk.CTkLabel(status_frame, text="Ready", anchor="w", height=20)
status_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 2))

file_label = ctk.CTkLabel(status_frame, text="", anchor="w", height=20, text_color="#3498db")
file_label.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 2))

download_info = ctk.CTkLabel(status_frame, text="", anchor="w", height=20)
download_info.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))

# ---------- Download Functions ----------
def update_status(msg, filename=None, progress_val=None):
    status_label.configure(text=msg)
    if filename:
        short_name = os.path.basename(filename)
        file_label.configure(text=f"File: {short_name}")
    if progress_val is not None:
        progress.set(progress_val)
    if "downloading" in msg.lower():
        download_info.configure(text=msg.split("@")[-1].strip() if "@" in msg else "")
    else:
        download_info.configure(text="")

def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' 
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' 
        r'localhost|' 
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' 
        r'(?::\d+)?' 
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def progress_hook(d, status_callback=None):
    if d['status'] == 'downloading':
        downloaded = d.get('downloaded_bytes', 0)
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        speed = d.get('speed', 0)
        speed_mb = speed / (1024 * 1024)  # MB/s

        if total:
            percent = downloaded / total
            progress_val = percent
            msg = f"Downloading: {percent:.1%} - {downloaded/(1024*1024):.1f}/{total/(1024*1024):.1f} MB"
        else:
            progress_val = 0
            msg = f"Downloading: {downloaded/(1024*1024):.1f} MB"

        if speed:
            msg += f" @ {speed_mb:.1f} MB/s"

        if status_callback:
            status_callback(msg, progress_val=progress_val)

    elif d['status'] == 'finished':
        if status_callback:
            status_callback("Processing...", progress_val=1.0)

def download_video(url, status_callback=None):
    try:
        output_dir = output_path_var.get()
        os.makedirs(output_dir, exist_ok=True)

        ydl_opts = {
            'progress_hooks': [lambda d: progress_hook(d, status_callback)],
            'outtmpl': os.path.join(output_dir, output_template_var.get()),
            'quiet': True,
            'no_warnings': False,
        }

        # Mode & Quality
        mode = mode_var.get()
        quality_value = quality_var.get()

        # Extract resolution from quality string if needed
        resolution = None
        if "p" in quality_value and quality_value != "Best":
            resolution = ''.join(filter(str.isdigit, quality_value))

        if mode == "audio":
            postprocessors = [{'key': 'FFmpegExtractAudio', 'preferredcodec': format_var.get()}]

            if quality_value != "Best":
                postprocessors[0]['preferredquality'] = quality_value.replace("kbps", "")

            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': postprocessors
            })
        else:
            # Video format handling
            if resolution:
                fmt = f"bestvideo[height<={resolution}]+bestaudio/best"
            else:
                fmt = "bestvideo+bestaudio/best"

            ydl_opts.update({
                'format': fmt,
                'merge_output_format': format_var.get()
            })

        # Advanced Options
        if download_subs_var.get():
            ydl_opts['writesubtitles'] = True
            ydl_opts['writeautomaticsub'] = True
            ydl_opts['subtitleslangs'] = [subtitle_lang_var.get()]

        if embed_thumbnail_var.get():
            ydl_opts['embedthumbnail'] = True

        if embed_metadata_var.get():
            ydl_opts['addmetadata'] = True

        if no_playlist_var.get():
            ydl_opts['noplaylist'] = True

        if playlist_start_var.get().strip():
            try:
                ydl_opts['playliststart'] = int(playlist_start_var.get())
            except ValueError:
                pass

        if playlist_end_var.get().strip():
            try:
                ydl_opts['playlistend'] = int(playlist_end_var.get())
            except ValueError:
                pass

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            final_filename = ydl.prepare_filename(info_dict)

            # Handle filename extensions
            if mode == "audio":
                final_filename = os.path.splitext(final_filename)[0] + '.' + format_var.get()

        if status_callback:
            status_callback("Download completed!, Ready for next download!", filename=final_filename)
            progress.set(0)
            download_btn.configure(state="enabled", text="Download")

    except yt_dlp.utils.DownloadError as e:
        if status_callback:
            status_callback(f"Error: {str(e)}")
            download_btn.configure(state="enabled", text="Download")
    except Exception as e:
        if status_callback:
            status_callback(f"Unexpected error: {str(e)}")
            download_btn.configure(state="enabled", text="Download")

def start_download_thread(url):
    thread = threading.Thread(target=download_video, args=(url, update_status), daemon=True)
    thread.start()
    return thread

def download():
    url = url_entry.get().strip()
    if not url:
        update_status("Please enter a URL!")
        return
    if not is_valid_url(url):
        update_status("Invalid URL format!")
        return

    progress.set(0)
    file_label.configure(text="")
    download_info.configure(text="")
    download_btn.configure(state="disabled", text="Downloading...")
    start_download_thread(url)

# ---------- Download Button ----------
download_btn = ctk.CTkButton(root, text="Download", height=45,
                             font=("Arial", 14, "bold"), fg_color="#2980b9", hover_color="#3498db",
                             command=download)
download_btn.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))

# ---------- Run ----------
if __name__ == "__main__":
    root.mainloop()