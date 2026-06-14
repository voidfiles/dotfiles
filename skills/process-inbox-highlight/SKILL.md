---
name: process-inbox-highlight
argument-hint: file path or folder, e.g., "Clippings/Article.md" or "projects/foo/research/"
description: Apply knowledge-focused Layer 1-2 progressive summarization using multi-method analysis. Knowledge = claims + evidence + insight. Three framed LLM passes (claims, evidence, insight) run in parallel, combined with TF-IDF and TextRank graph centrality scores, to select the highest-confidence passages. Use whenever the user wants to highlight, bold, progressively summarize, or extract the essence from research files, articles, vault notes, or any document where identifying claims and evidence matters. Strongly prefer this over the basic process-inbox-highlight skill for documents with structured arguments, research findings, or evidence-backed claims.
---

# process-inbox-highlight-v2

Knowledge-focused progressive summarization. Layer 1 bolds the highest-signal passages. Layer 2 highlights the absolute essence.

**Core insight:** Knowledge = claims + evidence + insight. Three framed LLM passes triangulated against structural scores (TF-IDF + TextRank) produce much higher-confidence selections than a single "what's important?" pass.

---

## Step-by-step workflow

### Step 1: Run the script

```bash
uv run scripts/knowledge_highlight.py \
  "<absolute-file-path>" \
  --vault-root "<obsidian vault root>"
```

The script handles everything autonomously:
- Reads the file and checks frontmatter (`highlighted: true` → skips unless `--force`)
- Runs three LLM frames (claims, evidence, insight) in parallel via `claude_code_sdk`
- Computes TF-IDF + TextRank structural scores
- Scores and ranks passages by convergence across frames + structural signals
- Applies `**bold**` for Layer 1 and `==**bold**==` for Layer 2
- Updates frontmatter with `highlighted: true` and `highlighted_date`

To re-process an already-highlighted file:

```bash
uv run scripts/knowledge_highlight.py "<path>" --vault-root "<root>" --force
```

To skip structural analysis (faster, LLM-only):

```bash
uv run scripts/knowledge_highlight.py "<path>" --vault-root "<root>" --fast
```

### Step 2: Report to the user

Tell the user:
- File processed (or skipped/failed, with reason)
- How many passages were bolded (Layer 1) and highlighted (Layer 2)

---

## Content type guidance

Detected automatically from the file path:

| Path contains | Type | Focus |
|---|---|---|
| `Clippings/` | article | Transferable knowledge, novel ideas, data |
| `daily/` | daily | Reflections, patterns, commitments |
| `Meetings/` | meeting | Decisions, commitments, open questions |
| `assets/` | asset | Core frameworks, central arguments |
| anything else | unknown | General knowledge extraction |

---

## Output format

- Layer 1: `**passage**`
- Layer 2: `==**passage**==`
- Frontmatter updated: `highlighted: true`, `highlighted_date: YYYY-MM-DD`

---

## Folder processing

If a folder path is given, pass the folder path directly — the script globs `**/*.md` and processes each file, skipping already-highlighted ones. A summary is printed at the end.

---

## Edge cases

**File too short:** Fewer than 3 content paragraphs → frontmatter updated with `highlighted: true`, logged as skipped.

**Assets:** The script automatically processes `summary.md` inside the asset folder if the path points to an asset directory.
