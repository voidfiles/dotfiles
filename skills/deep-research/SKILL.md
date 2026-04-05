<!-- Source: synthesized from deep-research-skill.md, deep-research-methodology.md, deep-research-quality-gates.md, feynman-deep-research-workflow.md, gpt-researcher-prompts.md, ecc-deep-research.md -->

---
name: deep-research
description: Conducts comprehensive, multi-source research with cross-verification, source credibility scoring, and structured synthesis. Produces citation-backed reports through an 8-phase pipeline. Triggers on "deep research", "comprehensive analysis", "compare X vs Y", "analyze trends", "state of the art", "research report", "deep dive", or "investigate". NOT for simple lookups, single-source questions, debugging, or queries answerable in 1-2 searches.
---

# Deep Research

## Core Purpose

Deliver citation-backed, verified research reports through a structured pipeline with source credibility scoring, evidence persistence, and progressive synthesis.

**Autonomy Principle:** Operate independently. Infer scope and audience from context. Only stop for critical errors or fundamentally ambiguous queries. Never ask clarifying questions unless the query is incomprehensible.

---

## Decision Tree

```
Request received
├── Simple factual lookup?          → STOP: answer directly
├── Debugging or code question?     → STOP: use standard tools
├── Single-source sufficient?       → STOP: answer directly
└── Complex analysis needed?        → CONTINUE to mode selection

Mode selection
├── Quick exploration               → quick   (3 phases, 2-5 min,  5-10 sources)
├── Standard research [DEFAULT]     → standard (6 phases, 5-10 min, 15+ sources)
├── Critical decision support       → deep    (8 phases, 10-20 min, 25+ sources)
└── Comprehensive review            → deep    (8 phases, 20-45 min, 30+ sources)
```

**Default assumptions:** Technical query → technical audience. Comparison request → balanced perspective required. Trend query → focus on most recent 12-18 months.

---

## Mode Table

| Mode | Phases | Source Target | Avg Credibility Gate | Time Target |
|------|--------|---------------|----------------------|-------------|
| quick | 1, 3, 8 | 5-10 | >60/100 | 2-5 min |
| standard | 1-5, 8 | 15+ | >60/100 | 5-10 min |
| deep | 1-8 | 25+ | >70/100 | 10-20 min |

---

## Pipeline Phases

### Phase 1: SCOPE — Research Framing

**Objective:** Define what is and is not being researched before touching any source.

**Activities:**
1. Decompose the question into 3-7 core sub-questions
2. Identify relevant stakeholder perspectives (technical, business, critical)
3. Define explicit scope boundaries: what is in scope, what is out
4. Establish success criteria — what would constitute a sufficient answer
5. List key assumptions to validate during research
6. Derive a short research slug (lowercase, hyphens, ≤5 words) for file naming

**Ambiguity check:** If the query is ambiguous — multiple valid interpretations exist that would lead to substantially different research — pause and confirm scope with the user before proceeding. Do not infer scope from a vague question. A wrong scope commitment in Phase 1 compounds through all subsequent phases: the wrong sub-questions are planned, the wrong searches are run, and the wrong synthesis is delivered. A brief clarification question is cheaper than a complete redo.

**Quality criteria:** Scope document must fit on one page. If it doesn't, the question is too broad — narrow it.

---

### Phase 2: PLAN — Strategy Formulation

**Objective:** Create a research roadmap before launching any searches.

**Activities:**
1. Map the 3-7 sub-questions to search angles (core topic, technical details, recent developments, academic sources, alternative perspectives, statistical data, critical analysis)
2. Identify knowledge dependencies — what must be understood before what
3. Generate 5-15 specific search query variants covering different angles
4. Plan source diversity: academic, industry, news, technical documentation
5. Define quality gates for this specific research task
6. Create a task ledger: sub-question → owner → status → output

**Quality criteria:** Each sub-question must have at least 2 distinct search angles planned.

---

### Phase 3: SEARCH — Parallel Information Gathering

**Objective:** Systematically collect information from multiple independent sources.

**Activities:**

**Step 1 — Launch all searches concurrently** in a single execution block:
- Core topic (broad semantic search)
- Technical details (specific term search)
- Recent developments (date-filtered to last 12-18 months)
- Academic / peer-reviewed sources
- Alternative perspectives and criticisms
- Statistical and quantitative data
- Industry analysis and applications
- Known limitations and failure modes

**Step 2 — Deep-read key sources:** For the 3-5 most promising URLs, fetch and read the full content, not just snippets. Do not rely on search result abstracts for core claims.

**Step 3 — Follow promising tangents** with additional targeted searches as gaps emerge.

**Step 4 — Maintain source diversity:**
- Minimum 3 source types (academic, industry, news, technical docs)
- Temporal mix: recent (last 12-18 months) + foundational older sources
- Perspective mix: proponents + critics + neutral analysis
- Geographic mix: avoid over-reliance on single-country sources

**Quality gate — proceed to Phase 4 when first threshold reached:**
- quick: 5+ sources OR 2 min elapsed
- standard: 15+ sources with avg credibility >60 OR 5 min elapsed
- deep: 25+ sources with avg credibility >70 OR 10 min elapsed

---

### Phase 4: VERIFY — Cross-Reference Triangulation

**Objective:** Validate information across multiple independent sources before treating anything as established fact.

**Activities:**
1. List all claims that will appear in the final report
2. For each core claim: confirm it appears in 3+ independent sources
3. Flag any single-source claims with a [SINGLE SOURCE] marker
4. Identify contradictions between sources — record both positions
5. Assess source independence (sources must not all cite each other)
6. Note consensus vs. genuinely contested areas
7. Record confidence level per claim: high (3+ concordant sources), medium (2 sources), low (1 source or conflicting)

**Source independence caveat:** Sources that all cite the same original study or news report are not independent — they are one data point amplified. Before counting sources as separate confirmations, check whether they share a common citation or all trace to a single origin (a press release, a single preprint, a Reuters wire story). A claim reported in dozens of outlets may still have only one independent source if all coverage traces to the same origin. When in doubt, count the origin, not the coverage.

**Quality criteria:**
- Core claims: 3+ independent sources minimum
- Single-source claims: flagged and treated as provisional
- Contradictions: documented, not papered over

---

### Phase 4.5: OUTLINE REFINEMENT — Evidence-Driven Adaptation

**Objective:** Adapt the research structure to match what the evidence actually shows, not what was initially assumed.

**Applies to:** standard, deep modes only. Quick mode skips this.

**Activities:**
1. Compare Phase 1 scope against Phase 3-4 discoveries
2. Check for signals requiring adaptation:
   - Major findings contradict initial assumptions
   - Evidence reveals a more important angle than originally scoped
   - Critical sub-topic emerged that was not in the original plan
   - Sources consistently discuss aspects not in the initial outline
3. If adaptation is warranted: add sections for unexpected findings, demote sections with weak evidence, reorder by evidence strength
4. Document the rationale for any changes in the methodology appendix
5. If the refined outline reveals gaps: run 2-3 targeted searches (time-boxed to 5 min)

**Anti-patterns to avoid:**
- Do NOT adapt based on "what would be interesting" — only on evidence
- Do NOT add sections without supporting evidence already in hand
- Do NOT restructure more than 50% of the outline (if more is needed, the original scope was severely wrong)

---

### Phase 5: SYNTHESIZE — Deep Analysis

**Objective:** Generate understanding that goes beyond what any single source provides.

**Activities:**
1. Identify patterns that hold across multiple sources
2. Map relationships and tensions between concepts
3. Build argument structures with evidence hierarchies
4. Generate insights: what does the totality of evidence imply?
5. Create conceptual frameworks where helpful
6. Distinguish clearly between: facts from sources vs. your synthesis vs. speculation

**Quality criteria:**
- Every factual claim must cite a specific source [N]
- Synthesis and inference must be labeled as such
- No vague attributions ("research suggests", "experts believe") — use specific citations

---

### Phase 6: CRITIQUE — Quality Assurance

**Applies to:** deep mode only.

**Objective:** Rigorously stress-test the research before writing.

**Red-team questions:**
- What is missing from this analysis?
- What could be wrong in my synthesis?
- What alternative explanations exist for the key findings?
- What biases are present in my source selection?
- What would a skeptical practitioner object to?
- What would a peer reviewer reject?
- What recommendations can actually be executed?

**Critical gap loop-back:** If critique identifies a material knowledge gap (not just a writing issue), return to Phase 3 with 2-3 targeted delta-queries. Time-box to 5 minutes. This prevents publishing reports with known blind spots.

---

### Phase 7: REFINE — Gap Resolution

**Applies to:** deep mode only.

**Objective:** Address weaknesses identified in Phase 6.

**Activities:**
1. Conduct additional searches for flagged gaps
2. Strengthen weak arguments with additional evidence
3. Add missing perspectives identified in critique
4. Resolve documented contradictions with additional research
5. Replace any single-source claims where possible

---

### Phase 8: WRITE + DELIVER — Report Generation

**Objective:** Produce a professional, citation-complete research report.

**Writing standards:**
- Prose-first: ≥80% flowing prose, ≤20% bullet points
- Precision: specific numbers embedded in sentences, not vague qualifiers
- Economy: no filler, no hedging without cause
- Directness: state findings, then support — not the reverse
- Citation density: every factual claim cited in the same sentence [N]

**Anti-hallucination rules:**
- Every factual claim → immediate citation [N]
- Label synthesis explicitly: "This suggests..." / "Taken together, these findings indicate..."
- Label speculation: "One possible interpretation is..."
- When uncertain: "No sources found addressing X directly" — never fabricate a citation
- Distinguish fact (from sources) from analysis (your synthesis)

---

## Source Credibility Scoring

Score each source 0-100 on these criteria:

| Criterion | 0-25 (low) | 26-50 (medium) | 51-75 (good) | 76-100 (high) |
|-----------|------------|----------------|--------------|----------------|
| **Publication type** | Blog, forum, no review | Trade press, news | Industry report, gov | Peer-reviewed, primary |
| **Author/org credibility** | Unknown, no affiliation | Known outlet | Recognized institution | Leading expert, top institution |
| **Evidence basis** | Opinion, anecdote | Partial data | Cited data | Rigorous methods, primary data |
| **Recency** | 5+ years old | 3-5 years | 1-3 years | <12 months |

**Thresholds:**
- Score <40: flag for additional verification, use only with caveat
- Score 40-70: adequate, use with source disclosure
- Score >70: high-quality, weight more heavily in synthesis
- Core claims require average credibility >60 across supporting sources

---

## Output Format

**Required sections (every report):**

```markdown
# [Topic]: Research Report
*Date | Mode: [quick/standard/deep] | Sources: N | Confidence: [High/Medium/Low]*

## Executive Summary
[200-400 words: key findings, main conclusions, major caveats]

## Introduction
[Scope, methodology, assumptions, what this report does and does not cover]

## [Finding 1 heading]
[600-2,000 words, prose-first, fully cited]

## [Finding 2 heading]
...

## [Finding N heading]
...

## Synthesis and Implications
[Patterns across findings, second-order implications, what the totality means]

## Limitations and Caveats
[What this research could not establish, where evidence is thin, known biases]

## Recommendations
[Actionable conclusions following from the evidence]

## Bibliography
[COMPLETE — every citation used in the report]
[N] Author/Org (Year). "Title". Publication. URL

## Methodology Appendix
[Search queries used, databases searched, outline adaptation rationale if applicable]
```

**Quality checklist before delivery:**
- [ ] Executive summary is 200-400 words
- [ ] 10+ sources (document if fewer and explain why)
- [ ] 3+ sources per major claim
- [ ] All claims cited immediately in the same sentence
- [ ] No placeholders (TBD, TODO, "content continues")
- [ ] Bibliography is complete — every [N] has an entry
- [ ] Prose ≥80%, bullets ≤20%
- [ ] Limitations section is honest about gaps
- [ ] Contradictions between sources are documented, not hidden

**Error handling:**
- Fewer than 5 sources after exhaustive search: note in limitations, deliver with explicit caveat
- Unresolvable contradiction between high-credibility sources: present both positions with evidence, do not pick sides arbitrarily
- Query is too broad to research thoroughly: scope down and explain what was and was not covered
