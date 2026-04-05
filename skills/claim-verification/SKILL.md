---
name: claim-verification
description: Verify a specific claim by cross-referencing 3 or more independent sources. Returns Supported / Contradicted / Contested / Insufficient verdict with evidence. Use on any claim flagged LOW or CONTESTED in research-synthesis, or on any high-stakes claim before it enters a final output.
---

You are executing a claim verification step. Your job is to take one specific claim, search for both supporting and contradicting evidence, assess source independence, and return a structured verdict.

Verify one claim per invocation. For multiple claims, invoke this skill once per claim.

---

## Step 1 — Normalize the Claim

Before searching, make the claim atomic and falsifiable.

**Atomic** means the claim makes exactly one assertion. Split compound claims.

**Falsifiable** means the claim can in principle be shown to be wrong. Vague claims cannot be verified — they must be made concrete first.

Examples of vague → atomic transformation:

| Vague (do not verify as-is) | Atomic (verify this) |
|-----------------------------|----------------------|
| "Coffee is bad for you" | "Regular coffee consumption (≥3 cups/day) is associated with increased all-cause mortality in adults" |
| "Remote work hurts productivity" | "Remote workers show lower output on measurable tasks compared to equivalent in-office workers in studies controlling for role type" |
| "AI models hallucinate a lot" | "Large language models produce factually incorrect statements on at least 20% of knowledge-intensive queries in [specific benchmark]" |
| "The economy is doing well" | "US GDP growth exceeded 2.5% annualized in Q3 2024" |

If the claim as received is not atomic and falsifiable, transform it before proceeding and document the transformation in the output.

---

## Step 2 — Search Strategy

Search for BOTH supporting AND contradicting evidence. Confirmation-only search is not verification.

**For supporting evidence**, search:
- Direct statement of the claim or its equivalent
- Data or studies cited as evidence for the claim
- Expert consensus statements that include this claim

**For contradicting evidence**, search:
- Studies finding null results or opposite direction of effect
- Expert critiques, rebuttals, or meta-analyses challenging the claim
- Methodological critiques of the primary studies supporting the claim
- Cases where the claim does not hold (boundary conditions, exceptions)

**Query construction:**
- Run at minimum 2 queries with different phrasings of the claim
- Run at minimum 1 query explicitly seeking contradiction: add "challenge", "critique", "null result", "contrary evidence", "replication failure" to the query terms
- Do not stop after finding the first supporting source — continue until you have searched for contradictions or have exhausted reasonable search paths

---

## Step 3 — Independence Check

Before counting sources toward a verdict, verify that each source is genuinely independent.

Sources are NOT independent if:
- One source cites the other as its primary evidence for the claim
- Both sources derive from the same underlying study, dataset, or press release
- Both sources are from the same organization (even if published separately)
- Sources are news articles all reporting on the same single study

Sources ARE independent if:
- They conducted separate empirical investigations
- They used different datasets or methodologies
- They reached the same conclusion through different evidence paths
- They are from different institutions with no evident coordination

For a `Supported` verdict, you need 3 genuinely independent sources. Count carefully. Two papers from the same lab using the same dataset count as 1 independent source.

> **Important limitation:** The same LLM that retrieved sources is performing this independence check. This is consistency checking, not true verification — the LLM cannot inspect full citation graphs, access paywalled reference lists, or know which sources share an upstream origin that isn't visible in their abstracts. For high-stakes claims, the only reliable independence verification is human review of primary sources.

---

## Verdict Definitions

| Verdict | Criteria |
|---------|----------|
| **Supported** | 3 or more independent sources confirm the claim. No credible contradictions found. Sources represent a reasonable quality level (at minimum: not anonymous, not lacking methodology). |
| **Contradicted** | 2 or more credible sources refute the claim with evidence. Refuting sources are of comparable or higher quality than supporting sources. The weight of evidence is against the claim. |
| **Contested** | Credible sources exist on both sides. The evidence quality on each side is comparable — neither clearly dominates. Reasonable experts disagree. |
| **Insufficient** | Fewer than 3 independent sources found for either confirmation or refutation. Not enough evidence to reach a verdict. This is not the same as "false" — it means the evidence base is too thin. |

> **Scope of all verdicts:** All verdicts are based on sources accessible to the LLM at the time of verification. Paywalled studies, retracted papers not yet updated in indexes, non-English sources, and grey literature are systematically invisible and may contain contradicting or qualifying evidence. A `Supported` verdict means well-attested in accessible sources — not that the claim is true.

---

## Confidence Modifier

Apply a confidence modifier to the verdict based on source quality:

| Modifier | Criteria |
|----------|----------|
| **High** | Primary sources include peer-reviewed studies, official data, or direct primary evidence. No significant methodological concerns identified. |
| **Medium** | Primary sources are credible but include secondary sources, preprints, or sources with noted methodological limitations. |
| **Low** | Sources are secondary, undated, from non-expert sources, or have significant methodological weaknesses. Verdict should be treated as provisional. |

A final verdict reads as: `[Verdict] / [Confidence]` — e.g., "Supported / High" or "Contested / Medium".

---

## Output Format

```
CLAIM VERIFICATION
==================
Original claim: [claim as received]
Normalized claim: [atomic, falsifiable version — or "same as original" if already atomic]

Search queries used:
  Supporting: [query 1], [query 2]
  Contradicting: [query 3], [query 4]

Sources FOR the claim:
  1. [URL] | [source type] | [independence status] | [one sentence: what this source says]
  2. [URL] | [source type] | [independence status] | [one sentence: what this source says]
  3. [URL] | [source type] | [independence status] | [one sentence: what this source says]

Sources AGAINST the claim:
  1. [URL] | [source type] | [one sentence: what this source says]
  [or: "No credible contradicting sources found after searching for: [queries used]"]

Independence assessment:
  [Are the "for" sources genuinely independent? Note any dependencies or shared origins.]

VERDICT: [Supported | Contradicted | Contested | Insufficient]
CONFIDENCE: [High | Medium | Low]
RATIONALE: [One sentence explaining the verdict, naming the strongest evidence on each side.]

Action recommendation:
  [One of:
   - "Use this claim in final output — well-supported."
   - "Use with qualification: note that evidence is from [source type only] / [single study] / [contested area]."
   - "Do not use without further research: [specific gap to address]."
   - "Remove or flag as unverified: insufficient independent evidence found."]
```
