import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnibrowse import OmniBrowser, print_banner

async def customize_channel():
    print_banner()
    print("=" * 60)
    print("  🎨 OmniBrowse Autonomous YouTube Customization")
    print("=" * 60)

    # Starts with your saved session profile!
    browser = OmniBrowser(headless=False)
    await browser.start()

    try:
        print("[*] Navigating to YouTube Studio Customization...")
        state = await browser.goto("https://studio.youtube.com/channel/UC/editing/profile")
        
        print(f"[*] Page loaded: {state.get('title')}")
        print(f"[*] Current URL: {browser.page.url}")

        # Check if already logged in or redirected to login
        if "accounts.google.com" in browser.page.url:
            print("\n[!] Not logged in yet! Please run login_profile.py first to save your session.")
            return

        print("\n[*] Taking snapshot of channel customization page...")
        await browser.screenshot("youtube_studio_customization.png")
        print("[*] Snapshot saved to youtube_studio_customization.png")

        print("\n[*] Inspecting channel settings elements...")
        print(state["ai_view"][:600] + "\n...[truncated]...")

        print("\n[✓] OmniBrowse is ready to navigate and apply customization settings!")
        await asyncio.sleep(4)

    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(customize_channel())
