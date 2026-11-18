import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnibrowse import OmniBrowser

async def make_token():
    browser = OmniBrowser(headless=False)
    await browser.start()
    try:
        url = "https://github.com/settings/tokens/new"
        print(f"[*] Navigating to {url}...")
        await browser.goto(url)
        await asyncio.sleep(3)

        # Note/name of token
        note_input = await browser.page.wait_for_selector("input#oauth_access_description, input[name='description']", timeout=5000)
        if note_input:
            await note_input.fill("omnibrowse-push")

        # Select 'repo' scope checkbox
        repo_checkbox = await browser.page.wait_for_selector("input#oauth_access_scope_repo, input[value='repo']", timeout=5000)
        if repo_checkbox:
            await repo_checkbox.check()

        # Scroll to bottom
        await browser.page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        await asyncio.sleep(1)

        # Generate token button
        gen_btn = await browser.page.wait_for_selector("button:has-text('Generate token'), button[type='submit']", timeout=5000)
        if gen_btn:
            await gen_btn.click()
            await asyncio.sleep(4)

        # Extract generated token text
        token_el = await browser.page.wait_for_selector("span#new-oauth-token, code#new-oauth-token", timeout=5000)
        if token_el:
            token = (await token_el.inner_text()).strip()
            print(f"[SUCCESS] Extracted Token: {token[:4]}...{token[-4:]}")
            with open("gh_token.txt", "w") as f:
                f.write(token)

        await browser.page.screenshot(path="token_page.png")

    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(make_token())
