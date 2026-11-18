import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnibrowse import OmniBrowser

async def scroll_main_container():
    browser = OmniBrowser(headless=False)
    await browser.start()
    try:
        url = "https://studio.youtube.com/channel/UCiUaMrbQT8uYeS7XQAG5oJw/editing/profile"
        await browser.page.goto(url, wait_until="networkidle", timeout=60000)
        await browser.page.wait_for_timeout(4000)

        # YouTube Studio scrolls inside a specific div or main container, not window!
        scroll_script = """
        () => {
            const containers = Array.from(document.querySelectorAll('*')).filter(el => {
                return el.scrollHeight > el.clientHeight && el.clientHeight > 300;
            });
            containers.forEach(c => {
                c.scrollTop = c.scrollHeight;
            });
            return containers.length;
        }
        """
        count = await browser.page.evaluate(scroll_script)
        print(f"Scrolled {count} inner scrollable containers.")
        await browser.page.wait_for_timeout(2000)
        await browser.page.screenshot(path="studio_bottom.png")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scroll_main_container())
