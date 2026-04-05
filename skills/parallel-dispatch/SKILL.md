<!-- Source: synthesized from deep-research-team-orchestrator.md, deep-research-team-coordinator.md, feynman-researcher-agent.md, feynman-system-prompt.md -->

---
name: parallel-dispatch
description: Dispatch N independent research workers in parallel using the Task tool, collect their results, and merge findings with per-worker source attribution preserved.
---

You are executing a parallel dispatch step. Your job is to spawn independent research workers for each sub-question, collect their outputs, and assemble results into a attributed finding set ready for synthesis.

---

## When to Parallelize vs. Run Sequentially

**Parallelize when:**
- Sub-questions are independent (answering one does not require the output of another)
- 2 or more sub-questions exist in the source plan
- Sub-questions target different source types (no resource contention)

**Run sequentially when:**
- Sub-question B requires results from sub-question A to formulate its query (e.g., "find papers on [term discovered in first pass]")
- The first pass is exploratory and the second pass is a targeted deep dive based on terms/sources found
- You have only one sub-question (no parallelism benefit)

Phased pipelines use parallelism within each phase but run phases sequentially. Label your phases clearly if using this pattern.

---

## Worker Instruction Template

Each spawned worker receives exactly this information — no more, no less:

```
Goal: [sub-question, stated as a complete question]
Constraint: Search [source type] only. Do not use other source types unless the primary yields fewer than 3 relevant results, in which case note the fallback and proceed.
Fallback: If primary source is insufficient, try [fallback source type from source plan].

Required output format:
- A bulleted list of findings
- Each finding is one sentence stating the claim
- Each finding includes: source URL | source type | one-sentence summary of the source
- If a source is a preprint, mark it [PREPRINT]
- If a source could not be verified (URL unavailable), mark it [UNVERIFIED] and do not include the claim

Do not synthesize or interpret findings. Report what sources say.
Do not include findings without a source URL.
Minimum: 3 findings with verified URLs. If you cannot reach 3, report what you found and explain the gap.
```

Workers must not be given the full research brief or other workers' sub-questions. Isolation is intentional — it prevents anchoring bias.

---

## Dispatch Pattern

```
FOR EACH sub-question in the source plan:
  Spawn a Task with:
    - Goal: [sub-question]
    - Constraint: search [source type] only
    - Fallback: [fallback source type]
    - Output: bullet list of findings, each with source URL

WAIT until ALL Tasks have completed before proceeding.

DO NOT proceed to synthesis until all workers have returned results
or have explicitly reported failure/gap.
```

Dispatch all workers simultaneously. Do not wait for one worker to finish before spawning the next.

---

## Failure Handling

If a worker returns zero findings:

1. **Retry with a broader query** — remove modifiers, expand acronyms, try synonyms. Re-dispatch the worker with the broadened query and note the revision.
2. **Try the fallback source type** — re-dispatch the worker using the fallback source type from the source plan.
3. **Accept the gap honestly** — if the fallback also yields no findings, return: `"No relevant sources found for: [sub-question text]"`. Do not pad the output with weakly-related findings to reach a minimum count. An honest gap is more useful than a manufactured answer — it tells the synthesis step where evidence is genuinely thin.

If a worker returns fewer than 3 findings (but at least 1):
- Report what was found with its source URL
- Mark the sub-question status as `partial`
- Note in the merge output what was tried and what the gap is

Document all worker failures and partial results in the merge output so the synthesis step can handle gaps correctly and flag low-confidence areas.

---

## Merge Protocol

After all workers complete, merge their outputs using this structure. Preserve per-worker attribution — do not flatten sources into a single undifferentiated list.

```
DISPATCH RESULTS
================
Sub-question 1: [question text]
Source type searched: [type]
Status: [complete | partial | insufficient]
Findings:
  - [claim] | [URL] | [source type] | [one-sentence summary]
  - [claim] | [URL] | [source type] | [one-sentence summary]
  ...

Sub-question 2: [question text]
Source type searched: [type]
Status: [complete | partial | insufficient]
Findings:
  - [claim] | [URL] | [source type] | [one-sentence summary]
  ...

[repeat for each sub-question]

GAPS AND FAILURES:
- [list any sub-questions that returned insufficient results, with reason]
```

This merged output is the direct input to `research-synthesis`.

Attribution must be preserved through synthesis. Each finding must remain traceable to its originating sub-question and source URL.
