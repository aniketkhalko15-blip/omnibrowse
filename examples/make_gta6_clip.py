import yt_dlp
import os
import sys
import imageio_ffmpeg

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnibrowse.clip_engine import clip_and_edit_short

# Exact path to working FFmpeg executable
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
FFMPEG_DIR = os.path.dirname(FFMPEG_EXE)

VIDEO_URL = "https://www.youtube.com/watch?v=8-DRGbQ1IXc"
RAW_FILE = "gta6_raw.mp4"
FINAL_SHORT = "gta6_police_chase_short.mp4"

def download_and_clip():
    print(f"[*] Found bundled FFmpeg: {FFMPEG_EXE}")
    print(f"[*] Downloading GTA 6 viral segment from: {VIDEO_URL}...")
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': RAW_FILE,
        'download_ranges': yt_dlp.utils.download_range_func(None, [(15, 60)]),
        'force_keyframes_at_cuts': True,
        'ffmpeg_location': FFMPEG_EXE,
        'quiet': False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([VIDEO_URL])

    print("\n[*] Raw segment acquired! Feeding into OmniBrowse Clip Engine...")
    
    clip_and_edit_short(
        input_video=RAW_FILE,
        start_time=2,
        duration=28,
        output_short=FINAL_SHORT
    )
    print(f"\n[SUCCESS] 🔥 Viral Short ready to publish: {FINAL_SHORT}")

if __name__ == "__main__":
    download_and_clip()
