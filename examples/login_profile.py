import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnibrowse import OmniBrowser, print_banner

async def login_session():
    print_banner()
    print("=" * 60)
    print("  🔑 OmniBrowse Persistent Profile Login Setup")
    print("=" * 60)
    print("[*] Launching browser window...")
    print("[*] Log into your accounts (YouTube, GitHub, etc.) manually.")
    print("[*] Your session cookies will be stored locally on your machine.")
    print("[*] Once you are logged in, close the browser window or press Enter here.")
    print("=" * 60)

    # Launch browser in visible mode with persistent context
    browser = OmniBrowser(headless=False)
    await browser.start()

    # Open YouTube Studio / YouTube
    await browser.goto("https://studio.youtube.com")

    try:
        # Keep open until user finishes
        print("\n[!] Browser is OPEN. Log into your YouTube account now.")
        input("[✓] Press [Enter] here in the terminal when you're done logging in... ")
    finally:
        print("[*] Saving session profile and closing browser...")
        await browser.close()
        print("\n[SUCCESS] Your session profile has been saved!")
        print("Now OmniBrowse can automate tasks on your account without asking for passwords!")

if __name__ == "__main__":
    asyncio.run(login_session())
