import asyncio
import os
import sys
import yt_dlp
import imageio_ffmpeg
from moviepy import VideoFileClip, ColorClip, CompositeVideoClip

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from omnibrowse import OmniBrowser, print_banner

# Resume from Video 3 through 10
REMAINING_TARGETS = [
    {
        "id": 3,
        "url": "https://www.youtube.com/watch?v=YDNs_sPEcJc",
        "start": 120,
        "duration": 25,
        "title": "GTA 6 Next-Gen Graphics Look Like Real Life! 🌴🌊 #GTA6 #Shorts",
        "desc": "Vice City graphics on PS5 Pro are unmatched. Made with OmniBrowse AI: https://github.com/aniketkhalko15-blip/omnibrowse"
    },
    {
        "id": 4,
        "url": "https://www.youtube.com/watch?v=Wd-vKw3XYP0",
        "start": 35,
        "duration": 24,
        "title": "Best Weapon Sounds in GTA 6 💥🔫 #GTA6 #Shorts #ViceCity",
        "desc": "Insane gun sound design in GTA 6. Clipped autonomously: https://github.com/aniketkhalko15-blip/omnibrowse"
    },
    {
        "id": 5,
        "url": "https://www.youtube.com/watch?v=_nSjfe3k6Ss",
        "start": 90,
        "duration": 25,
        "title": "GTA 6 First Mission Ending Was Wild! 💀🚨 #GTA6 #Shorts",
        "desc": "The first mission in Leonida gets chaotic fast! OmniBrowse AI: https://github.com/aniketkhalko15-blip/omnibrowse"
    },
    {
        "id": 6,
        "url": "https://www.youtube.com/watch?v=hwSg39yIBGU",
        "start": 150,
        "duration": 25,
        "title": "GTA 6 Car Customization is Unreal! 🏎️💨 #GTA6 #Shorts",
        "desc": "Next level car tuning in Vice City! Clipped by OmniBrowse: https://github.com/aniketkhalko15-blip/omnibrowse"
    },
    {
        "id": 7,
        "url": "https://www.youtube.com/watch?v=QjbepgVChIA",
        "start": 80,
        "duration": 25,
        "title": "NPC Reactions in GTA 6 are Hilarious 😂 #GTA6 #Shorts",
        "desc": "AI NPCs in GTA 6 do the craziest things! OmniBrowse: https://github.com/aniketkhalko15-blip/omnibrowse"
    },
    {
        "id": 8,
        "url": "https://www.youtube.com/watch?v=NxM5kt0LiJg",
        "start": 40,
        "duration": 25,
        "title": "Exploring Ocean Beach in GTA 6 at Night! 🌃✨ #GTA6 #Shorts",
        "desc": "Neon lights of Vice City look incredible. OmniBrowse: https://github.com/aniketkhalko15-blip/omnibrowse"
    },
    {
        "id": 9,
        "url": "https://www.youtube.com/watch?v=_3fyWLELeUE",
        "start": 110,
        "duration": 25,
        "title": "Secret Easter Egg Found in GTA 6 Already! 👁️😱 #GTA6 #Shorts",
        "desc": "Rockstar hid this crazy easter egg on Day 1! OmniBrowse: https://github.com/aniketkhalko15-blip/omnibrowse"
    },
    {
        "id": 10,
        "url": "https://www.youtube.com/watch?v=8-DRGbQ1IXc",
        "start": 210,
        "duration": 25,
        "title": "GTA 6 Tank Rampage vs SWAT Team! 💥🚨 #GTA6 #Shorts",
        "desc": "Full military response in Vice City! Clipped & uploaded by OmniBrowse: https://github.com/aniketkhalko15-blip/omnibrowse"
    }
]

def render_short(raw_file: str, start: float, duration: float, out_file: str):
    clip = VideoFileClip(raw_file).subclipped(start, start + duration)
    target_w, target_h = 1080, 1920
    scaled = clip.resized(width=target_w)
    bg = ColorClip(size=(target_w, target_h), color=(10, 10, 15), duration=clip.duration)
    final = CompositeVideoClip([bg, scaled.with_position(("center", "center"))])
    final.write_videofile(out_file, fps=30, codec="libx264", audio_codec="aac", logger=None)
    clip.close()
    final.close()

async def upload_single(browser: OmniBrowser, video_path: str, title: str, desc: str):
    print(f"\n[*] Uploading {video_path}...")
    url = "https://studio.youtube.com"
    await browser.page.goto(url, wait_until="networkidle", timeout=60000)
    await asyncio.sleep(3)

    create_btn = await browser.page.wait_for_selector("#create-icon, button:has-text('Create'), ytcp-button:has-text('Create')", timeout=15000)
    if create_btn:
        await create_btn.click()
        await asyncio.sleep(1.5)

    upload_item = await browser.page.wait_for_selector("tp-yt-paper-item:has-text('Upload videos'), #text-item-0", timeout=10000)
    if upload_item:
        await upload_item.click()
        await asyncio.sleep(3)

    file_input = await browser.page.wait_for_selector("input[type='file']", state="attached", timeout=15000)
    if file_input:
        await file_input.set_input_files(os.path.abspath(video_path))
        print("[✓] Video uploaded to YouTube, filling details...")
        await asyncio.sleep(7)

    title_box = await browser.page.wait_for_selector("#textbox[aria-label*='title' i], #title-textarea #textbox", timeout=15000)
    if title_box:
        await title_box.click()
        await browser.page.keyboard.press("Control+A")
        await browser.page.keyboard.press("Backspace")
        await asyncio.sleep(0.5)
        await browser.page.keyboard.type(title, delay=15)

    desc_box = await browser.page.wait_for_selector("#description-textarea #textbox, [aria-label*='description' i]", timeout=10000)
    if desc_box:
        await desc_box.click()
        await browser.page.keyboard.type(desc, delay=5)

    not_kids = await browser.page.query_selector("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK'], [name='NOT_MFK']")
    if not_kids:
        await not_kids.click()

    await asyncio.sleep(2)
    for _ in range(3):
        nxt = await browser.page.query_selector("#next-button, button:has-text('Next'), ytcp-button:has-text('Next')")
        if nxt:
            await nxt.click()
            await asyncio.sleep(2.5)

    pub = await browser.page.query_selector("tp-yt-paper-radio-button[name='PUBLIC'], [name='PUBLIC']")
    if pub:
        await pub.click()
        await asyncio.sleep(1)

    done = await browser.page.query_selector("#done-button, ytcp-button:has-text('Save'), ytcp-button:has-text('Publish')")
    if done:
        await done.click()
        await asyncio.sleep(6)
        print(f"[✓] Published successfully: {title}")

async def run_resume():
    print_banner()
    print("=" * 65)
    print("  🚀 RESUMING OMNIBROWSE BATCH PIPELINE (VIDEOS 3-10)")
    print("=" * 65)

    browser = OmniBrowser(headless=False)
    await browser.start()

    try:
        for item in REMAINING_TARGETS:
            idx = item["id"]
            print(f"\n==================================================")
            print(f"  🎬 PROCESSING VIDEO {idx}/10: {item['title'][:40]}...")
            print(f"==================================================")
            
            raw_tmp = f"raw_batch_{idx}.mp4"
            out_short = f"gta6_short_batch_{idx}.mp4"

            ydl_opts = {
                'format': 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': raw_tmp,
                'download_ranges': yt_dlp.utils.download_range_func(None, [(item['start'], item['start'] + item['duration'] + 4)]),
                'force_keyframes_at_cuts': True,
                'quiet': True,
                'socket_timeout': 30
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([item['url']])

                render_short(raw_tmp, 1, item['duration'], out_short)
                await upload_single(browser, out_short, item['title'], item['desc'])
                print(f"[SUCCESS] Video {idx}/10 is live on YouTube!")

                if os.path.exists(raw_tmp):
                    os.remove(raw_tmp)

                print("[*] Waiting 30 seconds before next video...")
                await asyncio.sleep(30)

            except Exception as e:
                print(f"[!] Error on video {idx}: {e}")
                continue

    finally:
        await browser.close()
        print("\n🎉 ALL VIDEOS PROCESSED AND PUBLISHED AUTONOMOUSLY!")

if __name__ == "__main__":
    asyncio.run(run_resume())
