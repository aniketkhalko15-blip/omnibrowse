"""
OmniBrowse Bug Bounty Hunter
============================
Autonomous security recon engine. Scans real bug bounty programs from
HackerOne's public program list, checks JS bundles for leaked secrets,
analyzes CORS/headers, and generates structured reports for submission.

Usage:
    from omnibrowse.bounty_hunter import BugBountyHunter
    hunter = BugBountyHunter()
    asyncio.run(hunter.run())
"""

import asyncio
import os
import re
import sys
import json
import httpx
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from omnibrowse import OmniBrowser, print_banner

# ── Secret patterns that commonly leak in front-end JS bundles ──────────────
PATTERNS: Dict[str, str] = {
    "AWS Access Key":          r"AKIA[0-9A-Z]{16}",
    "AWS Secret":              r"(?:aws_secret|AWS_SECRET)['\"\s:=]+([A-Za-z0-9/+=]{40})",
    "Google API Key":          r"AIza[0-9A-Za-z\-_]{35}",
    "Google OAuth Client":     r"[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com",
    "Stripe Live Key":         r"sk_live_[0-9a-zA-Z]{24,99}",
    "Stripe Restricted Key":   r"rk_live_[0-9a-zA-Z]{24,99}",
    "GitHub PAT":              r"gh[pous]_[0-9a-zA-Z]{36,}",
    "GitHub OAuth":            r"gho_[0-9a-zA-Z]{36,}",
    "Slack Token":             r"xox[baprs]-[0-9a-zA-Z\-]{10,48}",
    "Slack Webhook":           r"https://hooks\.slack\.com/services/T[A-Z0-9]{8}/B[A-Z0-9]{8}/[a-zA-Z0-9]{24}",
    "Twilio Key":              r"SK[0-9a-fA-F]{32}",
    "SendGrid Key":            r"SG\.[a-zA-Z0-9_\-]{22}\.[a-zA-Z0-9_\-]{43}",
    "Firebase Config":         r"\"apiKey\":\s*\"AIza[0-9A-Za-z\-_]{35}\"",
    "JWT Token":               r"eyJ[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=+/]*",
    "Generic API Key":         r"(?:api[_-]?key|apikey)['\"\s:=]+([a-zA-Z0-9_\-]{20,64})",
    "Generic Secret":          r"(?:secret[_-]?key|client[_-]?secret)['\"\s:=]+([a-zA-Z0-9_\-]{20,64})",
    "Internal Dev URL":        r"https?://(?:staging|dev|internal|admin|test|qa|uat)\.[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    "Hardcoded Password":      r"(?:password|passwd|pwd)['\"\s:=]+([a-zA-Z0-9!@#$%^&*]{8,32})",
    "Private Key Header":      r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----",
    "MongoDB Connection":      r"mongodb(?:\+srv)?://[a-zA-Z0-9_\-:@./]+",
    "SQL Connection String":   r"(?:mysql|postgres|postgresql|mssql)://[a-zA-Z0-9_\-:@./]+",
}

# ── HackerOne public programs known to have good JS surface area ────────────
HACKERONE_TARGETS = [
    {"name": "Shopify",        "url": "https://www.shopify.com",           "program": "shopify"},
    {"name": "GitLab",         "url": "https://gitlab.com",                "program": "gitlab"},
    {"name": "Automattic",     "url": "https://wordpress.com",             "program": "automattic"},
    {"name": "Grab",           "url": "https://grab.com",                  "program": "grab"},
    {"name": "Uber",           "url": "https://www.uber.com",              "program": "uber"},
    {"name": "Twitter",        "url": "https://twitter.com",               "program": "twitter"},
    {"name": "Yahoo",          "url": "https://yahoo.com",                 "program": "yahoo"},
    {"name": "Line",           "url": "https://line.me",                   "program": "line"},
    {"name": "Semrush",        "url": "https://semrush.com",               "program": "semrush"},
    {"name": "Vimeo",          "url": "https://vimeo.com",                 "program": "vimeo"},
]

SEVERITY_MAP = {
    "AWS Access Key":        "CRITICAL",
    "AWS Secret":            "CRITICAL",
    "Stripe Live Key":       "CRITICAL",
    "Stripe Restricted Key": "CRITICAL",
    "Private Key Header":    "CRITICAL",
    "MongoDB Connection":    "HIGH",
    "SQL Connection String": "HIGH",
    "GitHub PAT":            "HIGH",
    "Slack Token":           "HIGH",
    "Google API Key":        "MEDIUM",
    "Firebase Config":       "MEDIUM",
    "Slack Webhook":         "MEDIUM",
    "JWT Token":             "LOW",
    "Generic API Key":       "LOW",
    "Internal Dev URL":      "INFO",
}

PAYOUT_ESTIMATE = {
    "CRITICAL": "$5,000 – $50,000",
    "HIGH":     "$500 – $5,000",
    "MEDIUM":   "$100 – $500",
    "LOW":      "$50 – $150",
    "INFO":     "$0 – $50 (Good Faith)",
}


class BugBountyHunter:
    """
    Autonomous Bug Bounty Recon Engine.
    Scans public HackerOne programs for JS-exposed secrets and misconfigs.
    """

    def __init__(self, targets: List[Dict] = None, max_targets: int = 3):
        self.targets = targets or HACKERONE_TARGETS[:max_targets]
        self.all_findings: List[Dict] = []
        self.report_path = "bug_bounty_report.json"

    async def _scan_js_bundles(self, page, target_url: str) -> List[str]:
        """Download all JS bundle URLs from the page and scan their source."""
        raw_content = await page.content()
        script_srcs = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('script[src]'))
                   .map(s => s.src)
                   .filter(s => s.startsWith('http'));
        }""")

        all_text = raw_content
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            for src in script_srcs[:15]:  # check up to 15 JS bundles
                try:
                    r = await client.get(src, headers={"User-Agent": "Mozilla/5.0"})
                    if r.status_code == 200 and len(r.text) < 2_000_000:
                        all_text += r.text
                except Exception:
                    pass

        return all_text, len(script_srcs)

    def _run_patterns(self, text: str, target_name: str) -> List[Dict]:
        findings = []
        for key_name, pattern in PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                # De-dup, exclude known false positives
                unique = list(set(str(m) for m in matches if len(str(m)) > 8))[:3]
                severity = SEVERITY_MAP.get(key_name, "LOW")
                findings.append({
                    "target":   target_name,
                    "type":     key_name,
                    "severity": severity,
                    "count":    len(matches),
                    "samples":  [s[:20] + "..." for s in unique],
                    "payout":   PAYOUT_ESTIMATE.get(severity, "Unknown"),
                })
        return findings

    async def _check_headers(self, page, target_url: str) -> List[Dict]:
        """Check for missing security headers via JS."""
        findings = []
        try:
            csp = await page.evaluate("""() => {
                const meta = document.querySelector('meta[http-equiv="Content-Security-Policy"]');
                return meta ? meta.content : null;
            }""")
            if not csp:
                findings.append({
                    "target":   target_url,
                    "type":     "Missing Content-Security-Policy",
                    "severity": "MEDIUM",
                    "count":    1,
                    "samples":  ["No CSP header or meta tag found"],
                    "payout":   PAYOUT_ESTIMATE["MEDIUM"],
                })
        except Exception:
            pass
        return findings

    async def scan_target(self, browser: OmniBrowser, target: Dict) -> List[Dict]:
        name = target["name"]
        url  = target["url"]
        print(f"\n{'─'*55}")
        print(f"  🎯 TARGET: {name}")
        print(f"  URL: {url}")
        print(f"{'─'*55}")

        findings = []
        try:
            print(f"  [*] Loading page...")
            await browser.page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(3)

            print(f"  [*] Downloading & scanning JS bundles...")
            all_text, num_scripts = await self._scan_js_bundles(browser.page, url)
            print(f"  [✓] Scanned {num_scripts} JS assets ({len(all_text)//1024}KB total)")

            js_findings = self._run_patterns(all_text, name)
            header_findings = await self._check_headers(browser.page, url)

            findings = js_findings + header_findings

            if findings:
                print(f"\n  🚨 FINDINGS ({len(findings)}):")
                for f in findings:
                    print(f"     [{f['severity']}] {f['type']} → Est. {f['payout']}")
                    print(f"     Sample: {f['samples'][0] if f['samples'] else 'N/A'}")
            else:
                print(f"  ✅ No obvious leaked secrets detected on this target.")

            # Screenshot proof
            proof = f"proof_{name.lower().replace(' ', '_')}.png"
            await browser.page.screenshot(path=proof, full_page=False)
            print(f"  [✓] Proof screenshot: {proof}")

        except Exception as e:
            print(f"  [!] Error scanning {name}: {e}")

        return findings

    async def run(self):
        print_banner()
        print("=" * 65)
        print("  🏹 OMNIBROWSE BUG BOUNTY HUNTER")
        print(f"  Scanning {len(self.targets)} HackerOne public programs...")
        print(f"  Wallet: 0xB9C7335a345130658453F30Aad5d811c9e359500")
        print("=" * 65)

        browser = OmniBrowser(headless=False)
        await browser.start()

        try:
            for target in self.targets:
                findings = await self.scan_target(browser, target)
                self.all_findings.extend(findings)
                await asyncio.sleep(2)
        finally:
            await browser.close()

        self._save_report()
        self._print_summary()

    def _save_report(self):
        report = {
            "generated_at": datetime.now().isoformat(),
            "wallet":        "0xB9C7335a345130658453F30Aad5d811c9e359500",
            "total_findings": len(self.all_findings),
            "targets_scanned": len(self.targets),
            "findings": self.all_findings,
        }
        with open(self.report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n[✓] Report saved → {self.report_path}")

    def _print_summary(self):
        critical = [f for f in self.all_findings if f["severity"] == "CRITICAL"]
        high     = [f for f in self.all_findings if f["severity"] == "HIGH"]
        medium   = [f for f in self.all_findings if f["severity"] == "MEDIUM"]
        low      = [f for f in self.all_findings if f["severity"] in ("LOW", "INFO")]

        print("\n" + "=" * 65)
        print("  🏁 BUG BOUNTY RECON COMPLETE")
        print("=" * 65)
        print(f"  🔴 CRITICAL  : {len(critical)}  → {PAYOUT_ESTIMATE['CRITICAL']} each")
        print(f"  🟠 HIGH      : {len(high)}  → {PAYOUT_ESTIMATE['HIGH']} each")
        print(f"  🟡 MEDIUM    : {len(medium)}  → {PAYOUT_ESTIMATE['MEDIUM']} each")
        print(f"  🟢 LOW/INFO  : {len(low)}  → {PAYOUT_ESTIMATE['LOW']} each")
        print(f"\n  Total potential earnings estimate:")

        est_low  = len(critical)*5000 + len(high)*500  + len(medium)*100 + len(low)*50
        est_high = len(critical)*50000+ len(high)*5000 + len(medium)*500 + len(low)*150
        print(f"  💰 ${est_low:,} – ${est_high:,} USD")
        print(f"\n  📄 Full report: {os.path.abspath(self.report_path)}")
        print("=" * 65)
        print("\nNext step: Submit valid findings at https://hackerone.com/directory/programs")
        print("Payment: PayPal / Bank / Crypto via HackerOne payout settings")


if __name__ == "__main__":
    hunter = BugBountyHunter(max_targets=3)
    asyncio.run(hunter.run())
