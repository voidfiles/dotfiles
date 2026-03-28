---
argument-hint: [content-types or empty for all, e.g., "daily,meetings" or "articles"]
description: "[DEPRECATED] Use /process-vault instead. Orchestrates the full inbox processing pipeline."
name: process-inbox
version: 1.0.0
---
# Process Inbox - Concurrent Pipeline

> **DEPRECATED**: This skill is superseded by `/process-vault`. Use that instead.
> The underlying Python script (`process_inbox.py`) is shared and still maintained.

This skill provides a Python script for running the inbox processing pipeline with maximum concurrency.

## Script Location

```
.claude/skills/process-inbox/scripts/process_inbox.py
```

## Usage

```bash
# Process all content types
python .claude/skills/process-inbox/scripts/process_inbox.py

# Process specific types
python .claude/skills/process-inbox/scripts/process_inbox.py articles
python .claude/skills/process-inbox/scripts/process_inbox.py daily,meetings

# With options
python .claude/skills/process-inbox/scripts/process_inbox.py --max-concurrent 10
python .claude/skills/process-inbox/scripts/process_inbox.py --days-back 30
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `content_types` | Comma-separated types (articles,daily,meetings,assets) | all |
| `--vault-root` | Obsidian vault root path | auto-detect |
| `--max-concurrent` | Max concurrent operations | 5 |
| `--days-back` | Days back to search for items | 15 |

## Pipeline Stages

### Stage 1: Highlighting (Concurrent)
- Runs `process-inbox-highlight` skill on each item
- Uses semaphore to control concurrency
- Items processed in parallel up to `--max-concurrent` limit

### Stage 2: Extraction (Sequential)
- Runs `process-inbox-extract` skill on each item
- **Sequential** because it requires user confirmation
- Each item prompts for association decisions

### Stage 3: Archiving (Concurrent)
- Runs `process-inbox-archive` skill on each item
- Only articles and assets are archived
- Uses semaphore to control concurrency

## Content Types

| Type | Inbox Location | Archives? |
|------|----------------|-----------|
| articles | `Clippings/*.md` | Yes → `archive/Clippings/` |
| daily | `daily/{year}/{month}/{day}/` | No |
| meetings | `Meetings/{year}/{month}/{day}/` | No |
| assets | `assets/*/summary.md` | Partial |

## State Machine

```
inbox → highlighted → extracted → archived
         (Stage 1)     (Stage 2)   (Stage 3)
```

Each stage checks frontmatter state before processing:
- `highlighted: true` → skip highlighting
- `extracted: true` → skip extraction
- `processed: true` → skip archiving

## Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INBOX PROCESSING - 2026-01-22
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Articles: 12 items
  - Needs highlighting: 8
  - Needs extraction: 4
  - Needs archiving: 2

Daily: 5 items
  - Needs highlighting: 3
  - Needs extraction: 2

...

Continue with processing? (y/n):
```

## Requirements

- Python 3.10+
- `claude` CLI installed and available in PATH
- Obsidian vault with standard PARA structure

## Notes

### Concurrency Model
- Highlighting and archiving run concurrently (async)
- Extraction runs sequentially (interactive)
- Semaphore limits parallel operations to avoid overwhelming the system

### Error Handling
- Individual item failures don't stop the pipeline
- Errors are collected and reported at the end
- Item state is refreshed between stages

### Idempotency
- Safe to re-run; already-processed items are skipped
- State is tracked via frontmatter fields
