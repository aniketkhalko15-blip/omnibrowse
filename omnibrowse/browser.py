import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright, BrowserContext, Page

class OmniBrowser:
    """
    OmniBrowse Core Browser Engine with Persistent Profile Support.
    Allows the user to log into accounts manually once, and then lets
    AI agents automate actions inside that logged-in session safely.
    """

    def __init__(self, headless: bool = False, profile_dir: Optional[str] = None):
        self.headless = headless
        self.profile_dir = profile_dir or str(Path.home() / ".omnibrowse" / "browser_profile")
        self.playwright = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.interactive_elements: Dict[str, Any] = {}

    async def start(self):
        """Launch Chromium with persistent user profile (stores cookies/sessions)."""
        Path(self.profile_dir).mkdir(parents=True, exist_ok=True)
        
        self.playwright = await async_playwright().start()
        
        # launch_persistent_context saves logins, cookies, and localStorage
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.profile_dir,
            headless=self.headless,
            viewport={"width": 1280, "height": 800},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Grab existing page or open a fresh one
        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = await self.context.new_page()
            
        return self

    async def goto(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL and return initial page state."""
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"
        await self.page.goto(url, wait_until="domcontentloaded", timeout=45000)
        await self.page.wait_for_timeout(2000)
        return await self.get_state()

    async def get_state(self) -> Dict[str, Any]:
        """Extract clean, indexed interactive elements for LLMs."""
        if not self.page:
            return {}

        title = await self.page.title()
        url = self.page.url

        elements_script = """
        () => {
            const items = [];
            const selectors = 'a, button, input, select, textarea, [role="button"], [role="link"], [role="checkbox"], [tabindex]:not([tabindex="-1"])';
            const nodes = Array.from(document.querySelectorAll(selectors));

            let counter = 1;
            nodes.forEach(node => {
                const rect = node.getBoundingClientRect();
                const style = window.getComputedStyle(node);
                const isVisible = rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
                
                if (isVisible) {
                    const tag = node.tagName.toLowerCase();
                    const text = (node.innerText || node.placeholder || node.getAttribute('aria-label') || node.value || '').trim().slice(0, 80);
                    const type = node.getAttribute('type') || tag;
                    
                    const agentId = String(counter++);
                    node.setAttribute('data-omni-id', agentId);

                    items.push({
                        id: agentId,
                        tag: tag,
                        type: type,
                        text: text,
                        placeholder: node.placeholder || null,
                        href: node.href || null
                    });
                }
            });
            return items;
        }
        """
        raw_elements = await self.page.evaluate(elements_script)
        self.interactive_elements = {el["id"]: el for el in raw_elements}

        element_lines = []
        for el in raw_elements[:100]:
            desc = f"[{el['id']}] <{el['tag']}> {el['text']}" if el['text'] else f"[{el['id']}] <{el['tag']}>"
            if el.get('placeholder'):
                desc += f" (placeholder: {el['placeholder']})"
            element_lines.append(desc)

        ai_prompt_view = (
            f"Page Title: {title}\n"
            f"URL: {url}\n\n"
            f"--- Interactive Elements ---\n" +
            ("\n".join(element_lines) if element_lines else "(No interactive elements)")
        )

        return {
            "title": title,
            "url": url,
            "ai_view": ai_prompt_view,
            "elements_count": len(raw_elements)
        }

    async def click(self, element_id: str) -> Dict[str, Any]:
        """Click an interactive element by its Omni ID."""
        if not self.page:
            raise RuntimeError("Browser not started")
        selector = f'[data-omni-id="{element_id}"]'
        await self.page.click(selector, timeout=8000)
        await self.page.wait_for_timeout(1500)
        return await self.get_state()

    async def type_text(self, element_id: str, text: str, press_enter: bool = False) -> Dict[str, Any]:
        """Type text into an input field by its Omni ID."""
        if not self.page:
            raise RuntimeError("Browser not started")
        selector = f'[data-omni-id="{element_id}"]'
        await self.page.fill(selector, text, timeout=8000)
        if press_enter:
            await self.page.press(selector, "Enter")
        await self.page.wait_for_timeout(1500)
        return await self.get_state()

    async def screenshot(self, path: str = "omni_screenshot.png") -> str:
        """Capture screenshot for visual verification."""
        if not self.page:
            raise RuntimeError("Browser not started")
        await self.page.screenshot(path=path)
        return path

    async def close(self):
        """Cleanly close context and playwright instances."""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
