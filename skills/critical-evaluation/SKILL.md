<!-- Source: synthesized from scientific-critical-thinking.md, scholar-evaluation.md, peer-review.md -->

---
name: critical-evaluation
description: Assess evidence quality and research rigor using GRADE evidence levels, Cochrane Risk of Bias domains, and the ScholarEval 8-dimension scoring rubric to produce a defensible verdict on any paper or source.
---

# Critical Evaluation

## Scope of Applicability

**GRADE and Cochrane RoB are clinical frameworks.** GRADE was designed to rate confidence in effect estimates from clinical intervention studies. Cochrane Risk of Bias was designed specifically for randomized controlled trials. Applying these frameworks to non-clinical sources — tech blog posts, market research reports, policy documents, software documentation, business case studies, or opinion pieces — is a category error. These sources are not structured as clinical trials and cannot be meaningfully rated on randomization, blinding, or attrition.

**For non-clinical sources, use the Quick Assessment Checklist and ScholarEval dimensions only.** The 10-question checklist and the 8-dimension ScholarEval rubric are general-purpose and apply across source types. GRADE and Cochrane RoB should be reserved for evaluating clinical intervention studies, systematic reviews of clinical trials, and observational epidemiological studies.

When in doubt about which framework applies: if the source is not reporting results from a study of human subjects with a defined intervention and comparison condition, skip GRADE and Cochrane RoB and go directly to ScholarEval.

---

## When to Use

- Evaluating sources before including them in a literature review or research synthesis
- Assessing paper quality for a systematic review or meta-analysis
- Reviewing a methodology section for soundness
- Deciding how much weight to give a specific finding
- Producing a structured quality rating for any scholarly work

---

## GRADE Evidence Levels

GRADE rates the overall confidence that an effect estimate is close to the true effect.

| Level | Meaning | Starting point |
|---|---|---|
| **High** | We are very confident the estimate is close to the true effect. Further research is very unlikely to change our confidence. | RCTs begin here; well-executed observational studies upgraded substantially. |
| **Moderate** | We are moderately confident. The true effect is likely close to the estimate, but there is a possibility it is substantially different. | RCTs downgraded once; observational studies upgraded once. |
| **Low** | Our confidence is limited. The true effect may be substantially different from the estimate. | RCTs downgraded twice; observational studies at baseline. |
| **Very Low** | We have very little confidence in the estimate. The true effect is likely substantially different. | Observational studies downgraded; case series; expert opinion. |

**Factors that downgrade evidence (each issue = −1 level):**
1. Risk of bias — serious methodological flaws in included studies
2. Inconsistency — unexplained heterogeneity in results across studies
3. Indirectness — population, intervention, or outcome differs from question of interest
4. Imprecision — wide confidence intervals, small sample, few events
5. Publication bias — selective reporting or funnel plot asymmetry

**Factors that upgrade evidence (observational studies only):**
1. Large effect (RR > 2 or < 0.5 with no plausible confounding)
2. Dose-response gradient present
3. All plausible confounders would reduce (not inflate) the effect

---

## Cochrane Risk of Bias Domains

Apply to each individual study before aggregating evidence. Rate each domain: Low / Some concerns / High.

| Domain | What it covers | How to assess |
|---|---|---|
| **Selection bias** | Were participants properly randomized? Was allocation concealed? | Check sequence generation method (random number table, computer) and whether allocators could predict the next assignment. |
| **Performance bias** | Were participants and personnel blinded to treatment allocation? | Verify blinding procedures. For non-blinding, judge whether lack of blinding could influence outcomes. |
| **Detection bias** | Were outcome assessors blinded? | Determine who measured outcomes and whether they knew group assignment. Objective outcomes (mortality) are lower risk than subjective ones (pain scores). |
| **Attrition bias** | Was incomplete outcome data handled appropriately? | Compare dropout rates between groups. Check whether intention-to-treat analysis was used. Look for differential reasons for missing data. |
| **Reporting bias** | Were all pre-specified outcomes reported? | Compare registered protocol or methods section against published results. Missing outcomes with non-significant p-values are a red flag. |

---

## ScholarEval 8-Dimension Scoring Rubric

Score each dimension 1–5. Apply to the work as a whole; note "N/A" for dimensions not applicable to the work type.

**Scale:** 5 = Exemplary / 4 = Good, minor issues / 3 = Adequate, notable gaps / 2 = Needs significant revision / 1 = Fundamental problems

| # | Dimension | What 5 looks like | What 1 looks like |
|---|---|---|---|
| 1 | **Problem Formulation & Research Questions** | Question is specific, novel, significant, and clearly bounded. Contribution is explicit. | Vague or trivial question. No statement of why it matters. |
| 2 | **Literature Review** | Comprehensive, critically synthesized, identifies gaps, current sources. | Superficial summary, major papers missing, no gap identification. |
| 3 | **Methodology & Research Design** | Design matches the question, rigorous, reproducible, limitations acknowledged. | Design cannot answer the question, key details missing, no limitations. |
| 4 | **Data Collection & Sources** | Appropriate data, sufficient sample, collection procedures transparent, sources credible. | Data inappropriate for question, sample too small, collection unclear. |
| 5 | **Analysis & Interpretation** | Methods correct and justified, alternative explanations considered, results-claims aligned. | Wrong methods, no alternatives considered, conclusions exceed the data. |
| 6 | **Results & Findings** | Clear presentation, full statistical reporting (effect sizes, CIs, p-values), accurate interpretation. | Results incomplete, statistics missing or wrong, over-interpreted. |
| 7 | **Scholarly Writing & Presentation** | Clear, organized, appropriate tone, logical flow, accessible to target audience. | Disorganized, unclear, major grammar or style problems. |
| 8 | **Citations & References** | Complete, high-quality sources, accurately cited, balanced perspectives, correct format. | Missing key citations, poor sources, inaccurate references, one-sided. |

---

## Quick 10-Question Assessment Checklist

For rapid screening of sources by non-specialists:

1. Is the research question clearly stated and specific?
2. Is the study design appropriate for answering that question?
3. Was randomization or a comparable control strategy used?
4. Were key variables measured objectively and consistently?
5. Is the sample size justified, and was a power calculation reported?
6. Are effect sizes and confidence intervals reported (not just p-values)?
7. Are limitations openly acknowledged?
8. Do the conclusions stay within what the data can support?
9. Is there a pre-registration, protocol, or other transparency measure?
10. Are potential conflicts of interest disclosed?

**Scoring guide:** 8–10 yes = proceed with confidence; 5–7 yes = use cautiously and note gaps; below 5 = exclude or treat as very low quality evidence.

---

## Red Flags

Signs that should trigger additional scrutiny or downgrading:

**P-hacking**
- Results cluster suspiciously just below p = 0.05
- Many outcomes reported but only significant ones emphasized
- No pre-registration and no mention of multiple comparisons correction
- Reported analyses appear to have been chosen after results were seen

**HARKing (Hypothesizing After Results are Known)**
- Hypotheses written in past tense in introduction; results already known
- No pre-registered hypothesis; conclusions presented as confirmatory
- Hypotheses match results precisely with no discussion of exploratory nature
- Story in paper feels too clean given the exploratory nature of the work

**Underpowered studies**
- No a priori power calculation
- Sample size below typical for the effect size in the field
- Wide confidence intervals suggesting imprecision
- Significant results from tiny samples (inflated effect sizes are likely)

**Conflicts of interest**
- Funding source not disclosed
- Industry funding for studies of proprietary products with positive outcomes
- Authors have financial stake in the result
- Funding source matches the direction of findings systematically

---

## Output Format

Provide the verdict in this structure:

**Evidence Quality Verdict:** [High / Moderate / Low / Very Low]

**GRADE Rationale:** Starting level based on study design; specify each downgrade or upgrade factor applied and why.

**Cochrane ROB Summary (if applicable):** One sentence per domain — risk level and key reason.

**ScholarEval Scores (if applicable):** Dimension scores as a table; total and mean.

**Key Concerns:** Bulleted list of the most important methodological or reporting issues, ranked by severity (critical → important → minor).

**Recommended Use:** One sentence on how to appropriately use this evidence given its quality level (e.g., "suitable as supporting evidence with caveats," "exclude from quantitative synthesis," "treat as hypothesis-generating only").
