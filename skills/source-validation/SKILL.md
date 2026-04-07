---
name: source-validation
description: >-
  Audit a draft document's quotes, facts, and figures against its original source materials.
  Produces a validation report AND applies corrections directly to the draft.
  Use when the user says "fact check", "verify sources", "check quotes", "validate citations",
  "audit this document", "check this against sources", or any variation of comparing a draft
  to its reference materials. Also trigger when a user has a research report, article, or
  paper with citations and wants to confirm accuracy before publishing. This skill checks
  a document against LOCAL source files the user provides — it does NOT search the web
  for independent corroboration (use the fact-check skill for that instead).
---

# Source Validation & Fact-Checking

Audit every checkable claim in a draft document against provided source materials. Produce a validation report and apply corrections directly.

## When to Use

- A draft document cites sources and you need to verify accuracy before publishing
- Checking whether direct quotes match their original sources word-for-word
- Verifying that statistics, figures, and percentages are correctly transcribed
- Confirming that paraphrased claims accurately represent their sources
- Auditing attribution (correct author names, publication years, etc.)

**Not for**: verifying claims against the open web (use `fact-check`), literature reviews, or open-ended research.

## Inputs

The user provides:
1. **Draft document** — the file to validate (path specified by user)
2. **Source materials** — directory containing the original sources (path specified by user)

If the user doesn't specify a source path, ask for it.

## Status Definitions

| Code | Icon | Meaning |
|------|------|---------|
| VERIFIED | ✅ | Matches source exactly (quotes) or accurately (facts/figures/paraphrases) |
| MINOR_DISCREPANCY | ⚠️ | Small deviation that does not change meaning, implication, or magnitude |
| MATERIAL_ERROR | ❌ | Misquote, wrong number, incorrect fact, misattribution — changes meaning |
| NOT_FOUND | 🔍 | Cannot be located in the provided source materials |

### The MINOR vs MATERIAL Boundary

This is the most important judgment call. The test: **would a reasonable reader draw a materially different conclusion?**

**MINOR examples:**
- "revenue of $4.2 billion" when source says "$4.21 billion" (rounding)
- "extremely well received" when source says "very well received" (synonym preserving sentiment)
- Markdown formatting differences (asterisk vs underscore italics)

**MATERIAL examples:**
- "revenue of $4.2 billion" when source says "$2.4 billion" (transposed digits)
- "we will not raise prices" when source says "we will not raise prices this quarter" (omission changes scope)
- Wrong author name on a paper (readers cannot find the actual source)
- "policy achieved cost savings" when source says "failed to achieve cost savings" (inverted meaning)

## Procedure

### Phase 0: Source Inventory

Before checking any claims:

1. List every source referenced in the draft
2. For each, confirm whether a corresponding source file exists
3. Flag gaps immediately — claims from missing sources get 🔍 NOT_FOUND

### Phase 1: Identify Checkable Items

Scan the draft and tag every checkable item with a unique ID:

- **Q-N** — Direct quotes (text in quotation marks or blockquotes attributed to a source)
- **P-N** — Paraphrased claims (assertions attributed to or derived from a named source)
- **F-N** — Facts (events, dates, proper nouns, titles, roles tied to a source)
- **FIG-N** — Figures (numbers, percentages, dollar amounts, sample sizes, statistics)

The goal is exhaustive coverage. Every quote, every number, every attribution.

### Phase 2: Validate

For complex documents with many sources, use parallel agents — group claims by source and dispatch one agent per source group. Each agent reads the relevant source files and checks all claims against them.

For each item:

1. **Locate** the corresponding passage in the source file
2. **Compare** word-for-word for quotes; numerical accuracy for figures; faithful representation for paraphrases
3. **Reason** before classifying — write a brief note on what differs (if anything) and whether the difference changes meaning
4. **Classify** using the status codes above
5. **Assign confidence**: HIGH (binary match/mismatch), MEDIUM (requires interpretation), LOW (ambiguous source)

### Phase 3: Write Validation Report

Produce a `validation-report.md` as a sibling to the draft, containing:

**Summary table** — counts of each status type and overall accuracy score

**Source inventory** — which sources were available, which were missing

**Material errors section** — each error with location, what the draft says, what the source says, and the correction

**Minor discrepancies section** — same format, grouped for review

**Not Found section** — claims that couldn't be verified

**Item-by-item detail** — table with ID, type, source, status, confidence for every checked item

**Flagged concerns** — broader patterns (e.g., systematic author misattribution, conflated sources, vendor bias)

### Phase 4: Apply Corrections

After writing the report, apply fixes directly to the draft document:

- **Material errors**: fix to match source materials
- **Minor discrepancies**: fix to match source materials
- **Not Found items**: the user's instructions determine handling (remove as cited source, reframe as notional, flag inline, etc.) — ask if not specified

Preserve the original tone, style, and structure. Only change what is factually necessary.

## Parallelization Strategy

For documents with 10+ sources, dispatch parallel verification agents grouped by report section or source cluster. Each agent:
- Reads the relevant source files
- Checks all claims attributed to those sources
- Returns structured findings

Then synthesize all agent findings into the unified validation report.

## Common Error Patterns

Watch for these recurring issues — they're the most frequent sources of material error in research documents:

1. **Author misattribution** — wrong author name on a paper (often from metadata errors at capture time, not the actual paper)
2. **Source conflation** — merging findings from separate studies into a single attribution
3. **Scope narrowing** — paraphrasing that removes important qualifiers ("this quarter", "in the verbatim scenario", "2 of 669 respondents")
4. **Constructed statistics** — the report performs a calculation and presents it as if it came from the source
5. **Quote splicing** — combining passages from different sections of a source into one continuous quote
6. **Strength inflation** — "dipped" becomes "collapsed"; a minority finding becomes a "systematic" pattern

## Rules

- Only verify against provided source materials — do NOT use world knowledge
- Missing sources mean 🔍 NOT_FOUND for all claims from that source
- Be exhaustive — do not skip small items
- Over-report rather than under-report
- Write the reasoning note before assigning a status
- When in doubt, flag it
