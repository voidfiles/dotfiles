---
name: process-doc
description: Use when you want to process a PDF or EPUB file into a structured Obsidian vault asset with markdown conversion, chunking, and AI-generated summaries.
argument-hint: [path-to-pdf-or-epub]
---

# Process Doc

Convert a PDF or EPUB into a structured Obsidian asset with full markdown, smart chunks, and hierarchical summaries.

## Usage

```
/process-doc path/to/book.pdf
/process-doc ~/Downloads/paper.epub
```

## What It Does

Runs `.claude/scripts/commands/process_doc.py` through a 7-step pipeline:

1. **Workspace init** — creates temp dir with hash-based isolation
2. **Content extraction** — PDF via Datalab Marker API, EPUB via HTML parsing
3. **Structure extraction** — parses headers into `headers.md`
4. **Chapter level detection** — LLM determines which header level = chapters
5. **Intelligent chunking** — splits into `chunks/*.md` at chapter boundaries
6. **Metadata + canonicalize** — LLM extracts title/authors → `canonical_name`
7. **Summarization** — Haiku batch-summarizes chunks, Opus writes final summary

## Output Structure

```
assets/{canonical_name}/
├── {canonical_name}.pdf/.epub     ← original file
├── {canonical_name}.md            ← full markdown
├── summary.md                     ← Opus 4.5 high-level summary
├── chunk_summary.md               ← consolidated chunk summaries
├── images/                        ← extracted images
└── chunks/
    ├── 001_introduction.md
    ├── 002_chapter_name.md
    └── ...
```

Canonical name format: `title_author` (e.g., `deep_work_cal_newport`)

## Instructions

1. Resolve the input file path from `$ARGUMENTS`. If it's relative, resolve against the vault root or current directory.
2. Verify the file exists and is a `.pdf` or `.epub`.
3. Run the pipeline:

```bash
cd /Users/alex/Dropbox/obsidian/Alex3
uv run python .claude/scripts/commands/process_doc.py "$INPUT_FILE" --vault .
```

Add `--quiet` to suppress verbose output if the user prefers less noise.

4. On success, report:
   - The canonical asset name
   - The asset directory path
   - Number of chunks created
   - Whether summary was generated

## Reprocessing Steps

To re-run specific steps on an existing asset, use `--steps`:

```bash
uv run python .claude/scripts/commands/process_doc.py "$FILE" \
  --steps summarize \
  --force
```

Valid step names: `structure`, `chapter-level`, `chunks`, `metadata`, `finalize`, `summarize`

## Required Environment Variables

- `ANTHROPIC_API_KEY` — for LLM calls (chapter level, metadata, summaries)
- `DATALAB_API_KEY` — for PDF conversion (not needed for EPUBs)

Both should already be set in the environment. If not, tell the user.

## Notes

- The pipeline is **idempotent** — safe to re-run; each step checks for existing output
- Processing large PDFs takes several minutes due to OCR and batch summarization
- Assets land in `{vault}/assets/` — do not move them manually or wiki links break
