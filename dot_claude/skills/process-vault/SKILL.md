---
name: process-vault
description: Run the full vault processing pipeline (highlight, extract, review, apply, archive). Use weekly.
argument-hint: "[content-types] [--days-back N] [--batch]"
---
# Process Vault

Orchestrates the full vault processing pipeline. This is the primary entry point for weekly vault maintenance.

## Pipeline

```
highlight → extract → review → apply → archive
```

Each stage checks frontmatter state before processing, making the pipeline idempotent and resumable.

## Usage

```bash
# Process all content types (interactive)
python .claude/skills/process-inbox/scripts/process_inbox.py

# Process specific types
python .claude/skills/process-inbox/scripts/process_inbox.py articles
python .claude/skills/process-inbox/scripts/process_inbox.py daily,meetings

# Auto-approve HIGH relevance suggestions
python .claude/skills/process-inbox/scripts/process_inbox.py --batch

# Auto-approve ALL suggestions
python .claude/skills/process-inbox/scripts/process_inbox.py --batch-all

# Process older items (articles ignore date filter by default)
python .claude/skills/process-inbox/scripts/process_inbox.py --days-back 365
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `content_types` | Comma-separated types (articles,daily,meetings,assets) | all |
| `--vault-root` | Obsidian vault root path | auto-detect |
| `--max-concurrent` | Max concurrent operations | 5 |
| `--days-back` | Days back to search for daily/meetings | 15 |
| `--batch` | Auto-approve HIGH relevance suggestions | off |
| `--batch-all` | Auto-approve ALL suggestions | off |

## Pipeline Stages

### Stage 1: Highlighting (Concurrent)
- Runs `process-inbox-highlight` on each item
- Uses semaphore to control concurrency
- Items processed in parallel up to `--max-concurrent` limit

### Stage 2: Extraction (Sequential)
- Runs `process-inbox-extract` on highlighted items
- Generates a YAML suggestions file

### Stage 3: Review (Interactive or Batch)
- Interactive: present each suggestion for approval/rejection
- `--batch`: auto-approve HIGH relevance, skip others
- `--batch-all`: auto-approve everything

### Stage 4: Apply
- Creates integration notes from approved YAML suggestions
- Updates source frontmatter (`extracted: true`)
- Appends to `_meta/processing-log.md`

### Stage 5: Archiving (Concurrent)
- Runs `process-inbox-archive` on extracted items
- Only articles and assets are archived
- Uses `move-file` skill to maintain wiki link integrity

## State Machine

```
  inbox → highlighted → extracted → processed/archived
           (Stage 1)    (Stage 2-4)    (Stage 5)
```

Frontmatter is the single source of truth for item state:
- `highlighted: true` → skip highlighting
- `extracted: true` → skip extraction
- `processed: true` → skip archiving

## Processing Ledger

All operations are logged to `_meta/processing-log.md` for auditability.

## Content Types

| Type | Inbox Location | Archives? |
|------|----------------|-----------|
| articles | `Clippings/*.md` | Yes, to `archive/Clippings/` |
| daily | `daily/{year}/{month}/{day}/` | No |
| meetings | `Meetings/{year}/{month}/{day}/` | No |
| assets | `assets/*/summary.md` | Partial |

## Notes

- Articles have no date filter (all unprocessed articles are included)
- Daily/meetings use `--days-back` filter (default 15 days)
- Individual item failures don't stop the pipeline
- Safe to re-run; already-processed items are skipped
