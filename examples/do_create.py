import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnibrowse import OmniBrowser

async def create():
    browser = OmniBrowser(headless=False)
    await browser.start()
    try:
        url = "https://github.com/new"
        print(f"[*] Navigating to {url}...")
        await browser.goto(url)
        await asyncio.sleep(3)

        # In GitHub's React UI, the Repository name input has data-testid="repository-name-input"
        print("[*] Clicking the exact Repository name input box...")
        
        # Click the red outlined box in the screenshot directly
        await browser.page.click("input[aria-label*='Repository name' i], input[data-testid='repository-name-input'], form input[type='text']")
        await asyncio.sleep(0.5)
        
        # Type omnibrowse
        print("[*] Typing 'omnibrowse' via keyboard...")
        await browser.page.keyboard.type("omnibrowse", delay=50)
        await asyncio.sleep(2)

        # Also type description
        desc_box = await browser.page.query_selector("input#\\:r3\\:, input[aria-label*='Description' i], input[name='Description']")
        if desc_box:
            await desc_box.click()
            await browser.page.keyboard.type("The Universal Autonomous Browser Engine for AI Agents", delay=20)
            await asyncio.sleep(1)

        # Scroll to bottom
        print("[*] Scrolling to Create repository button...")
        await browser.page.evaluate("window.scrollBy(0, 700);")
        await asyncio.sleep(1)

        # Click the green button
        create_btn = await browser.page.wait_for_selector("button:has-text('Create repository')", timeout=5000)
        if create_btn:
            print("[*] Clicking green 'Create repository' button...")
            await create_btn.click()
            await asyncio.sleep(6)
            print(f"[SUCCESS] Current Page: {browser.page.url}")

        await browser.page.screenshot(path="gh_created_final.png")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(create())
