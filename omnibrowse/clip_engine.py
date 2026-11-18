import os
import sys
import subprocess
from moviepy import VideoFileClip, ColorClip, CompositeVideoClip

def clip_and_edit_short(
    input_video: str, 
    start_time: float, 
    duration: float = 30.0, 
    output_short: str = "gta6_viral_short.mp4"
):
    """
    1. Cuts the exact viral timestamp (start_time to start_time + duration).
    2. Converts horizontal 16:9 gameplay into 9:16 vertical Short format.
    3. Adds top/bottom cinematic borders.
    4. Renders the final MP4 ready for YouTube Shorts / Reels.
    """
    print(f"[*] Brain Clipping Video: {input_video} from {start_time}s to {start_time + duration}s...")

    # Load video clip
    clip = VideoFileClip(input_video).subclipped(start_time, start_time + duration)
    w, h = clip.size

    # Convert to 9:16 vertical aspect ratio (1080 x 1920)
    target_w = 1080
    target_h = 1920

    # Resize main gameplay to fit vertical width nicely
    scaled_clip = clip.resized(width=target_w)
    
    # Center the gameplay on a sleek dark canvas
    background = ColorClip(size=(target_w, target_h), color=(15, 15, 20), duration=clip.duration)
    
    # Place gameplay right in the center (y=center)
    final_video = CompositeVideoClip([
        background,
        scaled_clip.with_position(("center", "center"))
    ])

    print(f"[*] Rendering viral Short to {output_short}...")
    final_video.write_videofile(
        output_short,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        logger=None
    )
    print(f"[✓] Short rendered successfully: {output_short}")
    return output_short

if __name__ == "__main__":
    print("[✓] OmniBrowse Video Engine loaded and ready.")
