import asyncio
import json
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

class OmniBrowser:
    """
    OmniBrowse Core Browser Engine
    Designed for AI Agents (ChatGPT, Claude, Gemini, DeepSeek, Local LLMs)
    Extracts structured, token-efficient DOM representations and executes AI actions.
    """

    def __init__(self, headless: bool = False, viewport: Optional[dict] = None):
        self.headless = headless
        self.viewport = viewport or {"width": 1280, "height": 800}
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.interactive_elements: Dict[str, Any] = {}

    async def start(self):
        """Launch the Chromium browser instance."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"]
        )
        self.context = await self.browser.new_context(
            viewport=self.viewport,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = await self.context.new_page()
        return self

    async def goto(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL and return initial page state."""
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"
        await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await self.page.wait_for_timeout(1500)
        return await self.get_state()

    async def get_state(self) -> Dict[str, Any]:
        """
        Extract clean, token-efficient representation for LLMs.
        Labels every interactive element with an index [1], [2], etc.
        """
        if not self.page:
            return {}

        title = await self.page.title()
        url = self.page.url

        # Inject JavaScript to find and index visible interactive elements
        elements_script = """
        () => {
            const items = [];
            const interactiveSelectors = 'a, button, input, select, textarea, [role="button"], [role="link"], [role="checkbox"], [tabindex]:not([tabindex="-1"])';
            const nodes = Array.from(document.querySelectorAll(interactiveSelectors));

            let idCounter = 1;
            nodes.forEach(node => {
                const rect = node.getBoundingClientRect();
                const style = window.getComputedStyle(node);
                const isVisible = rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
                
                if (isVisible) {
                    const tag = node.tagName.toLowerCase();
                    const text = (node.innerText || node.placeholder || node.getAttribute('aria-label') || node.value || '').trim().slice(0, 80);
                    const type = node.getAttribute('type') || tag;
                    
                    // Mark element with an agent attribute
                    const agentId = String(idCounter++);
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

        # Build clean markdown/text summary for LLM context
        element_lines = []
        for el in raw_elements[:100]:  # Cap to top 100 for token efficiency
            desc = f"[{el['id']}] <{el['tag']}> {el['text']}" if el['text'] else f"[{el['id']}] <{el['tag']}>"
            if el.get('placeholder'):
                desc += f" (placeholder: {el['placeholder']})"
            element_lines.append(desc)

        ai_prompt_view = (
            f"Page Title: {title}\n"
            f"URL: {url}\n\n"
            f"--- Interactive Elements (Use ID to interact) ---\n" +
            ("\n".join(element_lines) if element_lines else "(No interactive elements found)")
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
        await self.page.click(selector, timeout=5000)
        await self.page.wait_for_timeout(1200)
        return await self.get_state()

    async def type_text(self, element_id: str, text: str, press_enter: bool = False) -> Dict[str, Any]:
        """Type text into an input field by its Omni ID."""
        if not self.page:
            raise RuntimeError("Browser not started")
        selector = f'[data-omni-id="{element_id}"]'
        await self.page.fill(selector, text, timeout=5000)
        if press_enter:
            await self.page.press(selector, "Enter")
        await self.page.wait_for_timeout(1200)
        return await self.get_state()

    async def scroll(self, direction: str = "down", amount: int = 500) -> Dict[str, Any]:
        """Scroll the page."""
        if not self.page:
            raise RuntimeError("Browser not started")
        delta = amount if direction == "down" else -amount
        await self.page.evaluate(f"window.scrollBy(0, {delta});")
        await self.page.wait_for_timeout(800)
        return await self.get_state()

    async def screenshot(self, path: str = "omni_screenshot.png") -> str:
        """Capture screenshot for multimodal vision models."""
        if not self.page:
            raise RuntimeError("Browser not started")
        await self.page.screenshot(path=path, full_page=False)
        return path

    async def close(self):
        """Close browser resources."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
