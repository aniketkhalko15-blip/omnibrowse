import asyncio
import os
import sys

from playwright.async_api import async_playwright

async def inspect_bounties():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            url = "https://earn.superteam.fun/bounties"
            print(f"[*] Navigating to {url}...")
            await page.goto(url, timeout=45000)
            await asyncio.sleep(4)

            # Click 'Development' filter tab to find pure software/automation tasks
            print("[*] Filtering for Development / Tech bounties...")
            dev_tab = await page.query_selector("button:has-text('Development'), div:has-text('Development')")
            if dev_tab:
                await dev_tab.click()
                await asyncio.sleep(3)

            # Scrape top 5 bounty links and titles
            bounties = await page.evaluate('''() => {
                const results = [];
                const cards = document.querySelectorAll('a[href*="/bounties/"]');
                cards.forEach(c => {
                    const title = c.innerText.trim();
                    if (title && c.href) {
                        results.push({
                            title: title.replace(/\\n/g, ' | '),
                            url: c.href
                        });
                    }
                });
                return results.slice(0, 5);
            }''')

            print("\n" + "=" * 60)
            print("  🎯 TOP LIVE TECH/DEV BOUNTIES:")
            print("=" * 60)
            for i, b in enumerate(bounties, 1):
                print(f"{i}. {b['title']}")
                print(f"   Link: {b['url']}")
            print("=" * 60)

            await page.screenshot(path="dev_bounties_screen.png")

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_bounties())
