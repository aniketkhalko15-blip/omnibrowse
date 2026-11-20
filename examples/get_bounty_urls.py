import asyncio
from playwright.async_api import async_playwright

async def inspect_bounties():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            url = "https://earn.superteam.fun/bounties"
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(4)

            # Scroll down to bring cards into viewport
            await page.evaluate("window.scrollBy(0, 500);")
            await asyncio.sleep(2)

            # Find all clickable links containing /listings/ or /bounties/
            links = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('a[href*="/listings/"], a[href*="/bounties/"]')).map(a => ({
                    text: a.innerText.replace(/\\n/g, ' | '),
                    href: a.href
                }));
            }''')

            print("\n" + "=" * 60)
            print(f"  FOUND {len(links)} BOUNTY LINKS:")
            print("=" * 60)
            for i, l in enumerate(links[:6], 1):
                print(f"{i}. {l['text']}")
                print(f"   URL: {l['href']}")
            print("=" * 60)

            # Click the first one directly via URL
            if links:
                target_url = links[0]['href']
                print(f"\n[*] Navigating directly to top bounty: {target_url}...")
                await page.goto(target_url, wait_until="networkidle", timeout=60000)
                await asyncio.sleep(3)
                print(f"[*] Title: {await page.title()}")

                # Extract requirements text
                text_content = await page.evaluate('''() => {
                    return document.querySelector('main, article, #__next')?.innerText.slice(0, 2000) || '';
                }''')
                print("\n--- BOUNTY DETAILS ---")
                print(text_content[:1500])
                print("----------------------")

                await page.screenshot(path="bounty_details_captured.png")

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_bounties())
