import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnibrowse import OmniBrowser, print_banner

VIDEO_FILE = os.path.abspath("gta6_police_chase_short.mp4")
TITLE = "GTA 6 CRAZY 5-STAR POLICE CHASE! 🚨😱 #GTA6 #Shorts #Gaming"
DESCRIPTION = """INSANE GTA 6 Police Chase & Rampage in Vice City! 🚗💥

⚡ Autonomous clip extracted, edited into 9:16 vertical Short, and uploaded directly by OmniBrowse AI!
⭐ Star the open-source project on GitHub: https://github.com/aniketkhalko15-blip/omnibrowse
📸 Follow on Instagram: @aniket_aegistraton

#GTA6 #GrandTheftAuto6 #GTA6Gameplay #Shorts #Viral #Gaming"""

async def run_upload():
    print_banner()
    print("=" * 65)
    print("  🚀 OMNIBROWSE AUTO-UPLOADING GTA 6 SHORT TO @Yamiyugen-z3x")
    print(f"  Target File: {VIDEO_FILE}")
    print("=" * 65)

    browser = OmniBrowser(headless=False)
    await browser.start()

    try:
        # Navigate to Studio Dashboard
        url = "https://studio.youtube.com"
        print(f"[*] Navigating to {url}...")
        await browser.page.goto(url, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(4)

        # Click Create button (top right)
        print("[*] Clicking 'Create' button...")
        create_btn = await browser.page.wait_for_selector("#create-icon, button:has-text('Create'), ytcp-button:has-text('Create')", timeout=15000)
        if create_btn:
            await create_btn.click()
            await asyncio.sleep(1.5)

        # Click Upload videos in dropdown
        print("[*] Clicking 'Upload videos'...")
        upload_item = await browser.page.wait_for_selector("tp-yt-paper-item:has-text('Upload videos'), #text-item-0", timeout=10000)
        if upload_item:
            await upload_item.click()
            await asyncio.sleep(3)

        # YouTube Studio creates a hidden <input type="file"> in the DOM
        print("[*] Injecting video file into file chooser...")
        # Query selector for the input file even if not visible
        file_input = await browser.page.wait_for_selector("input[type='file']", state="attached", timeout=15000)
        if file_input:
            await file_input.set_input_files(VIDEO_FILE)
            print("[✓] Video uploaded! Processing upload wizard...")
            await asyncio.sleep(8)

        # Enter Title
        print(f"[*] Setting title: {TITLE}...")
        title_box = await browser.page.wait_for_selector("#textbox[aria-label*='title' i], #title-textarea #textbox", timeout=15000)
        if title_box:
            await title_box.click()
            await browser.page.keyboard.press("Control+A")
            await browser.page.keyboard.press("Backspace")
            await asyncio.sleep(0.5)
            await browser.page.keyboard.type(TITLE, delay=15)
            print("[✓] Title entered!")

        # Enter Description
        print("[*] Setting description with OmniBrowse branding...")
        desc_box = await browser.page.wait_for_selector("#description-textarea #textbox, [aria-label*='description' i]", timeout=10000)
        if desc_box:
            await desc_box.click()
            await browser.page.keyboard.type(DESCRIPTION, delay=5)
            print("[✓] Description entered!")

        # Audience: Not made for kids
        print("[*] Selecting 'Not made for kids'...")
        not_kids = await browser.page.query_selector("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK'], [name='NOT_MFK']")
        if not_kids:
            await not_kids.click()
            print("[✓] Audience set!")

        await asyncio.sleep(2)

        # Step through wizard with Next button
        for i in range(3):
            next_btn = await browser.page.query_selector("#next-button, button:has-text('Next'), ytcp-button:has-text('Next')")
            if next_btn:
                print(f"[*] Clicking Next ({i+1}/3)...")
                await next_btn.click()
                await asyncio.sleep(3)

        # Set Public
        print("[*] Selecting Public visibility...")
        public_radio = await browser.page.query_selector("tp-yt-paper-radio-button[name='PUBLIC'], [name='PUBLIC']")
        if public_radio:
            await public_radio.click()
            await asyncio.sleep(1)

        # Click Publish
        done_btn = await browser.page.query_selector("#done-button, ytcp-button:has-text('Save'), ytcp-button:has-text('Publish')")
        if done_btn:
            print("[*] 🚀 Clicking PUBLISH...")
            await done_btn.click()
            await asyncio.sleep(6)
            print("\n[SUCCESS] 🎉 GTA 6 VIRAL SHORT PUBLISHED TO YOUR CHANNEL!")

        await browser.page.screenshot(path="studio_published_live.png")
        await asyncio.sleep(3)

    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_upload())
