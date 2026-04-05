---
name: crawl4ai-crawl
description: Deep-crawl an entire site or site section, following links up to a configurable depth, and return markdown content for every page found.
---

# Crawl4AI — Crawl

Bulk-extract content from a website by following links. Returns a list of `CrawlResult` objects, one per page. Runs locally — no API key required.

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
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.deep_crawling.filters import URLPatternFilter, FilterChain

async def crawl_site(start_url: str) -> list:
    # Filter to a specific section (e.g., /docs/)
    filter_chain = FilterChain([
        URLPatternFilter(patterns=["*docs*"]),
    ])

    strategy = BFSDeepCrawlStrategy(
        max_depth=3,
        max_pages=50,
        include_external=False,
        filter_chain=filter_chain,
    )

    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        deep_crawl_strategy=strategy,
        stream=False,  # collect all results before returning
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun(url=start_url, config=run_config)

    # results is a list of CrawlResult objects
    successful = [r for r in results if r.success]
    print(f"Crawled {len(successful)} pages successfully")
    return successful

async def main():
    pages = await crawl_site("https://docs.example.com")
    for page in pages:
        print(page.url, "—", len(page.markdown.raw_markdown), "chars")

if __name__ == "__main__":
    asyncio.run(main())
```

### Streaming results as they arrive

```python
run_config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    deep_crawl_strategy=strategy,
    stream=True,  # yield results one by one
)

async with AsyncWebCrawler(config=browser_config) as crawler:
    async for result in await crawler.arun(url=start_url, config=run_config):
        if result.success:
            print(f"Got: {result.url}")
```

### Include/exclude patterns

```python
from crawl4ai.deep_crawling.filters import URLPatternFilter, FilterChain

# Only crawl /docs/ and /guides/, skip /blog/
filter_chain = FilterChain([
    URLPatternFilter(patterns=["*docs*", "*guides*"]),
])

# If you want to block specific patterns, chain a second filter with negation
# or scope the start URL to a sub-path directly.
```

## Key parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `BFSDeepCrawlStrategy(max_depth)` | int | — | Link levels to follow beyond the start URL |
| `BFSDeepCrawlStrategy(max_pages)` | int | unlimited | Hard cap on total pages crawled — **always set this explicitly**; no default is safe for production (an unconstrained crawl on a large site can run indefinitely) |
| `BFSDeepCrawlStrategy(include_external)` | bool | `False` | Follow links to other domains |
| `BFSDeepCrawlStrategy(filter_chain)` | FilterChain | `None` | URL filters to restrict which pages are visited |
| `BFSDeepCrawlStrategy(score_threshold)` | float | `0.0` | Minimum URL relevance score (0.0–1.0) |
| `URLPatternFilter(patterns)` | list[str] | — | Wildcard patterns URLs must match (e.g., `["*docs*"]`) — **warning: glob matching is greedy**; `*docs*` will also match `/redirects/docs-legacy/`, `/undocumented/`, etc. Prefer scoping the start URL to a sub-path (e.g., `https://example.com/docs/`) rather than relying solely on pattern filtering. |
| `CrawlerRunConfig(stream)` | bool | `False` | `True` = yield results as they arrive; `False` = return list |
| `CrawlerRunConfig(cache_mode)` | CacheMode | `ENABLED` | `BYPASS` forces fresh fetches |

## Result fields (per CrawlResult)

| Field | Type | Contents |
|-------|------|----------|
| `result.url` | str | The URL that was crawled |
| `result.success` | bool | `True` if page was fetched and parsed |
| `result.status_code` | int | HTTP response code |
| `result.error_message` | str | Error description if `success=False` |
| `result.markdown.raw_markdown` | str | Full page markdown |
| `result.markdown.fit_markdown` | str | Filtered, lower-noise markdown |
| `result.html` | str | Raw HTML |
| `result.links` | dict | `{"internal": [...], "external": [...]}` |
| `result.media` | dict | Images, videos, audio found on the page |

## When to use vs. alternatives

| Situation | Use |
|-----------|-----|
| Need content from many pages on a site | **crawl4ai-crawl** (this skill) |
| Single URL only | crawl4ai-scrape |
| Only need URLs, not page content | crawl4ai-map (faster — skips content extraction) |
| Need structured JSON from crawled pages | crawl4ai-extract |

**Tip:** Scope the crawl with `URLPatternFilter` to a docs section or path prefix — crawling a full site unconstrained is slow and usually unnecessary. Use `crawl4ai-map` first to understand site structure before committing to a full crawl.
