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

    browser = OmniBrowser(headless=False)
    await browser.start()

    try:
        url = "https://studio.youtube.com/channel/UCiUaMrbQT8uYeS7XQAG5oJw/editing/profile"
        print(f"[*] Navigating to {url}...")
        
        # Navigate with networkidle wait so heavy client-side SPAs render fully
        await browser.page.goto(url, wait_until="networkidle", timeout=60000)
        await browser.page.wait_for_timeout(4000)

        print(f"[*] Page loaded: {await browser.page.title()}")
        print(f"[*] Current URL: {browser.page.url}")

        # Capture screenshot
        await browser.page.screenshot(path="youtube_studio_customization.png")
        print("[*] Snapshot saved to youtube_studio_customization.png")

        state = await browser.get_state()
        print(f"[*] Total interactive elements found: {state.get('elements_count')}")
        print("\n" + "=" * 50)
        print(state["ai_view"][:1500])
        print("=" * 50)

        # Keep browser open for a few moments to inspect
        await asyncio.sleep(5)

    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(customize_channel())
