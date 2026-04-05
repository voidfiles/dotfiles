---
name: crawl4ai-extract
description: Extract structured JSON from a webpage using an LLM and a Pydantic schema, returning typed objects instead of raw markdown.
---

# Crawl4AI — Extract

Scrape a URL and use an LLM to extract structured data matching a Pydantic schema. Returns parsed JSON. Use this when you need specific fields (title, price, author, etc.) rather than full markdown.

## Setup

```bash
# One-time: download browser binaries (Playwright)
uvx --from crawl4ai python -m crawl4ai.install
```

Run the script with:

```bash
uv run --with crawl4ai --with pydantic python your_script.py
```

Set your LLM provider API key as an environment variable:
```bash
export OPENAI_API_KEY="sk-..."
# or
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Usage

```python
import asyncio
import json
import os
from typing import List
from pydantic import BaseModel, Field
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    LLMConfig,
    LLMExtractionStrategy,
)

# Define the schema for what you want to extract
class Article(BaseModel):
    title: str
    author: str = Field(default="Unknown")
    summary: str = Field(description="2-3 sentence summary of the article")
    key_points: List[str] = Field(description="Main takeaways as bullet points")
    published_date: str = Field(default="")

async def extract_article(url: str) -> Article:
    llm_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider="openai/gpt-4o-mini",
            api_token=os.getenv("OPENAI_API_KEY"),
        ),
        schema=Article.model_json_schema(),
        extraction_type="schema",
        instruction=(
            "Extract the article's title, author, a 2-3 sentence summary, "
            "key takeaway points, and publication date."
        ),
        input_format="markdown",        # feed markdown to the LLM
        chunk_token_threshold=1000,     # split long pages into chunks
        overlap_rate=0.1,
        apply_chunking=True,
        extra_args={"temperature": 0.0, "max_tokens": 1000},
        verbose=False,
    )

    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=llm_strategy,
    )
    browser_config = BrowserConfig(headless=True)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)

    if not result.success:
        raise RuntimeError(f"Crawl failed for {url}: {result.error_message}")

    data = json.loads(result.extracted_content)
    # extracted_content may be a list (one item per chunk) — take first non-empty
    if isinstance(data, list):
        data = next((item for item in data if item), data[0])

    return Article(**data)

async def main():
    article = await extract_article("https://example.com/blog/some-post")
    print("Title:", article.title)
    print("Author:", article.author)
    print("Summary:", article.summary)
    print("Key points:")
    for point in article.key_points:
        print(" -", point)

if __name__ == "__main__":
    asyncio.run(main())
```

### Using Anthropic instead of OpenAI

```python
llm_strategy = LLMExtractionStrategy(
    llm_config=LLMConfig(
        provider="anthropic/claude-3-5-haiku-20241022",
        api_token=os.getenv("ANTHROPIC_API_KEY"),
    ),
    schema=Article.model_json_schema(),
    extraction_type="schema",
    instruction="Extract the article metadata as specified in the schema.",
    input_format="markdown",
)
```

### Extracting a list of items (e.g., product listings)

```python
class Product(BaseModel):
    name: str
    price: str
    description: str = ""

class ProductList(BaseModel):
    products: List[Product]

llm_strategy = LLMExtractionStrategy(
    llm_config=LLMConfig(
        provider="openai/gpt-4o-mini",
        api_token=os.getenv("OPENAI_API_KEY"),
    ),
    schema=ProductList.model_json_schema(),
    extraction_type="schema",
    instruction="Extract all products listed on this page with their names, prices, and descriptions.",
    input_format="markdown",
)
```

## Key parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `LLMConfig(provider)` | str | Provider/model string: `"openai/gpt-4o-mini"`, `"anthropic/claude-3-5-haiku-20241022"`, `"ollama/llama2"` |
| `LLMConfig(api_token)` | str | API key for the provider (read from env var) |
| `LLMExtractionStrategy(schema)` | dict | Pydantic model's JSON schema via `MyModel.model_json_schema()` |
| `LLMExtractionStrategy(extraction_type)` | str | `"schema"` for structured output; `"block"` for freeform |
| `LLMExtractionStrategy(instruction)` | str | Natural-language guidance for the LLM |
| `LLMExtractionStrategy(input_format)` | str | `"markdown"` (recommended), `"html"`, or `"fit_markdown"` |
| `LLMExtractionStrategy(chunk_token_threshold)` | int | Split pages longer than N tokens into chunks |
| `LLMExtractionStrategy(overlap_rate)` | float | Overlap between chunks (0.0–0.3); helps with context at boundaries |
| `LLMExtractionStrategy(apply_chunking)` | bool | Enable/disable chunking; set `False` for short pages |
| `LLMExtractionStrategy(extra_args)` | dict | Pass `{"temperature": 0.0, "max_tokens": 800}` to the LLM |

## Result fields

| Field | Type | Contents |
|-------|------|----------|
| `result.success` | bool | `True` if crawl completed |
| `result.error_message` | str | Error description if `success=False` |
| `result.extracted_content` | str | JSON string of extracted data (parse with `json.loads()`) |
| `result.markdown` | object | Raw markdown (available but not needed for extraction) |
| `llm_strategy.usages` | list | Token counts per chunk |
| `llm_strategy.show_usage()` | method | Print total token consumption |

## Provider string reference

| Provider | String format | Env var |
|----------|--------------|---------|
| OpenAI GPT-4o mini | `"openai/gpt-4o-mini"` | `OPENAI_API_KEY` |
| OpenAI GPT-4o | `"openai/gpt-4o"` | `OPENAI_API_KEY` |
| Anthropic Claude Haiku | `"anthropic/claude-3-5-haiku-20241022"` | `ANTHROPIC_API_KEY` |
| Anthropic Claude Sonnet | `"anthropic/claude-sonnet-4-5"` | `ANTHROPIC_API_KEY` |
| Ollama (local) | `"ollama/llama2"` | none needed |

## Output Handling Caveats

**Chunk boundary data loss and duplication.** When extracting lists of items across a long page, the LLM extraction runs per-chunk and results are merged afterward. Items that appear near chunk boundaries may be duplicated (extracted by both surrounding chunks) or dropped (split across chunks in a way neither chunk can fully resolve). When precision matters — e.g., extracting a product catalog or a list of speakers — verify the total item count against an expected range and deduplicate on a stable field (e.g., `name`, `id`, `url`).

**LLM will fabricate values for missing fields.** Fields not present in the source HTML will be invented by the LLM to satisfy the schema, rather than left blank. To prevent silent fabrication, mark any field that may not always appear in the source as `Optional[str] = None` in your Pydantic model. Required (non-Optional) fields will receive a plausible-sounding fabricated value if absent — this is a known behavior, not a bug.

---

## When to use vs. alternatives

| Situation | Use |
|-----------|-----|
| Need specific fields as structured JSON | **crawl4ai-extract** (this skill) |
| Need full page text as markdown | crawl4ai-scrape (no LLM cost) |
| Need content from many pages | crawl4ai-crawl + loop over pages |
| Only need to discover which URLs exist | crawl4ai-map |

**Tip:** For simple single-page extractions, `crawl4ai-scrape` followed by manual parsing is cheaper and faster. Use `crawl4ai-extract` when the page structure is complex or inconsistent enough that you need an LLM to reliably pull out the right fields. Call `llm_strategy.show_usage()` after runs to track token costs.
