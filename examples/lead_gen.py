import asyncio
import os
import sys
import csv
from omnibrowse import OmniBrowser, print_banner

async def scrape_leads(search_term: str = "Web development agency in Mumbai"):
    """
    Autonomous B2B Lead Extractor
    Navigates public directory search results and compiles business names and links into CSV.
    This is the core engine for your freelance lead generation service!
    """
    print_banner()
    print(f"[*] OmniBrowse Lead Gen: Extracting business leads for '{search_term}'...")

    browser = OmniBrowser(headless=False)
    await browser.start()

    try:
        url = f"https://www.bing.com/search?q={search_term.replace(' ', '+')}"
        await browser.goto(url)
        await asyncio.sleep(3)

        leads = await browser.page.evaluate('''() => {
            const list = [];
            const results = document.querySelectorAll('li.b_algo');
            results.forEach(r => {
                const titleEl = r.querySelector('h2 a');
                const snippetEl = r.querySelector('.b_caption p, p');
                if (titleEl) {
                    list.push({
                        title: titleEl.innerText.trim(),
                        url: titleEl.href,
                        snippet: snippetEl ? snippetEl.innerText.trim() : ''
                    });
                }
            });
            return list;
        }''')

        print(f"\n[✓] Extracted {len(leads)} business leads!")

        csv_file = "leads_output.csv"
        with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "url", "snippet"])
            writer.writeheader()
            for row in leads:
                writer.writerow(row)

        print(f"[✓] Leads exported successfully to {csv_file}")

    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_leads())
