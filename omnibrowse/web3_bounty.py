import asyncio
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from omnibrowse import OmniBrowser, print_banner

class Web3BountyScout:
    """
    OmniBrowse Web3 Bounty & Opportunity Scout
    Scrapes Web3 bounty platforms (Superteam Earn, Immunefi, Gitcoin)
    to find active bounties paying in USDC/USDT/SOL for building tools or audits.
    """

    def __init__(self):
        self.opportunities = []

    async def scan_superteam_earn(self):
        print_banner()
        print("=" * 65)
        print("  ⚡ OMNIBROWSE WEB3 BOUNTY SCOUT (Crypto & USDC Bounties)")
        print("=" * 65)

        browser = OmniBrowser(headless=False)
        await browser.start()

        try:
            url = "https://earn.superteam.fun/bounties"
            print(f"[*] Scouting live Solana & Web3 bounties at {url}...")
            await browser.goto(url)
            await asyncio.sleep(5)

            # Scrape active bounties with prize pools
            bounties = await browser.page.evaluate('''() => {
                const list = [];
                const cards = document.querySelectorAll('a[href*="/bounties/"], div[class*="bounty-card"], [role="article"]');
                cards.forEach(card => {
                    const text = card.innerText.trim();
                    if (text && (text.includes('$') || text.includes('USDC') || text.includes('SOL'))) {
                        list.push(text.slice(0, 150).replace(/\\n/g, ' | '));
                    }
                });
                return list.slice(0, 8);
            }''')

            print("\n" + "=" * 60)
            print(f"  💰 ACTIVE CRYPTO BOUNTIES FOUND ({len(bounties)} items):")
            print("=" * 60)
            for i, b in enumerate(bounties, 1):
                print(f"{i}. {b}")
            print("=" * 60)

            await browser.page.screenshot(path="web3_bounties_found.png")
            print("[✓] Snapshot saved to web3_bounties_found.png")

        finally:
            await browser.close()

if __name__ == "__main__":
    scout = Web3BountyScout()
    asyncio.run(scout.scan_superteam_earn())
