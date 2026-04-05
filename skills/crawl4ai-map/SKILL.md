<!-- Source: synthesized from firecrawl-map | Adapted for: Crawl4AI -->

---
name: crawl4ai-map
description: Discover and collect all URLs on a site without extracting page content — faster than a full crawl, used to locate target pages before scraping.
---

# Crawl4AI — Map

Discover URLs across a site by following links, but skip content extraction entirely. Returns a flat list of URLs. Use this to find which pages exist before deciding what to scrape.

## Setup

```bash
pip install crawl4ai
python -m crawl4ai.install  # downloads browser binaries (Playwright)
```

## Usage

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.deep_crawling.filters import URLPatternFilter, FilterChain

async def map_site(start_url: str, pattern: str | None = None) -> list[str]:
    filters = []
    if pattern:
        filters.append(URLPatternFilter(patterns=[pattern]))

    strategy = BFSDeepCrawlStrategy(
        max_depth=3,
        max_pages=200,
        include_external=False,
        filter_chain=FilterChain(filters) if filters else None,
    )

    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        deep_crawl_strategy=strategy,
        # Skip content processing — we only want URLs
        word_count_threshold=0,
        stream=False,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun(url=start_url, config=run_config)

    return [r.url for r in results if r.success]

async def main():
    # Example: find all authentication-related pages in docs
    urls = await map_site("https://docs.example.com", pattern="*auth*")
    print(f"Found {len(urls)} matching URLs:")
    for url in urls:
        print(" ", url)

if __name__ == "__main__":
    asyncio.run(main())
```

### Map → scrape pattern (common workflow)

```python
async def map_then_scrape(start_url: str, search_pattern: str) -> list[str]:
    """Discover relevant URLs, then scrape only the ones you need."""
    # Step 1: map to find URLs
    urls = await map_site(start_url, pattern=search_pattern)
    print(f"Discovered {len(urls)} pages matching '{search_pattern}'")

    # Step 2: scrape only the relevant ones
    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
    results = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url in urls:
            result = await crawler.arun(url=url, config=run_config)
            if result.success:
                results.append(result.markdown.raw_markdown)

    return results
```

## Key parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `BFSDeepCrawlStrategy(max_depth)` | int | — | How many link levels to follow |
| `BFSDeepCrawlStrategy(max_pages)` | int | unlimited | Max URLs to collect |
| `BFSDeepCrawlStrategy(include_external)` | bool | `False` | Follow off-domain links |
| `URLPatternFilter(patterns)` | list[str] | — | Wildcard patterns to restrict which URLs are visited (e.g., `["*docs*"]`) |
| `CrawlerRunConfig(word_count_threshold)` | int | `10` | Set to `0` to skip content filtering and make URL discovery faster |
| `CrawlerRunConfig(stream)` | bool | `False` | Stream results as they arrive |

## Result fields

Map returns `[r.url for r in results if r.success]` — a plain list of URL strings.

For reference, each raw `CrawlResult` also has:

| Field | Type | Contents |
|-------|------|----------|
| `result.url` | str | The discovered URL |
| `result.success` | bool | Whether the page responded successfully |
| `result.status_code` | int | HTTP response code |
| `result.error_message` | str | Error if `success=False` |

## When to use vs. alternatives

| Situation | Use |
|-----------|-----|
| Find which pages exist on a site | **crawl4ai-map** (this skill) |
| Need page content too | crawl4ai-crawl (same depth traversal, extracts content) |
| Single known URL, need its content | crawl4ai-scrape |
| Need structured JSON from pages | crawl4ai-extract |

**crawl4ai-map is faster than crawl4ai-crawl** because it sets `word_count_threshold=0` to skip content processing. Use it when you need to locate the right pages before scraping, or when you want to survey site structure without downloading full content.

**Common pattern:** `map --search "*auth*"` → found `/docs/api/authentication` → pass that URL to `crawl4ai-scrape`.

> **Prefer sitemap.xml when available.** For sites that publish a sitemap, fetching `https://domain.com/sitemap.xml` directly is faster and more reliable than browser-based map crawling — it returns a structured XML index without spinning up a headless browser. Use crawl4ai-map only when no sitemap is available or when the sitemap is incomplete/outdated.
