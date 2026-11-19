import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnibrowse import OmniBrowser, print_banner

async def search_gta6():
    print_banner()
    b = OmniBrowser(headless=False)
    await b.start()
    url = 'https://www.youtube.com/results?search_query=GTA+6+gameplay&sp=CAI%253D'
    print(f'[*] Navigating to {url}...')
    await b.goto(url)
    await asyncio.sleep(4)
    
    videos = await b.page.evaluate('''() => {
        const results = [];
        const items = document.querySelectorAll('ytd-video-renderer, ytd-rich-item-renderer');
        items.forEach(item => {
            const titleEl = item.querySelector('#video-title, #video-title-link');
            const metaEl = item.querySelector('#metadata-line');
            if (titleEl && titleEl.innerText.trim() && titleEl.href) {
                results.push({
                    title: titleEl.innerText.trim(),
                    url: titleEl.href,
                    meta: metaEl ? metaEl.innerText.trim().replace(/\\n/g, ' • ') : ''
                });
            }
        });
        return results.slice(0, 10);
    }''')
    
    print('\n' + '='*60)
    print(f'🔥 TOP RECENT GTA 6 VIDEOS ON YOUTUBE ({len(videos)} found):')
    print('='*60)
    for i, v in enumerate(videos, 1):
        print(f"{i}. {v['title']}")
        print(f"   Link: {v['url']}")
        if v['meta']:
            print(f"   Stats: {v['meta']}")
    print('='*60)
    await b.page.screenshot(path='gta6_results.png')
    await b.close()

if __name__ == "__main__":
    asyncio.run(search_gta6())
