"""
OmniBrowse Bounty Hunter — Full Run
=====================================
Runs Bug Bounty recon + Web3 Bounty scan in sequence.
Results saved to bug_bounty_report.json and web3_bounties.json.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from omnibrowse.bounty_hunter import BugBountyHunter
from omnibrowse.web3_bounty import Web3BountyScout
from omnibrowse import print_banner

async def main():
    print_banner()
    print("=" * 65)
    print("  🏹 OMNIBROWSE BOUNTY HUNTER — FULL SWEEP")
    print("  Bug Bounties + Web3 Bounties")
    print("=" * 65)

    # ── Phase 1: Bug Bounty Recon ────────────────────────────────────
    print("\n\n📌 PHASE 1: BUG BOUNTY RECON (HackerOne Public Programs)")
    print("-" * 65)
    hunter = BugBountyHunter(max_targets=3)
    await hunter.run()

    # ── Phase 2: Web3 Bounty Scan ────────────────────────────────────
    print("\n\n📌 PHASE 2: WEB3 BOUNTY SCAN (Superteam + DoraHacks)")
    print("-" * 65)
    scout = Web3BountyScout()
    await scout.run()

    print("\n\n" + "=" * 65)
    print("  🎯 ALL DONE! Check these files:")
    print("     📄 bug_bounty_report.json  — Security findings to submit")
    print("     📄 web3_bounties.json      — Crypto bounties to apply for")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(main())
