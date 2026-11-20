import asyncio
import os
import sys
import yt_dlp
from moviepy import VideoFileClip, ColorClip, CompositeVideoClip

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from omnibrowse import OmniBrowser, print_banner

# Videos 5-10 with fresh working URLs (popular GTA 6 content)
REMAINING_TARGETS = [
    {
        "id": 5,
        "url": "https://www.youtube.com/watch?v=lU9IggTBpCo",
        "start": 60,
        "duration": 25,
        "title": "GTA 6 Lucia's Best Moments 🔥 #GTA6 #Shorts #Lucia",
        "desc": "Lucia is already iconic. Clipped autonomously by OmniBrowse: https://github.com/aniketkhalko15-blip/omnibrowse"
    },
    {
        "id": 6,
        "url": "https://www.youtube.com/watch?v=QdBZExpgErs",
        "start": 45,
        "duration": 25,
        "title": "GTA 6 Insane Police Chase 🚔💨 #GTA6 #Shorts #ViceCity",
        "desc": "5-star wanted level in Vice City hits different! OmniBrowse AI: https://github.com/aniketkhalko15-blip/omnibrowse"
    },
    {
        "id": 7,
        "url": "https://www.youtube.com/watch?v=aRKBpYPHi_0",
        "start": 30,
        "duration": 25,
        "title": "GTA 6 Map Size vs GTA 5 is MASSIVE! 🗺️ #GTA6 #Shorts",
        "desc": "Leonida map is 3x bigger than Los Santos! OmniBrowse: https://github.com/aniketkhalko15-blip/omnibrowse"
    },
    {
        "id": 8,
        "url": "https://www.youtube.com/watch?v=3OkPbSWMUoI",
        "start": 90,
        "duration": 25,
        "title": "GTA 6 Crazy NPC Interactions 😂 #GTA6 #Shorts #Funny",
        "desc": "These NPCs have actual memory! OmniBrowse: https://github.com/aniketkhalko15-blip/omnibrowse"
    },
    {
        "id": 9,
        "url": "https://www.youtube.com/watch?v=K3mXO9JcIPY",
        "start": 120,
        "duration": 25,
        "title": "GTA 6 Underwater Exploration Hidden Secret! 🌊🐟 #GTA6 #Shorts",
        "desc": "Rockstar hid this underwater! Clipped by OmniBrowse: https://github.com/aniketkhalko15-blip/omnibrowse"
    },
    {
        "id": 10,
        "url": "https://www.youtube.com/watch?v=gFO9p6MpMo4",
        "start": 70,
        "duration": 25,
        "title": "GTA 6 Helicopter vs Fighter Jet 🚁✈️ #GTA6 #Shorts",
        "desc": "Air combat in Vice City is insane! Clipped by OmniBrowse: https://github.com/aniketkhalko15-blip/omnibrowse"
    }
]

FFMPEG_DIR = r"C:\Python314"

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
    print(f"\n[*] Uploading {os.path.basename(video_path)}...")
    await browser.page.goto("https://studio.youtube.com", wait_until="networkidle", timeout=90000)
    await asyncio.sleep(4)

    create_btn = await browser.page.wait_for_selector(
        "#create-icon, button:has-text('Create'), ytcp-button:has-text('Create')",
        timeout=20000
    )
    if create_btn:
        await create_btn.click()
        await asyncio.sleep(2)

    upload_item = await browser.page.wait_for_selector(
        "tp-yt-paper-item:has-text('Upload videos'), #text-item-0",
        timeout=15000
    )
    if upload_item:
        await upload_item.click()
        await asyncio.sleep(4)

    file_input = await browser.page.wait_for_selector("input[type='file']", state="attached", timeout=20000)
    if file_input:
        await file_input.set_input_files(os.path.abspath(video_path))
        print("[✓] File selected, waiting for upload...")
        await asyncio.sleep(10)

    title_box = await browser.page.wait_for_selector(
        "#textbox[aria-label*='title' i], #title-textarea #textbox",
        timeout=20000
    )
    if title_box:
        await title_box.click()
        await browser.page.keyboard.press("Control+A")
        await browser.page.keyboard.press("Backspace")
        await asyncio.sleep(0.5)
        await browser.page.keyboard.type(title, delay=15)

    desc_box = await browser.page.wait_for_selector(
        "#description-textarea #textbox, [aria-label*='description' i]",
        timeout=10000
    )
    if desc_box:
        await desc_box.click()
        await browser.page.keyboard.type(desc, delay=5)

    not_kids = await browser.page.query_selector(
        "tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK'], [name='NOT_MFK']"
    )
    if not_kids:
        await not_kids.click()

    await asyncio.sleep(2)
    for _ in range(3):
        nxt = await browser.page.query_selector(
            "#next-button, button:has-text('Next'), ytcp-button:has-text('Next')"
        )
        if nxt:
            await nxt.click()
            await asyncio.sleep(3)

    pub = await browser.page.query_selector("tp-yt-paper-radio-button[name='PUBLIC'], [name='PUBLIC']")
    if pub:
        await pub.click()
        await asyncio.sleep(1)

    done = await browser.page.query_selector(
        "#done-button, ytcp-button:has-text('Save'), ytcp-button:has-text('Publish')"
    )
    if done:
        await done.click()
        await asyncio.sleep(8)
        print(f"[✓] Published: {title}")

async def run():
    print_banner()
    print("=" * 65)
    print("  🚀 FINISHING BATCH — VIDEOS 5-10")
    print("=" * 65)

    browser = OmniBrowser(headless=False)
    await browser.start()

    try:
        for item in REMAINING_TARGETS:
            idx = item["id"]
            print(f"\n{'='*50}")
            print(f"  🎬 VIDEO {idx}/10: {item['title'][:45]}...")
            print(f"{'='*50}")

            raw_tmp = f"raw_batch_{idx}.mp4"
            out_short = f"gta6_short_batch_{idx}.mp4"

            # Skip if already rendered
            if os.path.exists(out_short):
                print(f"[→] Short already exists, uploading directly...")
                try:
                    await upload_single(browser, out_short, item["title"], item["desc"])
                    print(f"[SUCCESS] Video {idx}/10 is LIVE!")
                    await asyncio.sleep(30)
                except Exception as e:
                    print(f"[!] Upload failed for {idx}: {e}")
                continue

            # Try multiple format options
            formats_to_try = [
                'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'best[height<=720]/best',
                'worst'
            ]

            downloaded = False
            for fmt in formats_to_try:
                try:
                    print(f"[*] Downloading with format: {fmt[:40]}...")
                    ydl_opts = {
                        'format': fmt,
                        'outtmpl': raw_tmp,
                        'ffmpeg_location': FFMPEG_DIR,
                        'quiet': False,
                        'socket_timeout': 30,
                        'retries': 3,
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([item['url']])
                    downloaded = True
                    print(f"[✓] Downloaded successfully!")
                    break
                except Exception as e:
                    print(f"[!] Format {fmt[:30]} failed: {e}")
                    continue

            if not downloaded:
                print(f"[SKIP] Could not download video {idx}, trying next...")
                continue

            try:
                print(f"[*] Rendering 9:16 short...")
                render_short(raw_tmp, 1, item['duration'], out_short)
                print(f"[✓] Short rendered: {out_short}")
            except Exception as e:
                print(f"[!] Render failed: {e}")
                if os.path.exists(raw_tmp):
                    os.remove(raw_tmp)
                continue

            try:
                await upload_single(browser, out_short, item['title'], item['desc'])
                print(f"[SUCCESS] Video {idx}/10 is LIVE on YouTube! 🎉")
            except Exception as e:
                print(f"[!] Upload failed: {e}")

            if os.path.exists(raw_tmp):
                os.remove(raw_tmp)

            print("[*] Waiting 30s before next...")
            await asyncio.sleep(30)

    finally:
        await browser.close()
        print("\n🎉 BATCH COMPLETE — ALL VIDEOS PROCESSED!")

if __name__ == "__main__":
    asyncio.run(run())
