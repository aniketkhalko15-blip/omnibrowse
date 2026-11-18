import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnibrowse import OmniBrowser, print_banner

async def login_and_create():
    print_banner()
    print("=" * 60)
    print("  🐙 OmniBrowse GitHub Setup")
    print("=" * 60)
    print("[*] Launching browser directly to GitHub login...")

    browser = OmniBrowser(headless=False)
    await browser.start()

    try:
        # Navigate directly to GitHub login
        await browser.goto("https://github.com/login")
        print("\n[!] The browser window is now OPEN.")
        print("[!] Enter your GitHub login details and complete any 2FA.")
        
        # Wait until you press Enter in terminal
        input("\n[✓] Press [Enter] here in PowerShell as soon as you are logged in! ")

        print("\n[*] Awesome! Now OmniBrowse is taking over...")
        print("[*] Navigating to https://github.com/new...")
        await browser.goto("https://github.com/new")
        await asyncio.sleep(3)

        # Type repo name
        print("[*] Typing repository name: omnibrowse...")
        name_input = await browser.page.wait_for_selector(
            "input[data-testid='repository-name-input'], input[name='name'], input#repository_name", 
            timeout=10000
        )
        if name_input:
            await name_input.fill("omnibrowse")
            await asyncio.sleep(2)

        # Click Create Repository
        print("[*] Clicking 'Create repository'...")
        create_btn = await browser.page.wait_for_selector(
            "button:has-text('Create repository'), button[type='submit']", 
            timeout=10000
        )
        if create_btn:
            await create_btn.click()
            await asyncio.sleep(5)
            print(f"\n[SUCCESS] 🎉 Repository created! URL: {browser.page.url}")

    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(login_and_create())
