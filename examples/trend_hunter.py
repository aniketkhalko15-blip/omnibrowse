import asyncio
import os
import sys
import json
from typing import List, Dict, Any
from omnibrowse import OmniBrowser, print_banner

async def find_trending_topics(niche: str = "ai automation") -> List[Dict[str, Any]]:
    """
    Autonomous tool to scrape trending YouTube search results,
    extract video titles, views, channels, and generate viral Short ideas.
    """
    print_banner()
    print(f"[*] OmniBrowse Hunter: Scouting viral trends for '{niche}'...")

    browser = OmniBrowser(headless=False)
    await browser.start()
    results = []

    try:
        search_query = f"{niche} shorts"
        url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
        print(f"[*] Opening search feed: {url}")
        await browser.goto(url)
        await asyncio.sleep(4)

        # Scroll to load dynamic video items
        await browser.scroll("down", 1200)
        await asyncio.sleep(2)

        # Scrape video titles and metadata
        scrape_script = """
        () => {
            const data = [];
            const cards = document.querySelectorAll('ytd-video-renderer, ytd-reel-item-renderer, ytd-rich-item-renderer');
            cards.forEach(card => {
                const titleEl = card.querySelector('#video-title, #video-title-link');
                const metaEl = card.querySelector('#metadata-line, .inline-metadata-item');
                const linkEl = card.querySelector('a#thumbnail, a#video-title-link');

                if (titleEl && titleEl.innerText.trim()) {
                    data.push({
                        title: titleEl.innerText.trim(),
                        url: linkEl ? linkEl.href : null,
                        meta: metaEl ? metaEl.innerText.trim() : ''
                    });
                }
            });
            return data.slice(0, 10);
        }
        """
        results = await browser.page.evaluate(scrape_script)
        
        print("\n" + "=" * 60)
        print(f"  🔥 TOP VIRAL TOPICS FOUND ({len(results)} items)")
        print("=" * 60)
        for i, item in enumerate(results, 1):
            print(f"{i}. {item['title']}")
            if item.get('meta'):
                print(f"   Views/Date: {item['meta'].replace(chr(10), ' • ')}")
        print("=" * 60)

        # Save to file for easy reference
        with open("viral_ideas.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print("[✓] Report saved to viral_ideas.json")

    finally:
        await browser.close()
    
    return results

if __name__ == "__main__":
    asyncio.run(find_trending_topics("ai agent automation"))
