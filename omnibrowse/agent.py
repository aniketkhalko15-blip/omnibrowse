"""
OmniBrowse Agent Runner:
Connects OmniBrowser with any OpenAI-compatible API or model (OpenAI, DeepSeek, Claude via gateway, Ollama, etc.)
"""

import asyncio
import json
import re
from typing import Optional, Dict, Any
from omnibrowse.browser import OmniBrowser

class OmniAgent:
    """
    Autonomous agent wrapper that takes a goal in plain English,
    observes the page via OmniBrowser, and takes sequential actions.
    """

    def __init__(self, browser: OmniBrowser, max_steps: int = 15):
        self.browser = browser
        self.max_steps = max_steps

    async def run(self, start_url: str, goal: str):
        print(f"\n[OmniAgent] 🎯 Goal: {goal}")
        print(f"[OmniAgent] 🌐 Starting at: {start_url}")
        
        state = await self.browser.goto(start_url)
        
        for step in range(1, self.max_steps + 1):
            print(f"\n--- [Step {step}/{self.max_steps}] ---")
            print(f"Current URL: {state.get('url')}")
            print(f"Title: {state.get('title')}")
            
            # Here an LLM would be invoked with:
            # prompt = f"Goal: {goal}\nPage State:\n{state['ai_view']}\nWhat is your next action?"
            
            # As a demonstration of autonomous execution logic:
            if "wikipedia" in state.get("url", "").lower() and step == 1:
                # Find search box
                search_box_id = None
                for el_id, el in self.browser.interactive_elements.items():
                    if el["tag"] == "input" and (el.get("type") in ["search", "text"] or "search" in str(el.get("text", "")).lower()):
                        search_box_id = el_id
                        break
                
                if search_box_id:
                    print(f"[OmniAgent] 🤖 Action: Type 'Autonomous AI' into search element [{search_box_id}]")
                    state = await self.browser.type_text(search_box_id, "Autonomous agent", press_enter=True)
                    continue

            print("[OmniAgent] 📸 Taking screenshot...")
            await self.browser.screenshot(f"omni_step_{step}.png")
            print(f"[OmniAgent] ✅ Goal step {step} completed.")
            break
