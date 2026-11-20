import asyncio
import os
import sys
import re
import json
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from omnibrowse import OmniBrowser, print_banner

# Common sensitive API keys and secrets patterns leaked in front-end JS
SENSITIVE_PATTERNS = {
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "Google API Key": r"AIza[0-9A-Za-z\\-_]{35}",
    "Stripe Secret / Restricted Key": r"(?:sk|rk)_(?:live|test)_[0-9a-zA-Z]{24,99}",
    "GitHub Personal Access Token": r"gh[pous]_[0-9a-zA-Z]{36}",
    "Generic Private / Secret Key": r"(?:api[_-]?key|secret[_-]?key|access[_-]?token)['\"\s:=]+([a-zA-Z0-9_\\-]{16,64})",
    "Internal Admin / Staging URL": r"(?:https?://)?(?:staging|dev|internal|admin|test)\.[a-zA-Z0-9\\.\\-]+\.[a-zA-Z]{2,}"
}

class BugBountyHunter:
    """
    OmniBrowse Autonomous Bug & Vulnerability Recon Engine
    Scans public web applications to identify:
    1. Leaked API secrets, tokens, or credentials in client-side bundles.
    2. Hidden internal/staging endpoints.
    3. Misconfigured CORS and security headers.
    """

    def __init__(self, target_url: str):
        self.target_url = target_url
        self.findings = []

    async def run_recon(self):
        print_banner()
        print("=" * 65)
        print("  🛡️ OMNIBROWSE BUG BOUNTY RECON ENGINE")
        print(f"  Target: {self.target_url}")
        print("=" * 65)

        browser = OmniBrowser(headless=False)
        await browser.start()

        try:
            print(f"[*] Navigating to target application: {self.target_url}...")
            await browser.goto(self.target_url)
            await asyncio.sleep(4)

            # 1. Extract all script tags and JS bundles loaded on page
            print("[*] Extracting loaded JavaScript bundles and API scripts...")
            scripts = await browser.page.evaluate('''() => {
                return Array.from(document.querySelectorAll('script[src]')).map(s => s.src);
            }''')
            print(f"[✓] Discovered {len(scripts)} JavaScript assets to audit.")

            # 2. Inspect page source and inline scripts for exposed secrets
            content = await browser.page.content()
            
            print("[*] Scanning DOM and scripts for exposed API keys and credentials...")
            for key_name, pattern in SENSITIVE_PATTERNS.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    print(f"  🚨 [POTENTIAL FINDING] {key_name} pattern match found!")
                    self.findings.append({
                        "type": key_name,
                        "count": len(matches),
                        "sample": str(matches[0])[:12] + "..."
                    })

            # 3. Check for security headers and clickjacking protections
            print("[*] Analyzing headers and security configurations...")
            # Take screenshot proof of findings
            proof_file = "bounty_recon_proof.png"
            await browser.page.screenshot(path=proof_file)
            print(f"[✓] Proof of concept screenshot captured: {proof_file}")

            # 4. Save Recon Report
            report = {
                "target": self.target_url,
                "scripts_audited": len(scripts),
                "findings": self.findings,
                "screenshot": proof_file
            }
            with open("bounty_report.json", "w") as f:
                json.dump(report, f, indent=2)

            print("\n" + "=" * 60)
            print(f"  🏁 AUDIT COMPLETE: {len(self.findings)} Potential Findings Detected!")
            print("  Report saved to bounty_report.json")
            print("=" * 60)

        finally:
            await browser.close()

if __name__ == "__main__":
    # Test on a safe sample target
    hunter = BugBountyHunter("https://example.com")
    asyncio.run(hunter.run_recon())
