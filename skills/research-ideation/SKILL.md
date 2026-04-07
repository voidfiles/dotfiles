---
name: research-ideation
description: Generate, formulate, and filter research ideas through four phases — divergent ideation, question expansion, hypothesis formulation, and problem selection — using the Fischbach & Walsh framework to prioritize by generality, learning value, feasibility, and impact.
---

# Research Ideation

## When to Use

- Choosing a new research direction or thesis topic
- Generating candidate hypotheses from observations or preliminary data
- Evaluating whether a problem is worth pursuing before investing significant effort
- Breaking out of a narrow framing to find more promising angles
- Preparing a project pitch or proposal and needing to stress-test the idea
- Expanding or evolving research questions before committing to a direction

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

## Phase 2 — Question Expansion

Phase 1 produces raw candidate directions. Before formalizing them into testable hypotheses, this phase widens and deepens those directions through structured expansion techniques. The purpose is to make sure you haven't locked in too early — that you've explored the full shape of the question space before committing.

This phase is interactive. Present the menu of techniques below and let the user choose which ones to apply. Not every technique suits every question — some questions benefit most from cross-disciplinary reframing, others from assumption interrogation or recursive deepening. Let the user's intuition guide selection.

### Technique Menu

Present these options to the user. For each, give a one-line description and ask which they'd like to explore. Typical sessions use 2–4 techniques — enough to meaningfully expand the question set without exhaustion.

---

### 1. Assumption Interrogation

Surface the hidden premises embedded in the current framing, then use each as a lever to generate alternative questions.

**How to run this conversationally:**

1. Take the user's current research question(s) from Phase 1.
2. Identify 3–5 assumptions baked into the framing. These might be assumptions about causality, about which variables matter, about the population of interest, about the timescale, or about what counts as a valid outcome.
3. Present them to the user: "Here are assumptions I see embedded in your question. Which of these feel shakiest or most worth challenging?"
4. For each assumption the user flags, generate an alternative research question that drops or inverts it.
5. Ask: "What would need to be false for your original question to be meaningless?" — this often surfaces the deepest assumption of all.

**Example dialogue:**
> Your question assumes the effect operates at the individual level. What if the relevant unit is the team, the organization, or the network? That reframes the question from "why do individuals X?" to "what structural conditions produce X?"

---

### 2. Cross-Disciplinary Pollination

LLMs have absorbed patterns across many fields. This technique exploits that to find **structural isomorphisms** — problems that look different on the surface but share deep formal similarities.

**How to run this conversationally:**

1. Ask: "What's the core dynamic in your question — what's the abstract pattern?" (e.g., competition for a scarce resource, cascading failure, information asymmetry, adaptation under pressure)
2. Once the user names the dynamic, identify 2–3 distant fields that study the same dynamic under different names.
3. For each field, translate the user's question into that field's language and ask: "Does this translation suggest a mechanism or method you hadn't considered?"
4. Look for frameworks or metaphors that import cleanly. A supply chain optimization lens applied to neural pathway efficiency. An epidemiological model applied to information spread. An evolutionary fitness landscape applied to startup strategy.

The value here isn't in the analogy itself — it's in the specific mechanism or method the analogy imports that wasn't visible from within the original field.

---

### 3. Systematic Dimension Expansion

Decompose the question along orthogonal axes to find versions of it that might be more interesting, more tractable, or more impactful than the original.

**Walk through each dimension with the user:**

| Dimension | Guiding question |
|---|---|
| **Scale** | What does this look like at the individual / group / institutional / civilizational level? |
| **Temporality** | How does this change over milliseconds vs. decades vs. centuries? |
| **Negation** | What's the inverse? What if you studied the *absence* of this phenomenon? |
| **Mechanism vs. Function** | Are you asking *how* this works or *why* it exists? What happens if you switch? |
| **Boundary conditions** | Under what conditions does this question become trivial? Under what conditions does it become impossible? |

For each dimension, generate the expanded version of the question and ask the user: "Is this more interesting than the original? Does it suggest a different entry point?"

Boundary conditions are especially productive — they often reveal where the interesting science actually lives (at the edges, not the center).

---

### 4. Literature Gap Detection

Help the user identify questions that live in the spaces between existing bodies of work.

**How to run this conversationally:**

1. Ask the user to name 2–3 literatures or theoretical traditions their question touches.
2. For each pair of literatures, ask: "What questions sit in the gap between these two that neither addresses directly?"
3. Also ask: "What's the obvious question in this space that seems surprisingly under-studied? What would a newcomer to the field be shocked no one has answered yet?"
4. Probe for empirical anomalies: "What phenomenon would be surprising or unexplained from the perspective of [the dominant theory]?"

**Important caveat to share with the user:** LLMs can suggest directions and framings, but they hallucinate citations and can confabulate the state of a literature. Use this technique to generate *candidate* gaps, then verify against actual literature before investing. The `/paper-lookup` and `/literature-review` skills can help with verification.

---

### 5. Conceptual Stress-Testing

Use devil's advocate reasoning to sharpen and pressure-test the questions before they become hypotheses.

**Run through these prompts with the user:**

- "What's the strongest methodological critique of this question as currently framed?"
- "If you found a strong positive result, what are 3 alternative explanations a skeptical reviewer would raise?"
- "What would make this question more precise? More falsifiable? More consequential?"
- "Is this question actually asking what you think it's asking, or is there a deeper question hiding underneath?"

The goal isn't to kill the question — it's to find the version of it that can survive scrutiny. Questions that emerge from stress-testing are more likely to produce publishable, defensible work.

---

### 6. Generative Combinatorics

Map the combinatorial space of possible questions from the user's building blocks.

**How to run this conversationally:**

1. Ask the user to list:
   - Their core constructs (3–5 key concepts or variables)
   - Their available methods (what they can actually measure or manipulate)
   - Their populations or systems of interest
2. Generate the full combinatorial matrix of possible questions from these inputs.
3. Flag the combinations that seem most novel or under-explored — especially those the user hadn't considered.
4. Present the matrix and ask: "Which of these combinations surprises you? Which feels like it's been hiding in plain sight?"

This is especially useful when the user has been circling the same 2–3 questions and needs to see the broader possibility space their ingredients support.

---

### 7. Recursive Deepening (The "5 Whys")

Surface the deeper motivating question that the surface-level question is actually serving.

**How to run this conversationally:**

1. Start with the user's current question.
2. Ask: "Why does the answer to this question matter?"
3. Take their answer and ask "why does *that* matter?" again.
4. Repeat 4–5 times, or until the user hits bedrock — a question they care about for its own sake, not as a means to something else.
5. Compare the deep question to the surface question. Sometimes the deep question is more interesting, more publishable, or more tractable. Sometimes it confirms the surface question was the right one all along.

This technique often reveals that the user's real question is 2–3 levels below where they started. The surface question was a proxy for something they hadn't articulated yet.

---

### Wrapping Up Phase 2

After running the selected techniques, consolidate the results:

1. Present the full set of expanded/evolved questions alongside the originals from Phase 1.
2. Ask the user: "Looking at all of these, which directions feel most alive? Which ones do you want to carry forward into hypothesis formulation?"
3. The user selects 2–5 questions to advance to Phase 3.

The point of expansion is not to keep expanding forever — it's to make sure the questions entering Phase 3 are the strongest, most interesting versions of themselves.

---

## Phase 3 — Hypothesis Formulation

Take the selected questions from Phase 2 and make them precise enough to test.

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

## Phase 4 — Problem Selection Filter (Fischbach & Walsh)

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
