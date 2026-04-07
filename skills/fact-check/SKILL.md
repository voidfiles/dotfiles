---
name: fact-check
description: Verifies specific claims by decomposing them into atomic sub-claims and searching for independent corroborating or contradicting evidence. Produces a structured verdict with an evidence table. Use when verifying a specific factual assertion, checking for contradictions between sources, assessing whether a claim is supported by evidence, or auditing a document for unsupported statements. NOT for open-ended research or literature surveys.
---

# Fact Check

## When to Use

Use this skill when:

- A specific claim needs verification ("Is it true that X?")
- Two sources contradict each other and you need to determine which is correct
- A document contains assertions that need independent verification
- A user wants to know whether a statistic, finding, or narrative is accurate
- Auditing an AI-generated or third-party document for hallucinations or errors

Do NOT use for: general research (use deep-research), academic literature surveys (use literature-review), or open-ended "tell me about X" questions.

---

## Claim Decomposition

Complex claims must be broken into **atomic, falsifiable sub-claims** before searching. An atomic sub-claim:

- Makes exactly one verifiable assertion
- Can be confirmed or refuted by a single piece of evidence
- Is specific enough that a source either supports or contradicts it

**Example decomposition:**

Original claim: "GPT-4 achieved human-level performance on the bar exam, scoring in the 90th percentile."

Sub-claims:

1. GPT-4 was tested on the bar exam
2. GPT-4's score on the bar exam was in the 90th percentile
3. The 90th percentile score represents human-level performance on the bar exam

Each sub-claim is independently falsifiable. Note that sub-claim 3 is an interpretive framing that may itself be contested.

**How to decompose:**

1. Identify every distinct factual assertion in the claim
2. Separate factual assertions from interpretive framing
3. Isolate any implied comparisons or context-dependent statements
4. List all sub-claims explicitly before beginning any search

---

## Source Strategy

**Rule: search for both supporting AND contradicting evidence for every sub-claim.**

Searching only for confirmation produces misleading verdicts. Actively seek sources that would refute the claim.

**For each sub-claim, run:**

1. A search designed to find supporting evidence
2. A search designed to find contradicting evidence ("X is false", "X is incorrect", "X is disputed")
3. A search for the primary source (the original study, official dataset, or direct statement)

**Source independence rule:**
Sources must be independently gathered — they must not all cite the same upstream source. If three sources all trace back to a single press release, that is one independent data point, not three.

**Source convergence warning:** Many claims that appear to be "independently confirmed" by multiple sources actually trace to a single origin — a press release, a single study, or a Reuters wire story that all subsequent coverage reproduced. Before counting sources as independent confirmations, check whether they cite each other or reference the same underlying source. A claim in 20 news articles based on one study is one independent data point, not twenty.

**Test for independence:**

- Do these sources have different authors and institutions?
- Do they arrive at their claims through different methods or data?
- Could they have influenced each other's conclusions?

Prefer primary sources (original studies, official data releases, direct quotes) over secondary reports (news coverage, summaries, commentary).

**Source count targets:**

- Simple factual claim: minimum 3 independent sources
- Statistical claim: minimum 3 independent sources including original data
- Scientific finding: minimum 3 peer-reviewed sources or 2 peer-reviewed + 1 authoritative review
- Contested claim: sources on both sides required before rendering verdict

---

## Source Credibility Assessment

Rate each source used in the evidence table:

| Dimension          | High                                                  | Medium                              | Low                                       |
| ------------------ | ----------------------------------------------------- | ----------------------------------- | ----------------------------------------- |
| **Credibility**    | Peer-reviewed, established institution, official data | Reputable news outlet, known expert | Blog, unknown author, no editorial review |
| **Evidence basis** | Primary data, rigorous methodology                    | Cited data, sound approach          | Anecdotal, no data, opinion               |
| **Recency**        | <2 years                                              | 2-5 years                           | 5+ years (note potential obsolescence)    |
| **Objectivity**    | No conflicts, balanced view                           | Minor affiliations disclosed        | Funded by interested party, one-sided     |

**Overall source quality:**

- 4 High = strong source — weight heavily
- 2+ Medium = adequate source — use with caveats
- 2+ Low = weak source — verify independently before relying on it

---

## Verdict Framework

Apply one of four verdicts to each sub-claim:

| Verdict          | Criteria                                                                                                                                                                                                                                                                                   |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **SUPPORTED**    | 3+ independent credible sources confirm the sub-claim AND no credible source contradicts it. _Note: SUPPORTED means the claim is well-attested in sources accessible to the LLM — it does not mean the claim is true. For high-stakes decisions, verify against primary sources directly._ |
| **CONTRADICTED** | 2+ credible independent sources refute the sub-claim with evidence AND no equivalently credible source confirms it                                                                                                                                                                         |
| **CONTESTED**    | Credible sources exist on both sides; the evidence does not clearly favor one position                                                                                                                                                                                                     |
| **INSUFFICIENT** | Fewer than 3 independent sources found; or only low-credibility sources found; or the claim is too vague to test                                                                                                                                                                           |

**Special cases:**

- "No evidence found" is not the same as "contradicted" — use INSUFFICIENT if the search was exhaustive
- A contested verdict is not a failure — many important claims are genuinely contested
- Do not force a verdict when the evidence is genuinely ambiguous

**Overall claim verdict:**

- If all sub-claims are SUPPORTED → overall claim is SUPPORTED
- If any sub-claim is CONTRADICTED with no resolution → overall claim is CONTRADICTED or CONTESTED
- If critical sub-claims are INSUFFICIENT → overall claim is INSUFFICIENT
- If sub-claims split across verdicts → overall claim is CONTESTED; explain the split

---

## Evidence Table Format

For each sub-claim, build a table:

**Sub-claim N: [exact text of the sub-claim]**

| Source        | URL/Reference     | Supports / Contradicts | Credibility | Key Quote or Finding      |
| ------------- | ----------------- | ---------------------- | ----------- | ------------------------- |
| [Source name] | [URL or citation] | Supports               | High        | "[Relevant direct quote]" |
| [Source name] | [URL or citation] | Contradicts            | Medium      | "[Relevant direct quote]" |
| [Source name] | [URL or citation] | Supports               | High        | "[Relevant finding]"      |

**Verdict:** [SUPPORTED / CONTRADICTED / CONTESTED / INSUFFICIENT]
**Confidence:** [High / Medium / Low]
**Notes:** [Any important caveats, conflicting interpretations, or limitations in the evidence]

---

## Output Format

```markdown
# Fact Check: [original claim in full]

## Claim Decomposition

Original claim: "[exact text]"

Sub-claims:

1. [Sub-claim 1]
2. [Sub-claim 2]
3. [Sub-claim 3]
   [...]

---

## Evidence

### Sub-claim 1: [text]

| Source | Reference | Supports/Contradicts | Credibility | Key Finding |
| ------ | --------- | -------------------- | ----------- | ----------- |
|        |           |                      |             |             |
|        |           |                      |             |             |
|        |           |                      |             |             |

**Verdict:** [SUPPORTED / CONTRADICTED / CONTESTED / INSUFFICIENT]
**Confidence:** [High / Medium / Low]
**Notes:** [caveats]

### Sub-claim 2: [text]

[...same structure...]

---

## Overall Verdict

**Claim:** [original claim restated]
**Overall verdict:** [SUPPORTED / CONTRADICTED / CONTESTED / INSUFFICIENT]
**Confidence:** [High / Medium / Low]

**Summary:** [2-4 sentences explaining the verdict, what evidence was found, and what uncertainty remains]

**Key caveats:**

- [Any important limitations in the evidence]
- [Any interpretive ambiguities]
- [Any time-sensitivity issues]

## Sources

[All sources used, with full citations]
```

---

## Procedural Rules

1. **Always cite specific sources.** Never state a verdict without evidence. "I believe X" or "it is generally understood that X" are not evidence.

2. **Distinguish absence of evidence from contradicting evidence.** "No sources found for X" → INSUFFICIENT. "Sources found that directly refute X" → CONTRADICTED. These are different verdicts with different implications.

3. **Prefer primary sources.** If a claim is about a specific study, read the study directly rather than relying on press coverage or summaries.

4. **Note source quality and recency.** A verdict based on three low-credibility sources is not as strong as one based on three high-credibility sources.

5. **Do not resolve genuine disagreement by picking sides.** When credible sources conflict, the verdict is CONTESTED and both positions must be reported with their evidence.

6. **Flag interpretive framing separately.** A factual assertion ("X scored in the 90th percentile") may be well-supported while the interpretive frame ("this represents human-level performance") is contested. Report these as separate sub-claims.

7. **Report search scope.** If the search was limited (e.g., only English-language sources, only web sources, no access to paywalled databases), note this as a limitation on the verdict's completeness.
