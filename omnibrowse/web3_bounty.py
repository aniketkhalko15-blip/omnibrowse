"""
OmniBrowse Web3 Bounty Scout
=============================
Scrapes Superteam Earn + Gitcoin Grants + DoraHacks for live crypto
bounties. Handles React SPAs properly with scroll + JS extraction.
Saves all findings to web3_bounties.json.

Usage:
    from omnibrowse.web3_bounty import Web3BountyScout
    scout = Web3BountyScout()
    asyncio.run(scout.run())
"""

import asyncio
import os
import re
import sys
import json
from datetime import datetime
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from omnibrowse.banner import print_banner

WALLET = "0xB9C7335a345130658453F30Aad5d811c9e359500"

# ── Superteam categories to scan ────────────────────────────────────────────
SUPERTEAM_URLS = [
    "https://earn.superteam.fun/all",
    "https://earn.superteam.fun/bounties",
]

DORAHACKS_URL = "https://dorahacks.io/hackathon"
GITCOIN_URL   = "https://grants.gitcoin.co"


class Web3BountyScout:
    """
    Autonomous Web3 Bounty & Grant Scout.
    Finds live bounties on Superteam Earn, DoraHacks, and Gitcoin.
    """

    def __init__(self):
        self.bounties: list = []
        self.report_path = "web3_bounties.json"

    # ────────────────────────────────────────────────────────────────────────
    # Superteam Earn (React SPA — needs deep scroll + JS eval)
    # ────────────────────────────────────────────────────────────────────────
    async def _scan_superteam(self, page, url: str):
        print(f"\n  [*] Superteam Earn → {url}")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Wait for JS hydration then scroll to trigger lazy-loading
            await asyncio.sleep(5)
            for _ in range(6):
                await page.keyboard.press("End")
                await asyncio.sleep(1.5)
            await asyncio.sleep(3)

            # Broad JS extraction — grab any element with reward-looking text
            bounties = await page.evaluate("""() => {
                const results = [];
                const seen = new Set();

                // Try card-based selectors first
                const selectors = [
                    'a[href*="/bounties/"]',
                    'a[href*="/project/"]',
                    'a[href*="/hackathon/"]',
                    '[class*="card"]',
                    '[class*="listing"]',
                    '[class*="bounty"]',
                    '[class*="grant"]',
                    'article',
                    'li',
                ];

                for (const sel of selectors) {
                    const els = document.querySelectorAll(sel);
                    els.forEach(el => {
                        const txt = el.innerText || '';
                        const href = el.href || '';
                        if (
                            (txt.includes('$') || txt.includes('USDC') ||
                             txt.includes('SOL') || txt.includes('USDT')) &&
                            txt.length > 20 && !seen.has(txt.slice(0,60))
                        ) {
                            seen.add(txt.slice(0,60));
                            results.push({
                                text: txt.slice(0, 200).replace(/\\n/g, ' | '),
                                href: href || window.location.href,
                                source: 'superteam'
                            });
                        }
                    });
                    if (results.length >= 20) break;
                }

                // Fallback: extract all text that looks like bounty rewards
                if (results.length === 0) {
                    const walker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_TEXT,
                        null
                    );
                    let node;
                    while (node = walker.nextNode()) {
                        const t = node.textContent.trim();
                        if (
                            t.length > 30 &&
                            (t.match(/\\$[0-9,]+/) || t.includes('USDC') || t.includes('SOL')) &&
                            !seen.has(t.slice(0,50))
                        ) {
                            seen.add(t.slice(0,50));
                            results.push({
                                text: t.slice(0, 200),
                                href: window.location.href,
                                source: 'superteam_text'
                            });
                        }
                    }
                }
                return results.slice(0, 25);
            }""")

            # Also extract page title + all links with /bounties/ in them
            bounty_links = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('a'))
                    .filter(a => a.href.includes('/bounties/') || a.href.includes('/project/'))
                    .map(a => ({
                        text: a.innerText.trim().slice(0, 100),
                        href: a.href,
                        source: 'superteam_link'
                    }))
                    .filter(a => a.text.length > 3)
                    .slice(0, 30);
            }""")

            combined = bounties + bounty_links
            print(f"  [✓] Found {len(combined)} items on Superteam Earn")
            self.bounties.extend(combined)

            # Screenshot
            shot = f"superteam_{url.split('/')[-1]}.png"
            await page.screenshot(path=shot, full_page=False)
            print(f"  [✓] Screenshot: {shot}")

        except Exception as e:
            print(f"  [!] Superteam error: {e}")

    # ────────────────────────────────────────────────────────────────────────
    # DoraHacks (Hackathons & Bounties)
    # ────────────────────────────────────────────────────────────────────────
    async def _scan_dorahacks(self, page):
        print(f"\n  [*] DoraHacks → {DORAHACKS_URL}")
        try:
            await page.goto(DORAHACKS_URL, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(4)
            for _ in range(4):
                await page.keyboard.press("End")
                await asyncio.sleep(1.5)

            items = await page.evaluate("""() => {
                const results = [];
                const seen = new Set();
                document.querySelectorAll('a[href*="/hackathon/"], a[href*="/bounty/"]').forEach(a => {
                    const txt = a.innerText.trim();
                    if (txt.length > 5 && !seen.has(txt.slice(0,50))) {
                        seen.add(txt.slice(0,50));
                        results.push({
                            text: txt.slice(0,200),
                            href: a.href,
                            source: 'dorahacks'
                        });
                    }
                });
                // Also try card divs
                document.querySelectorAll('[class*="hackathon"], [class*="bounty"], [class*="card"]').forEach(el => {
                    const txt = el.innerText.trim();
                    const reward = txt.match(/\\$[0-9,KkMm]+|[0-9,]+ USDC|[0-9]+ SOL/);
                    if (reward && txt.length > 20 && !seen.has(txt.slice(0,50))) {
                        seen.add(txt.slice(0,50));
                        results.push({
                            text: txt.slice(0,200).replace(/\\n/g,' | '),
                            href: window.location.href,
                            source: 'dorahacks'
                        });
                    }
                });
                return results.slice(0, 20);
            }""")

            print(f"  [✓] Found {len(items)} items on DoraHacks")
            self.bounties.extend(items)

            await page.screenshot(path="dorahacks_scan.png", full_page=False)
            print(f"  [✓] Screenshot: dorahacks_scan.png")

        except Exception as e:
            print(f"  [!] DoraHacks error: {e}")

    # ────────────────────────────────────────────────────────────────────────
    # Pretty print + save
    # ────────────────────────────────────────────────────────────────────────
    def _extract_reward(self, text: str) -> str:
        m = re.search(r'\$[\d,KkMm]+|\d[\d,]*\s*(?:USDC|USDT|SOL|ETH)', text, re.I)
        return m.group(0) if m else "?"

    def _print_findings(self):
        print("\n" + "=" * 65)
        print(f"  💰 WEB3 BOUNTIES FOUND — {len(self.bounties)} total")
        print("=" * 65)

        # Sort by source
        for src in ["superteam_link", "superteam", "superteam_text", "dorahacks"]:
            subset = [b for b in self.bounties if b.get("source") == src]
            if not subset:
                continue
            label = {
                "superteam_link":  "🟣 SUPERTEAM EARN — Bounty Links",
                "superteam":       "🟣 SUPERTEAM EARN — Card Listings",
                "superteam_text":  "🟣 SUPERTEAM EARN — Text Matches",
                "dorahacks":       "🔵 DORAHACKS — Hackathons",
            }.get(src, src)
            print(f"\n{label} ({len(subset)} items):")
            for i, b in enumerate(subset[:15], 1):
                reward = self._extract_reward(b.get("text", ""))
                name   = b.get("text", "")[:60].strip()
                href   = b.get("href", "")
                print(f"  {i:2}. [{reward:>12}] {name}")
                if href and href != "https://earn.superteam.fun/all":
                    print(f"       → {href}")

        print("\n" + "=" * 65)

    def _save_report(self):
        report = {
            "generated_at": datetime.now().isoformat(),
            "wallet": WALLET,
            "total": len(self.bounties),
            "bounties": self.bounties,
        }
        with open(self.report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"[✓] Report saved → {os.path.abspath(self.report_path)}")

    # ────────────────────────────────────────────────────────────────────────
    # Main runner
    # ────────────────────────────────────────────────────────────────────────
    async def run(self):
        print_banner()
        print("=" * 65)
        print("  ⚡ OMNIBROWSE WEB3 BOUNTY SCOUT")
        print(f"  Wallet: {WALLET}")
        print("=" * 65)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                # Scan Superteam
                for url in SUPERTEAM_URLS:
                    await self._scan_superteam(page, url)
                    await asyncio.sleep(2)

                # Scan DoraHacks
                await self._scan_dorahacks(page)

            finally:
                await browser.close()

        self._print_findings()
        self._save_report()
        print("\n🎯 Next: Sign up at earn.superteam.fun → submit to top bounties!")
        print("🎯 For EVM bounties → DoraHacks accepts MetaMask directly!")
        print(f"🎯 Your wallet: {WALLET}")


if __name__ == "__main__":
    asyncio.run(Web3BountyScout().run())
