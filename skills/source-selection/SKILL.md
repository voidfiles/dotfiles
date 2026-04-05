<!-- Source: synthesized from deep-research-team-search-specialist.md, deep-research-team-coordinator.md, feynman-researcher-agent.md -->

---
name: source-selection
description: Decision guide for matching research sub-questions to source types, with priority ordering and fallback chains when primary sources yield insufficient results.
---

You are executing a source selection step. For each sub-question in a research plan, determine which source types to search, in what order, and what to do if results are thin.

---

## What LLMs Can Actually Access

The source types and priority ordering below describe what you *should* prefer for evidence quality. They do not describe what is always accessible.

**Academic databases return metadata, not full text.** PubMed, Cochrane, Semantic Scholar, and similar databases expose their APIs to return titles, abstracts, authors, and DOIs. Full-text access for most peer-reviewed articles requires an institutional subscription or payment. An LLM without that access can read the abstract but not the methods, results, or supplementary data — which are often where the relevant details live.

**What this means in practice:**
- When a sub-question requires peer-reviewed evidence, you can identify relevant papers and read their abstracts. Note this limitation explicitly in your output rather than proceeding as if you read the full paper.
- Do not cite a paper as supporting a specific methodological claim if you only had access to the abstract — the abstract may not contain the relevant detail.
- Open-access papers (PubMed Central, arXiv, SSRN, many journals) are fully readable. Prefer these when peer-reviewed full text is needed.
- For paywalled sources, note the access limitation in your source plan: e.g., "Peer-reviewed (abstract only)" rather than "Peer-reviewed."

---

## Source Type Taxonomy

| Source type | Best for | Limitations |
|-------------|----------|-------------|
| **Web** | Current events, product announcements, company information, recent releases, public discourse, practitioner experience, documentation for live systems | Highly variable quality; SEO-optimized content is common; information decays fast; no peer review |
| **Preprint** (arXiv, bioRxiv, SSRN, etc.) | Cutting-edge research before formal publication; fast-moving fields (ML, genomics, economics); technical methodology | Not peer-reviewed; results may be revised or retracted; quality varies widely |
| **Peer-reviewed** (journals, conference proceedings) | Established empirical findings; validated methodology; scientific consensus; foundational theory | Publication lag 6–24 months; paywalled; may not reflect latest developments in fast-moving fields |
| **Enterprise / proprietary** | Industry-specific data, internal benchmarks, market share figures, financial filings, competitive intelligence, internal documentation | Access-restricted; potential commercial bias; not independently verifiable; may be confidential |
| **Structured data** (datasets, databases, registries, benchmarks) | Quantitative claims, statistics, trend analysis, performance comparisons, longitudinal patterns | Requires interpretation; may be outdated; methodology behind collection matters; can be cherry-picked |

---

## Selection Rules by Question Type

| Question type | Primary source | Fallback |
|---------------|---------------|---------|
| Current events / recent developments | Web | Preprint (if technical), news archives |
| Technical how-to / implementation | Web (official docs) | Peer-reviewed, preprint |
| Empirical claims about the world | Peer-reviewed | Preprint, structured data |
| Cutting-edge ML / AI / genomics claims | Preprint | Peer-reviewed, web (vendor announcements) |
| Performance benchmarks | Structured data | Preprint, web (independent evaluations) |
| Causal mechanisms in established science | Peer-reviewed | Preprint, structured data |
| Market size / industry trends | Enterprise / proprietary | Web (analyst coverage), structured data |
| Historical facts (>5 years old) | Peer-reviewed | Web (encyclopedic sources), structured data |
| Expert opinion / practitioner experience | Web (blogs, talks, interviews) | Enterprise, peer-reviewed |
| Policy / regulatory requirements | Web (official government sources) | Enterprise, peer-reviewed |
| Statistical claims | Structured data | Peer-reviewed, web (with source attribution) |

---

## Priority Order When Multiple Source Types Fit

When a sub-question could be answered by more than one source type, prioritize in this order:

1. **Structured data** — if a dataset or benchmark directly answers the question, it provides the most objective evidence
2. **Peer-reviewed** — independently validated; cite over preprint when both cover the same claim
3. **Preprint** — acceptable when peer-reviewed is absent or too lagged; flag as not yet peer-reviewed
4. **Web (primary sources)** — official documentation, government pages, institutional releases; prefer over secondary web
5. **Web (secondary sources)** — journalism, analyst coverage, practitioner blogs; use when primary sources are unavailable
6. **Enterprise / proprietary** — use when available and access is possible; note potential bias

Always prefer the higher-priority type when it exists and is current. Do not substitute a lower-priority type to avoid paywalls without noting the limitation.

---

## Fallback Chain When Primary Source Yields Insufficient Results

Execute this chain in order when a search returns fewer than 3 useful results:

1. **Broaden query terms** — remove modifiers, try synonyms, expand acronyms
2. **Try adjacent source type** — move one step down the priority order above
3. **Search for systematic reviews or meta-analyses** (for academic questions) — these aggregate primary studies and may cover the territory even if individual studies are sparse
4. **Search for negative evidence** — look for discussions of why evidence is limited; this is itself a finding
5. **Search citation graphs** — find a key paper and look at what cites it (forward) or what it cites (backward)
6. **Document the gap** — if the fallback chain produces no useful results, record "insufficient evidence found" as the sub-question result; this is an honest and useful output

Do not fabricate sources or pad results with low-relevance material to reach a minimum count.

---

## Output Format: Source Plan Table

For each sub-question from `query-decomposition` or `research-planning`, produce one row:

| Sub-question | Primary source | Corpus / index hint | Query strategy | Fallback |
|-------------|---------------|---------------------|----------------|---------|
| [question text] | [source type] | [where specifically to look] | [query approach in 1 phrase] | [next source type to try] |

**Example:**

| Sub-question | Primary source | Corpus / index hint | Query strategy | Fallback |
|-------------|---------------|---------------------|----------------|---------|
| What do RCTs show about Mediterranean diet and cardiovascular outcomes? | Peer-reviewed | PubMed, Cochrane, major cardiology journals | Search for systematic reviews and RCTs; filter for ≥2 year follow-up | Preprint (medRxiv) |
| What are practitioners reporting about operational challenges running Mediterranean diet interventions at scale? | Web | Health system blogs, dietitian association publications, conference proceedings | Search for implementation reports, practitioner retrospectives | Enterprise (health system whitepapers) |
| What does longitudinal epidemiological data show about adherence and actual health outcomes in population studies? | Structured data | NHANES, UK Biobank publications, WHO dietary databases | Search dataset documentation and associated publications | Peer-reviewed cohort studies |

This source plan table is the direct input to `parallel-dispatch`.
