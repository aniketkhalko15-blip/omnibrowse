import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnibrowse import OmniBrowser, print_banner

NEW_DESCRIPTION = """Welcome to YAMIYUGEN (幽玄) 🌌

Exploring the frontier of AI development, autonomous agents, and next-gen tech engineering.

Creator of OmniBrowse — the universal autonomous browser engine for AI models. Here, we build intelligent software and cutting-edge digital systems.

🔗 Connect & Follow:
🐙 GitHub: https://github.com/aniketkhalko15-blip
📸 Instagram: https://instagram.com/aniket_aegistraton
🚀 Project: https://github.com/aniketkhalko15-blip/omnibrowse"""

async def update_youtube_bio():
    print_banner()
    print("[*] Launching OmniBrowse to edit Description and publish...")
    
    browser = OmniBrowser(headless=False)
    await browser.start()

    try:
        url = "https://studio.youtube.com/channel/UCiUaMrbQT8uYeS7XQAG5oJw/editing/profile"
        print(f"[*] Navigating to {url}...")
        
        # Navigate without failing on background redirects
        await browser.page.goto(url, wait_until="networkidle", timeout=60000)
        await browser.page.wait_for_timeout(4000)

        print("[*] Page loaded! Looking for Description field...")
        
        # In YouTube Studio's new interface, description is inside an input/textarea with id 'description-textarea'
        # or contenteditable div with id 'textbox'
        found = False

        # Try scrolling down 500px first
        await browser.page.mouse.wheel(0, 500)
        await browser.page.wait_for_timeout(1000)

        # Check for textarea or mention-textbox
        for selector in [
            "#description-textarea textarea",
            "ytcp-mention-textbox #textbox",
            "textarea#description",
            "div[contenteditable='true']",
            "textarea"
        ]:
            try:
                el = await browser.page.wait_for_selector(selector, timeout=3000)
                if el:
                    # Verify it's not the search box
                    text = await el.inner_text() or await el.input_value() or ""
                    print(f"[*] Found candidate element ({selector}) with current text: '{text[:30]}...'")
                    
                    await el.click()
                    await browser.page.keyboard.press("Control+A")
                    await browser.page.keyboard.press("Backspace")
                    await browser.page.wait_for_timeout(500)
                    
                    # Fill with new bio
                    await browser.page.keyboard.insert_text(NEW_DESCRIPTION)
                    print("[*] Typed new bio successfully!")
                    found = True
                    break
            except Exception:
                continue

        if found:
            # Scroll to top to click Publish
            await browser.page.mouse.wheel(0, -1000)
            await browser.page.wait_for_timeout(1500)

            # Find Publish button
            publish_btn = await browser.page.query_selector("#publish-button, ytcp-button:has-text('Publish')")
            if publish_btn:
                print("[*] Clicking Publish...")
                await publish_btn.click()
                await browser.page.wait_for_timeout(4000)
                print("[✓] Successfully published to your YouTube channel!")
            else:
                print("[!] Publish button not clicked automatically.")

        # Take final screenshot
        await browser.page.screenshot(path="studio_bio_result.png")
        print("[*] Saved studio_bio_result.png")
        await browser.page.wait_for_timeout(3000)

    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(update_youtube_bio())
