<!-- Source: synthesized from deep-research-team-query-clarifier.md, deep-research-team-coordinator.md, feynman-system-prompt.md -->

---
name: query-decomposition
description: Takes a research question and returns N parallel sub-questions, each with a source type hint and search approach, for use in multi-track research workflows.
---

You are executing a query decomposition step. Your job is to split a complex research question into parallel, independently answerable sub-questions — each matched to a source type and search approach.

---

## When to Decompose vs. Not

Decomposition adds overhead. Only use it when the question genuinely requires multiple independent research tracks.

**Do not decompose:**
- "What is the boiling point of water at sea level?" — single fact, one source
- "When was the Eiffel Tower built?" — historical fact, direct retrieval
- "What does REST stand for?" — definition, no parallelism needed
- "Who wrote Crime and Punishment?" — attribution, single lookup

**Do decompose:**
- "Why are lithium-ion batteries degrading faster in EVs than in consumer electronics?" — requires mechanism (chemistry), evidence (empirical studies), and context (use-pattern differences)
- "What are the tradeoffs between PostgreSQL and MongoDB for a high-write workload?" — requires performance benchmarks, operational considerations, and community/ecosystem evidence
- "What is known about the long-term cognitive effects of childhood lead exposure?" — spans neuroscience, epidemiology, policy, and longitudinal studies

The test: if a single researcher, searching a single source type, could reasonably answer the question in one pass, do not decompose.

---

## How Many Sub-Questions

| Question complexity | Sub-question count |
|--------------------|--------------------|
| Standard (Tier 2) | 2–3 |
| Complex (Tier 3, focused) | 4–5 |
| Complex (Tier 3, broad) | 5–7 |

Do not exceed 7 sub-questions. If you feel you need more, the question itself needs scoping first — return to `research-planning` and narrow the scope.

Each sub-question should be answerable in one focused research pass. If a sub-question would itself require decomposition, it is not atomic enough.

---

## Decomposition Heuristics by Question Type

### Causal questions ("Why does X happen?", "What causes X?")

Decompose into three tracks:
1. **Mechanism**: What is the proposed causal pathway? (academic / technical)
2. **Evidence**: What empirical evidence supports or challenges the mechanism? (academic / structured data)
3. **Context**: Under what conditions does the cause operate? Are there moderating factors? (web / academic)

Example — "Why are open-source LLMs closing the gap with proprietary models faster than expected?"
1. What architectural or training innovations have driven recent open-source LLM improvements? → academic/preprint → search arXiv for architecture and training technique papers
2. What benchmark evidence shows capability convergence between open and proprietary models? → structured data → search benchmark leaderboards and technical reports
3. What organizational or resource factors (compute access, talent, tooling) explain the acceleration? → web → search tech journalism and institutional announcements

---

### Comparative questions ("X vs. Y", "Which is better for Z?")

Decompose into dimensions of comparison. Each dimension is a sub-question.

Standard dimensions to consider:
- Performance / capability
- Cost / resource requirements
- Maturity / ecosystem / support
- Risk / failure modes / limitations
- Adoption / real-world usage patterns

Do not create a sub-question for every dimension. Select the 2–4 dimensions most relevant to the stated use case.

Example — "PostgreSQL vs. MongoDB for high-write analytical workloads":
1. What do benchmarks show for write throughput and query latency under high-concurrency analytical patterns? → structured data → search published benchmarks and technical evaluations
2. What are the operational tradeoffs (indexing, schema flexibility, consistency guarantees) relevant to analytics? → web/academic → search engineering blogs and documentation comparisons
3. What do practitioners report about real-world experience with each system for analytics? → web → search engineering retrospectives, HN discussions, conference talks

---

### Factual questions

Usually do not decompose. If the fact requires corroboration across source types (e.g., a contested statistic), use query fanout instead of decomposition — issue 2–3 variant queries against the same question rather than creating separate sub-questions.

---

### Exploratory questions ("What is known about X?", "What research exists on X?")

Decompose by aspect or domain. Map the territory first, then assign one sub-question per major aspect.

Standard aspects to consider:
- Empirical findings / what the data shows
- Theoretical frameworks / conceptual models
- Contested areas / active debates
- Applied implications / real-world applications
- Recent developments / emerging directions

Example — "What is known about the effects of sleep deprivation on decision-making?":
1. What experimental evidence exists on cognitive and executive function impairment from sleep deprivation? → academic → search neuroscience and cognitive psychology literature
2. What neurobiological mechanisms explain the observed decision-making changes? → academic → search neuroscience literature on prefrontal cortex and sleep
3. What is known about real-world decision quality in sleep-deprived populations (shift workers, medical residents, etc.)? → academic/web → search occupational health studies and applied research
4. Are there individual differences or moderating factors (age, expertise, task type) that affect the relationship? → academic → search individual differences and moderating variable studies

---

## Multi-type questions

When a question spans multiple types — for example, a causal-comparative question like "Why does X outperform Y?" combines a causal question (Why does X perform as it does?) and a comparative question (How does X differ from Y on relevant dimensions?) — apply the decomposition heuristic for each applicable type and merge the resulting sub-questions. Do not silently apply only one heuristic and discard the others.

**How to identify multi-type questions:**
- Causal + comparative: "Why does X outperform Y?" → use both Causal and Comparative heuristics
- Exploratory + factual: "What is known about X, and is claim Z true?" → use Exploratory for the first part and factual corroboration (query fanout) for the second
- Causal + policy: "Why does X happen, and what should be done about it?" → Causal for mechanism, plus an additional sub-question for policy/practitioner response

Merge sub-questions after applying both heuristics, deduplicate any overlapping tracks, and cap at 7 total sub-questions. If the merged set exceeds 7, the question spans too much territory — scope it down before decomposing.

---

## Sub-Question Output Format

For each sub-question, output one line in this format:

```
{sub-question} → {recommended source type} → {search approach}
```

Where:
- `{sub-question}` is a complete, self-contained question
- `{recommended source type}` is one of: web | academic | preprint | enterprise | structured
- `{search approach}` is a brief phrase describing the search strategy (e.g., "search arXiv for RCTs", "search benchmark leaderboards", "search engineering postmortems")

---

## Full Example

**Input question:** "What are the health risks of ultra-processed food consumption, and how strong is the evidence?"

**Decomposition:**

1. What does epidemiological evidence show about associations between ultra-processed food consumption and all-cause mortality, cardiovascular disease, and cancer? → academic → search longitudinal cohort studies and meta-analyses in nutrition epidemiology journals

2. What proposed biological mechanisms link ultra-processed food components (additives, emulsifiers, processing byproducts) to adverse health outcomes? → academic/preprint → search mechanistic studies and review articles on food additives and gut microbiome

3. What are the methodological limitations and contested claims in ultra-processed food research (e.g., NOVA classification validity, confounding factors)? → academic → search critical commentaries, letters, and methodological debates in nutrition journals

4. What do public health bodies and regulatory agencies currently recommend based on this evidence? → web → search WHO, national dietary guidelines, and recent policy documents

**Source plan summary:**
- Sub-questions 1–3: academic literature (peer-reviewed journals, preprints)
- Sub-question 4: web (official institutional sources)
