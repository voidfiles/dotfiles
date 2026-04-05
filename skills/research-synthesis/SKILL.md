---
name: research-synthesis
description: Takes N sets of findings from parallel research workers and produces one deduplicated, attributed, thematically organized synthesis with confidence scores. Run after parallel-dispatch completes.
---

You are executing a research synthesis step. Your input is the merged dispatch output from `parallel-dispatch`. Your job is to transform per-worker finding lists into a unified, thematic synthesis where every claim is attributed, duplicates are handled correctly, contradictions are surfaced, and confidence is scored.

---

## Input

The dispatch results from `parallel-dispatch`, structured as:
- One finding set per sub-question
- Each finding: claim | source URL | source type | one-sentence source summary
- A gap/failure list for sub-questions with insufficient coverage

Do not begin synthesis until all worker results are present. If some results are marked `[INSUFFICIENT]`, proceed with what exists but flag the coverage gaps explicitly in the output.

---

## Step 1 — Deduplication

Identify claims that express the same assertion across multiple workers.

**Criteria for "same claim":**
- The core assertion is logically equivalent, even if phrased differently
- The claim refers to the same entities, relationships, and direction of effect
- Minor differences in quantification (e.g., "~40%" vs "between 35–45%") do not make claims different

**How to handle duplicates:**
- Do NOT discard duplicates silently
- Keep the claim once in the synthesis, but assign joint attribution: list all source URLs that support it
- Joint attribution strengthens confidence (see Step 5)

**What is NOT a duplicate:**
- Same topic, different claims (these may contradict — see Step 2)
- Same claim, different time periods or populations
- Same claim, different methodologies (keep both; methodology differences are relevant)

---

## Step 2 — Contradiction Detection

A contradiction exists when two or more sources make logically opposing assertions about the same subject under comparable conditions.

**How to identify contradictions:**
- Look for opposing directions of effect ("increases X" vs "decreases X" vs "no effect on X")
- Look for incompatible quantitative claims that cannot both be true
- Look for definitional disputes where sources use the same term to mean different things

**What to do with contradictions:**
- Do NOT resolve them by choosing one side
- Do NOT omit the minority view
- Flag explicitly using the label `[CONTESTED]`
- Present both claims with their respective sources
- Assess which is better supported using source quality criteria: peer-reviewed > preprint > web; more sources > fewer sources; primary data > secondary commentary
- If one side is clearly better supported, say so — but still present both

**What is NOT a contradiction:**
- Two claims about different populations or contexts that happen to differ
- A newer source superseding an older one on the same question (note the recency, do not flag as contested)
- One source being more specific than another (more specific does not negate general)

---

## Step 3 — Thematic Grouping

Organize findings by theme, not by worker or sub-question. Themes emerge from the content; do not impose them in advance.

To identify themes:
1. Read all findings across all workers
2. Group findings that address the same aspect of the question
3. Name each theme with a noun phrase that describes what the group is about (not "findings from worker 1")
4. A finding may belong to more than one theme — place it where it contributes most, with a cross-reference if relevant

Typical thematic structure for a complex question:
- 2–3 major themes (the things most sources address)
- 1–2 secondary themes (addressed by a subset of sources)
- 1 "contested / uncertain" section (contradictions and thin coverage)
- 1 "knowledge gaps" section (what the research did not find)

Do not create a theme for fewer than 2 independent findings. Orphan findings go into a "single-source observations" section.

---

## Step 4 — Attribution

Every claim in the synthesis must trace to at least one source URL. No exceptions.

Attribution format for each claim:
```
[Claim text.] [URL1, URL2] [confidence tag]
```

If a claim comes from multiple sources (deduplicated), list all URLs. If a claim comes from a single source, list that URL and apply the appropriate confidence tag.

Do not paraphrase in ways that merge two different claims into one. Keep claims atomic enough that each URL can be said to directly support that specific claim.

---

## Step 5 — Confidence Scoring

Assign one of three confidence tags to each claim:

| Tag | Criteria |
|-----|----------|
| `[HIGH]` | 3 or more genuinely independent sources agree on the claim. Sources do not cite each other as primary evidence. Sources represent at least 2 different source types (e.g., peer-reviewed + structured data). |
| `[MEDIUM]` | Exactly 2 independent sources agree, OR 3+ sources agree but they are all of the same type or may share a common upstream source. |
| `[LOW]` | Only 1 source found for this claim, OR sources found may not be independent (one cites the other as primary evidence, or both derive from the same underlying study or report). |

"Independent" means: the sources conducted separate investigations or analyses and reached the same conclusion through different evidence paths. Two news articles citing the same press release are NOT independent. Two academic papers using different datasets that reach the same conclusion ARE independent.

**Source independence caveat for HIGH confidence:** HIGH confidence requires ≥3 sources that are provably independent — meaning they do not cite each other and do not derive from the same original source. URL diversity is not sufficient: 10 different news sites all reporting on the same single study are not independent. If you cannot verify independence — e.g., sources were retrieved but their citation relationships are not visible — cap the confidence at MEDIUM regardless of source count.

---

## Output Format

```
SYNTHESIS
=========
Source sub-questions: [list the sub-questions that fed this synthesis]
Coverage gaps: [list sub-questions that returned insufficient results, if any]

THEME 1: [theme name]
---------------------
- [claim] [URL1, URL2] [HIGH/MEDIUM/LOW]
- [claim] [URL1] [LOW]
- [CONTESTED] [claim A] [URL1] vs. [claim B] [URL2] — [one sentence on which is better supported and why]

THEME 2: [theme name]
---------------------
- [claim] [URL1, URL2, URL3] [HIGH]
...

SINGLE-SOURCE OBSERVATIONS
--------------------------
- [claim] [URL1] [LOW] — note: single source, treat as preliminary

KNOWLEDGE GAPS
--------------
- [what the research did not find, and why this matters]
- [sub-questions with [INSUFFICIENT] status]

SYNTHESIS SUMMARY
-----------------
[2–4 sentence executive summary of the overall answer, incorporating the highest-confidence findings and flagging the most significant contested areas.]
```

This output is the direct input to `claim-verification` for any claims flagged `[LOW]` or `[CONTESTED]` that are critical to the final answer.
