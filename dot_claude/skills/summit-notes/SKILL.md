---
name: summit-notes
description: Transform multi-day summit transcripts into conversation-centric summaries using LangGraph
argument-hint: [summit-folder-path]
allowed-tools:
  - Bash
  - Read
---

# Summit Notes (LangGraph Pipeline)

Transform a folder of meeting transcripts and notes from multi-day events (summits, onsites, conferences) into comprehensive, conversation-based documentation.

## Usage

```bash
/summit-notes meetings/2026/02/risk-staff-onsite/
```

Or via CLI:
```bash
uv run python -m src.cli summit-notes meetings/2026/02/risk-staff-onsite/
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--max-concurrent` | 5 | Max parallel claude processes |
| `--force` | false | Force rerun, ignore checkpoints |
| `--dry-run` | false | Preview without writing files |
| `--no-stream` | false | Disable streaming output |
| `--extraction-model` | sonnet | Model for conversation extraction |
| `--analysis-model` | haiku | Model for file/conversation analysis |
| `--synthesis-model` | opus | Model for final synthesis |

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: File Analysis                                    │
│ • Discover and classify all files in folder              │
│ • Parallel processing with haiku                         │
│ • Output: manifest.yaml                                  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ Step 2: Conversation Extraction                          │
│ • Full transcript analysis with large context model      │
│ • Identifies discrete conversations within transcripts   │
│ • Output: conversations.yaml                             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ Step 3: Conversation Processing                          │
│ • Generate rich summary for each conversation            │
│ • Parallel processing                                    │
│ • Output: conversations/*.md                             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ Step 4: Rich Summary                                     │
│ • Synthesize all conversations into summit summary       │
│ • High-quality model for synthesis                       │
│ • Output: summit_summary.md                              │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure Created

```
{summit_folder}/
├── manifest.yaml           # Step 1: File inventory & categorization
├── conversations.yaml      # Step 2: Conversation boundaries & metadata
├── conversations/          # Step 3: Individual conversation summaries
│   ├── conv_001_opening_welcome.md
│   ├── conv_002_strategy_discussion.md
│   └── ...
├── summit_summary.md            # Step 4: Rich comprehensive summary
└── .langgraph_checkpoint.json   # Checkpoint file (for resume)
```

## Resumability

The pipeline uses LangGraph checkpointing for automatic resume:

- **Interrupt at any time** with Ctrl+C
- **Re-run the same command** to resume from checkpoint
- **Use `--force`** to start fresh and ignore checkpoints

The checkpoint file (`.langgraph_checkpoint.json`) stores pipeline state.

## Idempotency

Each step checks for existing outputs:

| Step | Check | Skip Condition |
|------|-------|----------------|
| File Analysis | manifest.yaml checksums | Checksum unchanged |
| Conversation Extraction | conversations.yaml timestamp | Newer than transcripts |
| Conversation Processing | processing_status field | Status == "completed" |
| Rich Summary | summit_summary.md timestamp | Newer than conversation files |

## Model Configuration

| Step | Default Model | Rationale |
|------|---------------|-----------|
| File Analysis | haiku | Fast classification, simple task |
| Conversation Extraction | sonnet | Large context for full transcripts |
| Conversation Processing | haiku | Fast, many parallel calls |
| Rich Summary | opus | Quality synthesis |

## Example Output

### manifest.yaml
```yaml
version: "1.0"
summit_folder: "/path/to/summit"
created_at: "2026-02-05T17:32:48Z"
files:
  - path: "day1_transcript.md"
    type: "transcript"
    status: "analyzed"
    checksum: "sha256:a1b2c3..."
    metadata:
      speakers: ["Alex", "Sarah", "Mike"]
      line_count: 3500
```

### conversations.yaml
```yaml
version: "1.0"
extracted_at: "2026-02-05T18:15:00Z"
conversations:
  - id: "conv_001_opening_welcome"
    title: "Opening Welcome and Agenda Setting"
    source_file: "day1_transcript.md"
    start_line: 1
    end_line: 245
    primary_speakers: ["Alex", "Sarah"]
    mode: "information_sharing"
    resolution_status: "resolved"
    processing_status: "completed"
    output_file: "conversations/conv_001_opening_welcome.md"
```

### conversations/conv_001_opening_welcome.md
```yaml
---
id: "conv_001_opening_welcome"
title: "Opening Welcome and Agenda Setting"
source_file: "day1_transcript.md"
source_lines: "1-245"
speakers: ["Alex", "Sarah"]
mode: "information_sharing"
resolution_status: "resolved"
---

# Opening Welcome and Agenda Setting

## One-Liner
Alex welcomed attendees and outlined the three-day summit agenda.

## TL;DR
Alex opened the summit by welcoming attendees and reviewing the agenda...

## Narrative Summary
...
```

## Error Handling

- Files with errors are marked `status: error` in manifest.yaml
- Conversations that fail are marked `processing_status: error`
- Pipeline continues past individual failures
- Errors are logged and summarized at completion

## Quick Reference

```bash
# Basic run
/summit-notes meetings/2026/02/onsite/

# Force fresh run
/summit-notes meetings/2026/02/onsite/ --force

# Preview without writing
/summit-notes meetings/2026/02/onsite/ --dry-run

# Custom models
/summit-notes meetings/2026/02/onsite/ --synthesis-model opus
```
