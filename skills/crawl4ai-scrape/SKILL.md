---
name: crawl4ai-scrape
description: Fetch a single URL and return clean markdown using an async headless browser, handling JS-rendered pages without external API costs.
---

# Crawl4AI — Scrape

Scrape one URL and return clean markdown. Handles static pages and JavaScript-rendered SPAs. Runs locally — no API key required.

## Setup

```bash
# One-time: download browser binaries (Playwright)
uvx --from crawl4ai python -m crawl4ai.install
```

Run the script with:

```bash
uv run --with crawl4ai python your_script.py
```

## Usage

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def scrape_url(url: str) -> str:
    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)

    if not result.success:
        raise RuntimeError(f"Scrape failed for {url}: {result.error_message}")

    return result.markdown

async def main():
    markdown = await scrape_url("https://example.com")
    print(markdown[:500])

if __name__ == "__main__":
    asyncio.run(main())
```

### With content filtering (cleaner output)

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def scrape_clean(url: str) -> str:
    md_generator = DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(threshold=0.4, threshold_type="fixed")
    )
    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=md_generator,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)

    if not result.success:
        raise RuntimeError(f"Scrape failed for {url}: {result.error_message}")

    # fit_markdown is the filtered, higher-signal version
    return result.markdown.fit_markdown
```

## Key parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `BrowserConfig(headless)` | bool | `True` | Run browser without UI |
| `BrowserConfig(java_script_enabled)` | bool | `True` | Enable JS rendering |
| `CrawlerRunConfig(cache_mode)` | CacheMode | `ENABLED` | `BYPASS` forces a fresh fetch |
| `CrawlerRunConfig(word_count_threshold)` | int | `10` | Min words per content block to keep |
| `CrawlerRunConfig(excluded_tags)` | list[str] | `[]` | HTML tags to strip (e.g., `["nav","footer"]`) |
| `CrawlerRunConfig(exclude_external_links)` | bool | `False` | Remove external links from output |
| `CrawlerRunConfig(remove_overlay_elements)` | bool | `False` | Strip popups/cookie banners |
| `CrawlerRunConfig(process_iframes)` | bool | `False` | Include iframe content |
| `CrawlerRunConfig(js_code)` | list[str] | `[]` | JavaScript to execute before scraping |

## Result fields

| Field | Type | Contents |
|-------|------|----------|
| `result.success` | bool | `True` if crawl completed without error |
| `result.status_code` | int | HTTP response code |
| `result.error_message` | str | Error description if `success=False` |
| `result.markdown` | object | Markdown result object (see below) |
| `result.markdown.raw_markdown` | str | Full markdown of the page |
| `result.markdown.fit_markdown` | str | Filtered markdown (lower noise, higher signal) |
| `result.html` | str | Raw HTML |
| `result.cleaned_html` | str | Cleaned HTML |
| `result.links` | dict | `{"internal": [...], "external": [...]}` |
| `result.media` | dict | `{"images": [...], "videos": [...]}` |

## Known Limitations

1. **Bot-protected pages silently return incomplete content.** `result.success=True` does not mean the content is real — it only means the request completed without a network error. Bot protection (Cloudflare, reCAPTCHA, login walls) often returns a challenge page or empty body while still returning HTTP 200. Always verify output length and content make sense for the page you expected to scrape.

2. **Each call spins up a headless browser.** Crawl4AI uses Playwright under the hood — not suitable for high-volume scraping (hundreds of pages per minute). For that scale, consider a dedicated scraping service or rate-limited queue.

3. **Short output is a signal, not a success.** If `result.markdown` contains fewer than ~50 words for a page you expect to have substantive content, the page likely has bot protection or requires authentication. Do not treat short output as valid scraped content — investigate before proceeding.

---

## When to use vs. alternatives

| Situation | Use |
|-----------|-----|
| Single URL, want markdown | **crawl4ai-scrape** (this skill) |
| Need URLs from many pages on a site | crawl4ai-crawl |
| Only need to discover URLs, not content | crawl4ai-map |
| Need structured JSON from a page | crawl4ai-extract |

**Tip:** `result.markdown` is the raw full-page markdown. `result.markdown.fit_markdown` runs a pruning filter to strip boilerplate — prefer it when passing content to an LLM.
