import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnibrowse import OmniBrowser, print_banner

async def login_github():
    print_banner()
    print("=" * 60)
    print("  🐙 OmniBrowse GitHub Session Setup")
    print("=" * 60)
    print("[*] Launching browser directly to GitHub login...")

    browser = OmniBrowser(headless=False)
    await browser.start()

    # Open GitHub login directly!
    await browser.goto("https://github.com/login")

    try:
        print("\n[!] The browser window is now on GitHub's sign-in page.")
        print("[!] Log into your account (aniketkhalko15-blip).")
        input("\n[✓] Press [Enter] here in PowerShell once you see your GitHub dashboard! ")
    finally:
        print("[*] Saving session and closing...")
        await browser.close()
        print("\n[SUCCESS] GitHub session saved to your profile!")

if __name__ == "__main__":
    asyncio.run(login_github())
