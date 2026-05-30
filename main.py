import asyncio
import nest_asyncio
from playwright.async_api import async_playwright

nest_asyncio.apply()

async def search_miruro_playwright(query):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        page = await context.new_page()
        print(f"Searching for '{query}'...")
        await page.goto(f"https://www.miruro.bz/search?q={query}", wait_until="networkidle")
        try:
            await page.wait_for_selector("a[href*='/watch/']", timeout=10000)
        except:
            return []
        
        results = []
        cards = await page.query_selector_all("a[href*='/watch/']")
        for card in cards[:10]:
            href = await card.get_attribute("href")
            parts = href.split('/')
            if len(parts) > 2:
                title = (await card.inner_text()).strip().split('\n')[0]
                results.append({'id': parts[2], 'title': title})
        await browser.close()
        return results

async def get_stream_command(watch_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        streams = set()
        page.on("response", lambda r: streams.add(r.url) if ".m3u8" in r.url else None)
        
        await page.goto(watch_url, wait_until="networkidle")
        await asyncio.sleep(5)
        play_btn = await page.query_selector("video, .play-button")
        if play_btn: await play_btn.click(force=True)
        await asyncio.sleep(8)
        
        m3u8 = next((s for s in streams if '.m3u8' in s), None)
        await browser.close()
        return f'mpv --referrer="https://www.miruro.bz/" --user-agent="Mozilla/5.0" "{m3u8}"' if m3u8 else None

async def main():
    query = input("Enter anime name to search: ")
    results = await search_miruro_playwright(query)
    if not results:
        print("No results found.")
        return

    for i, res in enumerate(results):
        print(f"[{i}] {res['title']}")
    
    idx = int(input("Select index: "))
    watch_url = f"https://www.miruro.bz/watch/{results[idx]['id']}"
    print("Extracting stream...")
    cmd = await get_stream_command(watch_url)
    if cmd:
        print("\nRun this command to play:")
        print(cmd)
    else:
        print("Stream not found.")

if __name__ == '__main__':
    asyncio.run(main())
