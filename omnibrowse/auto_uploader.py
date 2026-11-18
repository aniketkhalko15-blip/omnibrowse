import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnibrowse import OmniBrowser, print_banner

async def upload_short(video_path: str, title: str, description: str):
    """
    Automates YouTube Studio to upload a newly rendered Short!
    Uses your saved profile session (no passwords needed).
    """
    print_banner()
    print(f"[*] OmniBrowse Auto-Uploader: Uploading {video_path}...")

    abs_video_path = os.path.abspath(video_path)
    if not os.path.exists(abs_video_path):
        print(f"[!] Video file not found: {abs_video_path}")
        return

    browser = OmniBrowser(headless=False)
    await browser.start()

    try:
        url = "https://studio.youtube.com"
        print(f"[*] Opening YouTube Studio...")
        await browser.goto(url)
        await asyncio.sleep(4)

        # Click 'Create' button in Studio header
        create_btn = await browser.page.wait_for_selector("#create-icon, button:has-text('Create')", timeout=10000)
        if create_btn:
            await create_btn.click()
            await asyncio.sleep(1)

        # Click 'Upload videos'
        upload_option = await browser.page.wait_for_selector("tp-yt-paper-item:has-text('Upload videos'), #text-item-0", timeout=5000)
        if upload_option:
            await upload_option.click()
            await asyncio.sleep(2)

        # Set input file on hidden file chooser input
        print(f"[*] Attaching video file: {abs_video_path}")
        file_input = await browser.page.wait_for_selector("input[type='file']", timeout=10000)
        if file_input:
            await file_input.set_input_files(abs_video_path)
            print("[*] File uploaded to YouTube processing pipeline!")
            await asyncio.sleep(5)

        # Enter Title & Description
        title_box = await browser.page.wait_for_selector("#textbox[aria-label*='title' i], #title-textarea textarea", timeout=10000)
        if title_box:
            await title_box.click()
            await browser.page.keyboard.press("Control+A")
            await browser.page.keyboard.press("Backspace")
            await title_box.type(title, delay=15)
            print(f"[*] Entered title: {title}")

        print("[✓] OmniBrowse Auto-Upload stage complete!")
        await browser.page.screenshot(path="studio_upload_status.png")

    finally:
        await browser.close()

if __name__ == "__main__":
    print("[✓] Auto Uploader module ready.")
