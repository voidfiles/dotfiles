---
name: research-ideation
description: Generate, formulate, and filter research ideas through three phases — divergent ideation, hypothesis formulation, and problem selection — using the Fischbach & Walsh framework to prioritize by generality, learning value, feasibility, and impact.
---

# Research Ideation

## When to Use

- Choosing a new research direction or thesis topic
- Generating candidate hypotheses from observations or preliminary data
- Evaluating whether a problem is worth pursuing before investing significant effort
- Breaking out of a narrow framing to find more promising angles
- Preparing a project pitch or proposal and needing to stress-test the idea

---

## Phase 1 — Divergent Ideation

The goal of this phase is to generate a wide range of candidate directions without premature filtering. Quantity and diversity matter more than immediate feasibility.

### Analogical Reasoning
Ask: "What does this problem resemble in a different domain?"

Draw structural parallels across fields. A drug resistance problem may parallel antibiotic resistance, economic market dynamics, or evolutionary arms races — each analogy suggests different mechanisms and interventions. State the analogy explicitly, then extract the specific insight it imports.

### Constraint Removal
Ask: "What would become possible if the main limitation didn't exist?"

Identify the constraint that most limits current approaches (budget, measurement resolution, ethical barriers, data availability, compute). Imagine it removed. What experiments or analyses does that unlock? Then work backwards: is there a partial or proxy version of that unconstrained experiment that is actually feasible?

### Inversion
Ask: "What would reliably make this problem worse?"

Inversion surfaces the causal levers that are easy to miss when thinking only in the positive direction. If you can identify what reliably produces the failure mode, you have identified a mechanism worth studying and potentially reversing.

### Interdisciplinary Connection
Ask: "What methods or frameworks from field X could apply here?"

Pick fields adjacent to your domain and list their strongest methodological contributions. Ask whether those tools are under-applied in your area. Examples: network analysis applied to cell biology, causal inference methods applied to ecology, psychophysics measurement approaches applied to human-computer interaction.

---

## Phase 2 — Hypothesis Formulation

Take promising directions from Phase 1 and make them precise enough to test.

### Observation → Mechanism → Prediction → Experimental Test Format

State each hypothesis in four parts:

1. **Observation**: What is the empirical pattern or anomaly that motivates the hypothesis? Be specific — cite the data or phenomenon.
2. **Mechanism**: What process or causal pathway would produce that observation if the hypothesis is true? Mechanistic hypotheses are more informative than descriptive ones.
3. **Prediction**: What specific, measurable outcome should follow if the mechanism operates as hypothesized? Include direction and ideally magnitude.
4. **Experimental test**: What is the minimal experiment that would confirm or refute the prediction? What comparison is required?

### Falsifiability Check
Ask: "What result would prove this hypothesis wrong?"

A hypothesis is only scientifically useful if there exists a possible observation that would refute it. If no such observation is conceivable, the hypothesis is not falsifiable and cannot be tested. State the falsifying condition explicitly before proceeding.

### Specificity Check
Ask: "Is the prediction precise enough that a reasonable person would not accept it as confirmed by many different outcomes?"

Vague predictions (e.g., "X will increase Y") can be confirmed by almost any positive result. Specific predictions (e.g., "inhibiting pathway A will reduce Y by at least 30% in condition B, but not condition C") are harder to satisfy and more informative when confirmed.

---

## Phase 3 — Problem Selection Filter (Fischbach & Walsh)

Apply this filter after generating several candidate hypotheses to identify which problem is worth pursuing. Rate each candidate on four axes.

### Generality
How broadly applicable would a positive finding be?

A result that applies to one cell line under one condition has low generality. A result that reveals a mechanism shared across dozens of systems, or that overturns a widely-held assumption, has high generality. High-generality findings tend to have disproportionate downstream impact.

### Learning Value
What will you know regardless of outcome?

The best experiments are informative even if the hypothesis is wrong. A negative result that definitively rules out a mechanism or narrows the parameter space is valuable. Ask: "If the hypothesis is false, does running this experiment still advance understanding?" If the answer is no, reconsider the experimental design.

### Feasibility
Can this be done with available resources, time, and expertise?

Assess honestly: required equipment, data, skills, collaborators, budget, timeline. A high-impact idea that exceeds available resources by 10x is not actionable. Score 1–5 where 5 = fully executable with current resources, 1 = requires resources not obtainable in the foreseeable future.

### Impact
What changes if you succeed?

Map the downstream consequences of a confirmed positive result. Does it open a new therapeutic target? Enable a new class of algorithms? Resolve a long-standing empirical controversy? Change practice in a field? Score 1–5 where 5 = transforms the field or enables major practical advances, 1 = incremental confirmation of something already well-supported.

### Score Interpretation Warning

Feasibility and impact scores (1–5) are only meaningful relative to the user's specific resources, domain, and constraints — which the LLM generating them does not have. These scores should be treated as conversation starters, not recommendations. Every score should be presented with explicit assumptions: "Feasibility score of 4 assumes access to [specific dataset/equipment/expertise]. If [that resource] is not available, this drops to 2." Without stated assumptions, the scores are abstract and potentially misleading. Adjust all scores based on your actual context before acting on them.

---

## Output Format

For each candidate idea, produce the following structured summary:

**Hypothesis statement:** One sentence in the form "If [mechanism], then [prediction] under [conditions]."

**Mechanism:** One paragraph explaining the causal pathway — how and why the effect would occur.

**Falsifiability test:** One sentence describing the specific observation that would refute the hypothesis.

**Feasibility score:** [1–5] — brief justification (2–3 sentences on key resources required and current availability).

**Impact score:** [1–5] — brief justification (2–3 sentences on what changes downstream if confirmed).

**Recommended priority:** [High / Medium / Low] — one sentence rationale integrating generality, learning value, feasibility, and impact.

When evaluating multiple candidates, present them in a comparison table (hypothesis name, feasibility score, impact score, priority) followed by individual detailed entries for the top two or three.
