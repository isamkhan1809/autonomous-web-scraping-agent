import asyncio
import base64
from playwright.async_api import async_playwright, Browser, Page, Playwright


class BrowserController:
    def __init__(self):
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._page: Page | None = None

    async def init(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        context = await self._browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )
        self._page = await context.new_page()

    async def navigate(self, url: str) -> dict:
        try:
            await self._page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await self._page.wait_for_timeout(1500)
            title = await self._page.title()
            return {"url": self._page.url, "title": title, "success": True}
        except Exception as e:
            return {"url": url, "title": "", "success": False, "error": str(e)}

    async def get_page_text(self) -> str:
        try:
            text = await self._page.evaluate("() => document.body.innerText")
            return text[:5000] if text else ""
        except Exception:
            return ""

    async def get_page_links(self) -> list[dict]:
        try:
            links = await self._page.evaluate(
                """() => {
                    const anchors = Array.from(document.querySelectorAll('a'));
                    return anchors
                        .filter(a => a.href && a.href.startsWith('http'))
                        .map(a => ({text: (a.innerText || a.textContent || '').trim(), href: a.href}))
                        .filter(l => l.text.length > 0)
                        .slice(0, 50);
                }"""
            )
            return links
        except Exception:
            return []

    async def click(self, selector: str) -> dict:
        try:
            await self._page.click(selector, timeout=10000)
            await self._page.wait_for_timeout(1000)
            return {"success": True, "error": None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def fill_input(self, selector: str, value: str) -> dict:
        try:
            await self._page.fill(selector, value)
            return {"success": True, "error": None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def search_google(self, query: str) -> list[dict]:
        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&hl=en"
            await self._page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            await self._page.wait_for_timeout(2000)

            results = await self._page.evaluate(
                """() => {
                    const items = [];
                    // Try standard result containers
                    const divs = document.querySelectorAll('div.g, div[data-sokoban-container], div.tF2Cxc');
                    divs.forEach(div => {
                        const titleEl = div.querySelector('h3');
                        const linkEl = div.querySelector('a[href]');
                        const snippetEl = div.querySelector('div.VwiC3b, span.aCOpRe, div[data-sncf]');
                        if (titleEl && linkEl) {
                            const href = linkEl.href;
                            if (href && href.startsWith('http') && !href.includes('google.com')) {
                                items.push({
                                    title: titleEl.innerText.trim(),
                                    url: href,
                                    snippet: snippetEl ? snippetEl.innerText.trim().slice(0, 200) : ''
                                });
                            }
                        }
                    });
                    // Deduplicate by URL
                    const seen = new Set();
                    return items.filter(i => {
                        if (seen.has(i.url)) return false;
                        seen.add(i.url);
                        return true;
                    }).slice(0, 10);
                }"""
            )

            if not results:
                # Fallback: grab all external links with text
                links = await self._page.evaluate(
                    """() => {
                        return Array.from(document.querySelectorAll('a[href]'))
                            .filter(a => a.href.startsWith('http') && !a.href.includes('google'))
                            .map(a => ({title: (a.innerText||'').trim(), url: a.href, snippet: ''}))
                            .filter(a => a.title.length > 3)
                            .slice(0, 10);
                    }"""
                )
                return links

            return results
        except Exception as e:
            return [{"title": "Error", "url": "", "snippet": str(e)}]

    async def screenshot(self) -> str:
        try:
            data = await self._page.screenshot(type="png", full_page=False)
            return base64.b64encode(data).decode("utf-8")
        except Exception:
            return ""

    async def close(self):
        try:
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception:
            pass
