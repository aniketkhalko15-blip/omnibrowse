import asyncio
import os
import sys

# Add parent directory to path so omnibrowse package can be imported directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnibrowse import OmniBrowser, print_banner, check_social_verification

async def main():
    print_banner()
    
    # Prompt user to follow/subscribe before first run
    check_social_verification()

    print("[*] Launching OmniBrowse engine...")
    
    # Run in visible mode so you can see it in action
    browser = OmniBrowser(headless=False)
    await browser.start()

    try:
        url = "wikipedia.org"
        print(f"[*] Navigating to {url}...")
        state = await browser.goto(url)
        
        print("\n" + "="*50)
        print("  AI AGENT PAGE VIEW (Token Efficient)")
        print("="*50)
        print(state["ai_view"][:600] + "\n...[truncated for display]...")
        print("="*50)

        # Example action: Locate search input and type into it
        print("\n[*] Simulating AI Action: Searching for 'Artificial Intelligence'...")
        search_id = None
        for el_id, el in browser.interactive_elements.items():
            if el["tag"] == "input" and (el.get("type") in ["search", "text"] or "search" in str(el.get("text", "")).lower()):
                search_id = el_id
                break
        
        if search_id:
            print(f"[*] AI found search input at element [{search_id}]. Typing...")
            await browser.type_text(search_id, "Artificial intelligence", press_enter=True)
            await asyncio.sleep(2)
            print(f"[*] New Page Title: {browser.page.url}")
        else:
            print("[*] Taking screenshot...")
            await browser.screenshot("omni_demo.png")

        print("\n[✓] OmniBrowse test completed successfully!")
        await asyncio.sleep(3)

    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
