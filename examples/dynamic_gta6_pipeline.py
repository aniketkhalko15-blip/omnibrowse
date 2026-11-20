"""
Dynamic GTA 6 Clip Search & Uploader
Uses yt-dlp search to find real, active viral GTA 6 / Vice City videos dynamically,
renders vertical shorts, and publishes them autonomously to YouTube Studio.
"""
import asyncio
import os
import sys
import yt_dlp
from moviepy import VideoFileClip, ColorClip, CompositeVideoClip

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from omnibrowse import OmniBrowser, print_banner

SEARCH_QUERIES = [
    {"query": "ytsearch3:GTA 6 official trailer breakdown", "title": "GTA 6 Hidden Secrets Revealed! 👁️🔥 #GTA6 #Shorts #Gaming"},
    {"query": "ytsearch3:GTA 6 leaked graphics ps5", "title": "GTA 6 Graphics on PS5 Are Unreal! 🌴🌊 #GTA6 #Shorts #ViceCity"},
    {"query": "ytsearch3:GTA 6 map analysis leonida", "title": "GTA 6 Leonida Map is Insanely Huge! 🗺️ #GTA6 #Shorts"},
    {"query": "ytsearch3:GTA 6 vice city police chase", "title": "GTA 6 5-Star Wanted Level Chaos! 🚔💥 #GTA6 #Shorts"},
    {"query": "ytsearch3:GTA 6 lucia and jason story", "title": "GTA 6 Lucia & Jason Storyline! 💀🔥 #GTA6 #Shorts"}
]

FFMPEG_DIR = r"C:\Python314"

def render_short(raw_file: str, start: float, duration: float, out_file: str):
    clip = VideoFileClip(raw_file).subclipped(start, min(start + duration, max(1, clip_duration(raw_file) - 1)))
    target_w, target_h = 1080, 1920
    scaled = clip.resized(width=target_w)
    bg = ColorClip(size=(target_w, target_h), color=(10, 10, 15), duration=clip.duration)
    final = CompositeVideoClip([bg, scaled.with_position(("center", "center"))])
    final.write_videofile(out_file, fps=30, codec="libx264", audio_codec="aac", logger=None)
    clip.close()
    final.close()

def clip_duration(file_path):
    try:
        c = VideoFileClip(file_path)
        d = c.duration
        c.close()
        return d
    except Exception:
        return 60

async def upload_single(browser: OmniBrowser, video_path: str, title: str, desc: str):
    print(f"\n[*] Uploading {os.path.basename(video_path)} to YouTube Studio...")
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
        print("[✓] Video selected, filling metadata...")
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
        print(f"[✓] Published successfully: {title}")

async def run():
    print_banner()
    print("=" * 65)
    print("  🚀 DYNAMIC GTA 6 VIRAL PIPELINE (SEARCH & AUTONOMOUS UPLOAD)")
    print("=" * 65)

    browser = OmniBrowser(headless=False)
    await browser.start()

    try:
        for idx, item in enumerate(SEARCH_QUERIES, start=6):
            title = item["title"]
            query = item["query"]
            raw_tmp = f"raw_dynamic_{idx}.mp4"
            out_short = f"gta6_short_dynamic_{idx}.mp4"

            print(f"\n==================================================")
            print(f"  🎬 [{idx}/10] Searching active content: {query}...")
            print(f"==================================================")

            ydl_opts = {
                'format': 'best[height<=720][ext=mp4]/best[ext=mp4]/best',
                'outtmpl': raw_tmp,
                'ffmpeg_location': FFMPEG_DIR,
                'quiet': True,
                'max_downloads': 1
            }

            downloaded = False
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([query])
                downloaded = os.path.exists(raw_tmp)
            except Exception as e:
                print(f"[!] Search/download issue: {e}")

            if not downloaded:
                print("[!] Skipping this query, moving next...")
                continue

            try:
                print(f"[*] Rendering vertical 9:16 Short...")
                dur = clip_duration(raw_tmp)
                start_sec = 15 if dur > 40 else 0
                render_short(raw_tmp, start_sec, 25, out_short)
                print(f"[✓] Created: {out_short}")

                desc = f"{title}\n\nAutomated by OmniBrowse autonomous AI: https://github.com/aniketkhalko15-blip/omnibrowse"
                await upload_single(browser, out_short, title, desc)
                print(f"[SUCCESS] Short #{idx} is officially published!")

            except Exception as e:
                print(f"[!] Error processing clip #{idx}: {e}")

            finally:
                if os.path.exists(raw_tmp):
                    os.remove(raw_tmp)

            print("[*] Sleeping 25s before next upload...")
            await asyncio.sleep(25)

    finally:
        await browser.close()
        print("\n🎉 ALL DYNAMIC GTA 6 SHORTS UPLOADED!")

if __name__ == "__main__":
    asyncio.run(run())
