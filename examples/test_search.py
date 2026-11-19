import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnibrowse import OmniBrowser, print_banner

async def test_stealth_search():
    print_banner()
    print("=" * 65)
    print("  🕵️ OmniBrowse Autonomous Search & Content Extraction")
    print("=" * 65)

    browser = OmniBrowser(headless=False)
    await browser.start()

    try:
        topic = "Grand Theft Auto VI release updates"
        print(f"[*] Navigating to search engine for topic: '{topic}'...")
        await browser.goto(f"https://www.google.com/search?q={topic.replace(' ', '+')}")
        await asyncio.sleep(3)

        print("[*] Parsing top search headlines...")
        headlines = await browser.page.evaluate('''() => {
            return Array.from(document.querySelectorAll('h3')).map(h => h.innerText.trim()).filter(t => t.length > 5).slice(0, 5);
        }''')

        print("\n" + "=" * 50)
        print("  🔥 TOP HEADLINES FOUND BY OMNIBROWSE:")
        print("=" * 50)
        for i, h in enumerate(headlines, 1):
            print(f"{i}. {h}")
        print("=" * 50)

        await browser.page.screenshot(path="search_demo.png")
        print("\n[✓] Search demo completed and snapshot saved to search_demo.png!")
        await asyncio.sleep(3)

    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_stealth_search())
