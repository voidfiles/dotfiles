name: research-planning
description: Pre-flight research planning: clarify scope, assess complexity, choose approach, decompose into sub-questions. Run before any research task.
---

You are executing a pre-flight research planning step. Before any search or retrieval begins, produce a research brief that governs the rest of the workflow.

---

## Step 1 — Clarify the Question

Ask and answer these questions internally before proceeding:

- **Is the question clear?** Can a researcher act on it without guessing what is wanted?
- **What does success look like?** What form should the answer take — a verdict, a comparison, an explanation, a list of options, a structured report?
- **What is explicitly out of scope?** Identify at least one adjacent topic that is NOT being asked about. Name it and exclude it.
- **Is there a time constraint?** Should answers reflect current state, a specific historical period, or trends over time?

**If the question is ambiguous — multiple valid interpretations exist that would lead to substantially different research — do not proceed.** Present the interpretations to the user and ask which is intended. A wrong scope decision in planning compounds through the entire pipeline: wrong sub-questions, wrong sources, wrong synthesis. The result is a well-formatted answer to the wrong question. When in doubt, a single clarifying question before starting is always cheaper than a full redo after delivering.

If the question has only minor ambiguity (e.g., uncertain time period or slight scope fuzziness), choose the most likely interpretation, document the assumption in the brief, and proceed.

---

## Step 2 — Assess Complexity

Classify the question into one of three tiers:

| Tier | Label | Criteria |
|------|-------|----------|
| 1 | **Simple** | Single factual claim or definition. One domain. Likely answered in 1–2 sources. No sub-questions needed. |
| 2 | **Standard** | Requires 3–8 sources. May span two adjacent domains. Answer requires some synthesis but not multi-track research. |
| 3 | **Complex** | Multi-domain or multi-perspective. 8+ sources likely needed. Answer requires parallel research tracks and explicit synthesis. Decomposition is required. |

Criteria for escalating from Tier 1 to Tier 2:
- The question contains "why", "how does", or "compare"
- Multiple entities, time periods, or domains are involved
- A definitive answer would require corroboration across source types

Criteria for escalating from Tier 2 to Tier 3:
- The question spans technical, empirical, and policy/social dimensions simultaneously
- Reasonable expert disagreement is expected
- Answering requires both current sources and academic literature

---

## Step 3 — Choose Approach

Select one approach based on the complexity tier:

| Approach | When to Use | Description |
|----------|-------------|-------------|
| **Direct retrieval** | Tier 1 | Issue a single targeted query. No decomposition. One source type. |
| **Query fanout** | Tier 2, single domain | Issue 2–4 query variants on the same question to improve recall. No parallel tracks. |
| **Phased pipeline** | Tier 2, multiple domains | Run an exploratory pass first, then a targeted deep pass using terms and sources discovered in phase 1. |
| **Multi-agent** | Tier 3 | Decompose into parallel sub-questions. Dispatch independent workers. Synthesize after all workers complete. |

---

## Step 4 — Identify Source Types Needed

For each sub-question (or the main question if Tier 1–2), identify which source types are relevant:

- **Web**: Current events, industry news, product documentation, recent announcements, public discourse
- **Academic / preprint**: Empirical evidence, theoretical frameworks, systematic reviews, established science
- **Enterprise / proprietary**: Internal databases, paywalled industry reports, filings, private data
- **Structured data**: Datasets, statistics, benchmarks, time series

Note: for Tier 1 and Tier 2 questions, listing the primary source type is sufficient. For Tier 3, each sub-question gets its own source type assignment.

---

## Step 5 — Decompose (Complex Questions Only)

For Tier 3 questions, generate parallel sub-questions using the decomposition heuristics in `query-decomposition`. Each sub-question must be:

- **Independent**: answerable without waiting for another sub-question's results
- **Bounded**: covers one aspect, domain, or perspective
- **Actionable**: leads to a specific search strategy

Format each sub-question as:
```
Sub-question: [question text]
Source type: [web | academic | enterprise | structured]
Search approach: [brief description of query strategy]
```

Target 2–3 sub-questions for low-end Tier 3, 4–7 for high-end Tier 3. Stop decomposing when further splits would create redundant or trivially small questions.

---

## Output: Research Brief

Produce a one-page brief in this format:

```
RESEARCH BRIEF
==============
Question: [the clarified, scoped question]
Success looks like: [what form the answer takes]
Out of scope: [explicitly excluded topics]
Complexity tier: [Simple | Standard | Complex]
Approach: [Direct retrieval | Query fanout | Phased pipeline | Multi-agent]

Source plan:
- [source type 1]: [what it covers for this question]
- [source type 2]: [what it covers for this question]

Sub-questions (Complex only):
1. [sub-question] → [source type] → [search approach]
2. [sub-question] → [source type] → [search approach]
...

Assumptions made: [list any ambiguity resolutions]
```

This brief is the contract for all downstream research steps. Subsequent skills (`query-decomposition`, `source-selection`, `parallel-dispatch`) should receive this brief as input.
