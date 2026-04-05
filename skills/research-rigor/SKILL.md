<!-- Source: synthesized from scientific-method.md, experimental-design.md, research-ai-tools.md -->

---
name: research-rigor
description: Apply the core principles of methodological rigor to study design and execution — covering the hypothesis-first rule, controls, reproducibility, DOE basics, pre-registration, and anti-hallucination patterns for AI-assisted research.
---

# Research Rigor

## When to Use

- Designing a new study or experiment from scratch
- Checking an existing methodology for soundness before running it
- Ensuring a computational analysis is reproducible by others
- Reviewing a research plan for common methodological failures
- Using AI tools in a research workflow and needing to guard against false claims

---

## Hypothesis-First Rule

**Define your hypothesis before collecting or analyzing data.**

This is the single most important principle in research rigor. The hypothesis frames what counts as a confirmatory result and what counts as a failure. Writing a hypothesis after seeing results — then presenting the analysis as though the hypothesis was stated a priori — is called **HARKing: Hypothesizing After Results are Known**.

HARKing is a problem because:
- It converts exploratory findings into misleading confirmatory claims
- It inflates false-positive rates: researchers unconsciously test many implicit hypotheses and report the one that worked
- It makes the literature look more consistent than it actually is, since each published result appears to be a clean test of a pre-specified prediction
- It is almost impossible to detect from a published paper alone

Before analysis, write down: the primary hypothesis, the primary outcome measure, the statistical test you will use, and the threshold for a positive result. If you explore the data first and then form hypotheses from what you find, label those analyses explicitly as exploratory.

---

## Controls

Well-designed experiments isolate the variable of interest by establishing what the system looks like under known conditions.

### Positive Controls
**Purpose:** Confirm that the method works and can detect an effect when one exists.

A positive control is a condition where you expect a known, detectable result. If the positive control fails, the experiment is uninformative — you cannot distinguish "no effect" from "broken assay."

*Example:* In a cell viability assay, a well-established cytotoxic compound at a known concentration serves as the positive control. If treated cells do not show reduced viability, the assay is not working.

### Negative Controls
**Purpose:** Confirm the baseline — what the outcome looks like when the treatment is absent.

A negative control receives no active treatment (or a vehicle/placebo). It establishes the background against which treatment effects are measured.

*Example:* In a gene knockout experiment, wild-type cells or scramble-sequence cells provide the negative control. Without this, you cannot establish whether the knockout itself caused the observed change.

### Confound Controls
**Purpose:** Isolate the variable of interest by holding other potential causes constant.

Confound controls match the experimental and control conditions on everything except the treatment variable. They answer the question: "Could something other than my treatment explain this result?"

*Example:* Testing whether a drug reduces inflammation: the vehicle control must contain the same solvent at the same volume; any osmolarity, pH, or carrier-protein differences between drug and vehicle conditions are confounds that need to be controlled.

---

## Reproducibility Checklist

A study is reproducible if an independent researcher can rerun the analysis and obtain the same results. This checklist covers the minimum requirements.

**Code**
- [ ] Version-controlled in a repository (Git)
- [ ] README explains how to run the analysis from scratch
- [ ] No hardcoded absolute paths; paths are relative or configurable
- [ ] All scripts run without manual intervention beyond documented setup

**Data**
- [ ] Raw data preserved and not overwritten by processing steps
- [ ] All preprocessing steps documented (or implemented as runnable scripts)
- [ ] Derived datasets are clearly labeled as derived, not raw
- [ ] Data stored in a named, versioned location (not just "data_final_v3.csv")

**Environment**
- [ ] Software dependencies listed with pinned versions (requirements.txt, environment.yml, lockfile, or container)
- [ ] Operating system and hardware requirements noted if relevant
- [ ] Any external services or APIs documented

**Random Seeds**
- [ ] Every stochastic process (random splits, sampling, model initialization, shuffling) uses an explicit seed
- [ ] Seeds are documented and consistent across runs
- [ ] Sensitivity to seed choice is noted if results vary substantially

**Analysis**
- [ ] Confirmatory analyses are pre-registered or clearly distinguished from exploratory analyses
- [ ] All planned analyses are reported, including non-significant ones
- [ ] Primary outcome is designated before analysis

---

## Anti-Hallucination Patterns

When using AI tools (LLMs, AI search, summarization tools) in a research workflow, apply these patterns to avoid incorporating false claims into your work.

**Verify before asserting**
AI systems can state incorrect information confidently and fluently. Do not cite a paper, statistic, or finding that came from an AI summary without locating the primary source and confirming the claim yourself. AI-generated citations are frequently wrong — they may invent plausible-sounding author names, journals, years, and titles.

**Cite primary sources**
Prefer original papers over AI-generated summaries, and prefer primary research over review articles when the specific finding matters. Each step away from the primary source introduces opportunities for distortion or oversimplification.

**Flag uncertainty explicitly**
Use language that accurately represents the strength of evidence. "Evidence suggests" is not equivalent to "it is established that." Write with appropriate hedges and distinguish between: well-replicated findings, preliminary results, contested claims, and speculative interpretations. When the evidence is mixed, say so.

**Never present contested claims as consensus**
If a claim is debated in the literature, represent the debate. AI tools tend to smooth over controversy and present one side (often the more prominent or more recent one). Before asserting that a field has reached consensus, verify that consensus with primary sources.

---

## DOE Basics (Design of Experiments)

Conceptual principles for structuring experiments to extract maximum information efficiently.

### Factorial Design — When to Use
Use factorial design when you have multiple factors (independent variables) and want to understand their effects simultaneously, including whether they interact.

One-factor-at-a-time (OFAT) testing — varying one variable while holding all others fixed — cannot detect interactions and is less efficient than factorial design. If Factor A has no effect when Factor B is at level 0 but a large effect when B is at level 1, OFAT will miss this entirely depending on which level of B you happened to hold fixed.

Use a factorial design when: you have 2–5 factors, you suspect interactions matter, and you can run all or a fractional subset of the combinations.

### Blocking — What It Protects Against
Blocking protects against **known sources of variation** that you cannot eliminate but can measure and account for.

A block is a grouping of experimental units that are more similar to each other than to units in other groups. By running each treatment condition within each block, you remove the block-to-block variation from the error term, making treatment effects easier to detect.

*Example:* If an experiment runs across three days and day-to-day variability is expected (equipment calibration, reagent lot), assign each treatment to at least one run per day. Day is the blocking variable.

### Randomization — What It Protects Against
Randomization protects against **unknown sources of variation** — confounds you have not anticipated and cannot block.

When treatment assignment is random, any unmeasured confounds are distributed approximately equally across conditions by chance. Without randomization, systematic biases (processing order, position in a plate, time of day) can masquerade as treatment effects.

Randomize the order of all experimental runs. Document the randomization scheme so it can be reproduced.

---

## Pre-Registration Pattern

Pre-registration means committing your hypotheses and analysis plan to a written record before running the experiment or analyzing the data.

**Why it matters:** Pre-registration makes the distinction between confirmatory and exploratory analysis legible after the fact. It prevents unconscious outcome-switching, protects against p-hacking, and makes your findings more credible to reviewers and readers.

**How to do it informally (minimum viable pre-registration):**
1. Write a brief document (even a dated email to yourself or a timestamped file in your repository) stating:
   - The primary hypothesis in one sentence
   - The primary outcome measure
   - The statistical test and threshold you will use
   - Any planned subgroup or secondary analyses
2. Commit and timestamp the document before data collection or analysis begins
3. In your final write-up, note what was pre-registered versus what was added exploratorily

Formal pre-registration platforms include OSF (Open Science Framework) and AsPredicted. Formal registration is expected for clinical trials and is increasingly common in social and biomedical sciences.

Any analysis conducted after seeing the data that was not in the pre-registration is exploratory and should be labeled as such. Exploratory findings are valuable — they generate hypotheses for future confirmatory work — but they should not be presented as confirmatory results.
