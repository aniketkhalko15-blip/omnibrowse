import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnibrowse import OmniBrowser

async def add_links():
    browser = OmniBrowser(headless=False)
    await browser.start()
    try:
        url = "https://studio.youtube.com/channel/UCiUaMrbQT8uYeS7XQAG5oJw/editing/profile"
        await browser.page.goto(url, wait_until="networkidle", timeout=60000)
        await browser.page.wait_for_timeout(3000)

        # Scroll inner container down to Links section
        await browser.page.evaluate('''() => {
            const containers = Array.from(document.querySelectorAll('*')).filter(el => el.scrollHeight > el.clientHeight && el.clientHeight > 300);
            containers.forEach(c => c.scrollTop = 900);
        }''')
        await browser.page.wait_for_timeout(1500)

        # YouTube Studio link inputs are wrapped inside custom elements. Let's find real <input> elements
        inputs = await browser.page.query_selector_all("input")
        print(f"[*] Found {len(inputs)} inputs on page.")

        # Filter out inputs that are part of the link rows
        link_inputs = []
        for inp in inputs:
            placeholder = await inp.get_attribute("placeholder") or ""
            val = await inp.input_value() or ""
            if "title" in placeholder.lower() or "url" in placeholder.lower() or "http" in val.lower() or "pooja" in val.lower():
                link_inputs.append(inp)

        print(f"[*] Found {len(link_inputs)} link inputs.")

        if len(link_inputs) >= 2:
            print("[*] Typing OmniBrowse repo details...")
            # Title
            await link_inputs[0].click()
            await browser.page.keyboard.press("Control+A")
            await browser.page.keyboard.press("Backspace")
            await link_inputs[0].type("OmniBrowse (AI Browser)", delay=20)

            # URL
            await link_inputs[1].click()
            await browser.page.keyboard.press("Control+A")
            await browser.page.keyboard.press("Backspace")
            await link_inputs[1].type("https://github.com/aniketkhalko15-blip/omnibrowse", delay=20)
            await browser.page.wait_for_timeout(1000)

            # Scroll back up to Publish
            await browser.page.evaluate('''() => {
                const containers = Array.from(document.querySelectorAll('*')).filter(el => el.scrollHeight > el.clientHeight && el.clientHeight > 300);
                containers.forEach(c => c.scrollTop = 0);
            }''')
            await browser.page.wait_for_timeout(1000)

            publish_btn = await browser.page.query_selector("#publish-button, button:has-text('Publish')")
            if publish_btn:
                print("[*] Clicking Publish button...")
                await publish_btn.click()
                await browser.page.wait_for_timeout(4000)
                print("[✓] Custom link published successfully!")

        await browser.page.screenshot(path="studio_links_saved.png")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(add_links())
