import asyncio
from playwright.async_api import async_playwright

async def inspect_raenest():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            url = "https://earn.superteam.fun/bounties"
            await page.goto(url, timeout=45000)
            await asyncio.sleep(4)

            # Click directly on the Raenest 13k USDC bounty card
            print("[*] Opening 13k USDC Raenest Bounty...")
            card = await page.wait_for_selector("text='The Raenest Global Bounty'", timeout=10000)
            if card:
                await card.click()
                await asyncio.sleep(4)

            print(f"[*] Landed on Bounty Page: {page.url}")
            print(f"[*] Title: {await page.title()}")

            # Extract bounty prompt and submission guidelines
            details = await page.evaluate('''() => {
                const desc = document.querySelector('div[class*=\"description\"], article, main');
                return desc ? desc.innerText.slice(0, 1500) : 'No description found';
            }''')

            print("\n" + "=" * 60)
            print("  📋 BOUNTY REQUIREMENTS & REWARDS:")
            print("=" * 60)
            print(details)
            print("=" * 60)

            await page.screenshot(path="raenest_bounty_details.png")

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_raenest())
