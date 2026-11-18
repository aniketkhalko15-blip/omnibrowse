import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnibrowse import OmniBrowser, print_banner

async def auto_create_repo():
    print_banner()
    print("[*] Launching OmniBrowse to create GitHub repository...")
    browser = OmniBrowser(headless=False)
    await browser.start()

    try:
        await browser.goto("https://github.com/new")
        await asyncio.sleep(4)

        current_url = browser.page.url
        print(f"[*] Loaded URL: {current_url}")

        if "login" in current_url:
            print("\n" + "=" * 60)
            print("  ⚠️ GITHUB LOGIN NEEDED IN OMNIBROWSE WINDOW")
            print("=" * 60)
            print("The OmniBrowse browser window is open in front of you on GitHub Login.")
            print("Please enter your GitHub username & password in that window right now.")
            print("Once you sign in, OmniBrowse will automatically take over and create the repo!")
            print("=" * 60)
            
            # Wait up to 3 minutes for you to complete the sign-in in that window
            for i in range(36):
                await asyncio.sleep(5)
                if "login" not in browser.page.url:
                    print("\n[✓] Detected login successful! Proceeding...")
                    break
            
            if "github.com/new" not in browser.page.url:
                await browser.goto("https://github.com/new")
                await asyncio.sleep(3)

        if "github.com/new" in browser.page.url:
            print("[*] On repository creation page. Typing repository name...")
            # GitHub repo name input selector
            input_el = await browser.page.wait_for_selector("input[data-testid='repository-name-input'], input[name='name'], input#repository_name", timeout=10000)
            if input_el:
                await input_el.fill("omnibrowse")
                print("[*] Repository name 'omnibrowse' entered!")
                await asyncio.sleep(2)

            # Click Create repository button
            btn = await browser.page.wait_for_selector("button:has-text('Create repository'), button[type='submit']", timeout=10000)
            if btn:
                print("[*] Clicking 'Create repository' button...")
                await btn.click()
                await asyncio.sleep(5)
                print(f"[✓] Repo created! Final URL: {browser.page.url}")

        await browser.page.screenshot(path="gh_created_result.png")

    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(auto_create_repo())
