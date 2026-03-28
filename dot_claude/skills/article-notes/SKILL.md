---
name: article-notes
description: Transform a web article or clipping into rich, analyzed notes with thesis mapping, insight ranking, critical analysis, and vault cross-references.
argument-hint: [path-to-clipping-file]
---

# Article Notes (Multi-Stage Pipeline)

Transform an article or clipping into rich, contextualized notes using a 6-stage DAG pipeline with antagonistic critique.

## Usage

```
/article-notes Clippings/Context Engineering for Agents.md
```

The article should ideally be highlighted first (`/process-inbox-highlight`), but this is not required.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      ARTICLE NOTES DAG                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   [1. STRUCTURE] → [2. ARGUMENTS] → [3. CRITIQUE] ←──┐         │
│                                        │             │         │
│                                        ▼             │         │
│                                   [3b. REFINE] ──────┘         │
│                                        │                       │
│                                        ▼                       │
│   [4. INSIGHTS + RANK] → [5. EXTRACT] → [6. CONTEXT + COMPILE] │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**CRITICAL:** Execute stages sequentially. Use TodoWrite to track progress. Do NOT skip the critique step.

---

## Stage 1: Structure Extraction

**Goal:** Extract article metadata and build a pool of ALL notable passages.

### Instructions

1. Read the article file at `$ARGUMENTS`
2. Preserve any existing highlighted content (==**text**==)
3. Extract:
   - **Author** (from content or filename)
   - **Source URL** (if present)
   - **Publication date** (if available)
   - **Article type**: opinion | research | how-to | news | analysis | essay | tutorial
   - **Word count and reading time estimate**
   - **Core thesis** (1-2 sentences summarizing the main argument)

4. **Build the quote pool**: Extract EVERY potentially notable passage. Be generous here; we'll rank later. Look for:
   - Central claims ("The key insight is...")
   - Supporting evidence (data, citations, examples)
   - Surprising assertions ("Counterintuitively...")
   - Practical recommendations ("You should...")
   - Memorable phrases or metaphors
   - Conclusions and implications

### Stage 1 Output (internal)

```yaml
structure:
  author: "Author Name"
  source_url: "https://..."
  publication_date: "YYYY-MM-DD or null"
  article_type: "analysis"
  word_count: 2500
  read_time_minutes: 10
  core_thesis: |
    One or two sentences capturing the central argument
  quote_pool:
    - quote: "Exact quote text"
      context: "Brief context of where this appears"
      type: claim | evidence | recommendation | insight
```

Mark Stage 1 complete in TodoWrite before proceeding.

---

## Stage 2: Argument Mapping

**Goal:** Map the article's logical structure — claims, evidence, and reasoning flow.

### Instructions

1. Identify the **main claims** the author makes
2. For each claim, note the **supporting evidence**:
   - Data and statistics
   - Examples and case studies
   - Citations and appeals to authority
   - Logical reasoning
3. Identify **counterarguments** the author addresses (or ignores)
4. Map the **logical flow**: how does the argument build?

### Argument Mapping Prompts

Ask yourself:
- What is the author trying to convince me of?
- What evidence do they provide for each claim?
- Are there implicit claims that aren't stated directly?
- How do the sections connect logically?
- What would someone who disagrees say?

### Stage 2 Output (internal)

```yaml
argument_map:
  main_claims:
    - id: 1
      claim: "Description of claim"
      evidence:
        - type: data | example | citation | logic
          description: "What evidence supports this"
          strength: strong | moderate | weak
      counterarguments_addressed:
        - "Counterargument the author responds to"

  logical_flow: |
    Brief description of how the argument builds:
    - Opens with [X]
    - Builds case through [Y]
    - Concludes with [Z]

  implicit_claims:
    - "Unstated assumptions the argument relies on"
```

Mark Stage 2 complete in TodoWrite before proceeding.

---

## Stage 3: Antagonistic Critique (CRITICAL STEP)

**Goal:** Challenge the article's argument. Find what's missing, weak, or biased.

### The Critique Protocol

Review the argument map and ACTIVELY LOOK FOR PROBLEMS:

#### 1. OMISSIONS - What's Missing?
- Evidence the author should have included but didn't
- Perspectives or viewpoints not represented
- Obvious counterarguments not addressed
- Context that would change interpretation
- Limitations the author doesn't acknowledge

#### 2. ASSUMPTIONS - What's Unstated?
- Beliefs the argument requires to be true
- Background knowledge the author assumes readers share
- Value judgments embedded in the framing
- Causal claims that aren't proven

#### 3. BIASES - What Viewpoint Shapes This?
- Author's professional or ideological lens
- Selection bias in examples chosen
- Confirmation bias in evidence cited
- Audience the author is writing for
- Incentives that might shape the argument

#### 4. EVIDENCE QUALITY - How Strong Is It?
- Is the evidence sufficient for the claims?
- Are citations reliable and relevant?
- Are statistics used correctly?
- Could the examples be cherry-picked?
- Is correlation being treated as causation?

#### 5. IMPLICATIONS - What's Not Considered?
- Second-order effects the author ignores
- Who might be harmed by this advice?
- Edge cases where the argument breaks down
- Long-term consequences not addressed

### Stage 3 Output (internal)

```yaml
critique_findings:
  omissions:
    - "Missing perspective or evidence"
  assumptions:
    - "Unstated belief the argument requires"
  biases:
    - "Potential bias affecting the analysis"
  evidence_issues:
    - claim_id: 1
      issue: "Why evidence is weak or insufficient"
  unconsidered_implications:
    - "Consequence the author doesn't address"

  overall_assessment:
    strengths:
      - "What the article does well"
    weaknesses:
      - "Main limitations"
    trustworthiness: high | medium | low
    reasoning: "Why this trust level"
```

**If critique finds significant issues:** Note them for the final output. Consider how they affect which insights are worth extracting.

Mark Stage 3 complete in TodoWrite before proceeding.

---

## Stage 4: Insight Extraction + Priority Ranking

**Goal:** Extract actionable insights and rank by importance to the reader.

### For Each Potential Insight, Extract:

#### The Insight Itself
- Clear, standalone statement of the idea
- Not just a summary — the actual transferable knowledge

#### Supporting Quote
```markdown
> "Exact quote from article" — Author
```

#### Why It Matters
- How this changes thinking or behavior
- What problem it solves

#### How to Apply
- Concrete next step or application

### Priority Scoring

Score each insight on 5 dimensions (1-5 scale):

| Dimension | Weight | What to Assess |
|-----------|--------|----------------|
| Actionability | 2x | Can I apply this to my work/life? |
| Novelty | 2x | Does this challenge my assumptions? |
| Project Relevance | 1.5x | Does it relate to active projects? |
| Evidence Strength | 1x | How well-supported is this insight? |
| Memorability | 1x | Is this worth remembering long-term? |

**Priority Score** = (Actionability×2 + Novelty×2 + Relevance×1.5 + Evidence×1 + Memorability×1) / 7.5

- **High Priority (7-10):** 🔴 Red indicator
- **Medium Priority (4-6.9):** 🟡 Yellow indicator
- **Lower Priority (1-3.9):** 🟢 Green indicator

### Stage 4 Output (internal)

```yaml
insights:
  - id: 1
    insight: "Clear statement of the insight"
    priority_score: 8.5
    priority_level: "high"  # 🔴
    priority_rationale: "High actionability, novel to my current thinking"
    quote: "Supporting quote"
    why_it_matters: "Explanation of significance"
    how_to_apply: "Concrete next step"
    evidence_strength: strong | moderate | weak
    caveats:
      - "Any limitations from critique stage"
```

Mark Stage 4 complete in TodoWrite before proceeding.

---

## Stage 5: Permanent Note Extraction

**Goal:** Generate 1-3 atomic permanent notes for the most valuable insights.

### Criteria for Permanent Notes

Only create permanent notes for insights that:
- Are genuinely novel or reframe existing knowledge
- Have clear applications beyond this specific article
- Would be valuable to reference months or years later
- Can stand alone without context from the source

### Permanent Note Format

Each note should be atomic (one concept) and include:

```markdown
---
source: "[[Clippings/Original Article Title]]"
created: YYYY-MM-DD
type: permanent-note
tags: [relevant, topic, tags]
---

# [Insight Title - Descriptive and Searchable]

[2-3 paragraphs explaining the insight in your own words. This should be valuable on its own, not just a pointer to the source. Include:]

## The Core Idea

[Clear statement of the concept]

## Why This Matters

[Significance and implications]

## How to Apply

[Practical applications]

## Evidence and Caveats

[What supports this, and what limitations exist]

## Related

- [[Related Note 1]]
- [[Related Note 2]]

---

*Extracted from [[Clippings/Original Article Title]]*
```

### Stage 5 Output (internal)

```yaml
permanent_notes:
  - title: "Note Title"
    insight_id: 1  # Links to insight from Stage 4
    target_path: "resources/topic/Note Title.md"
    content: |
      [Full markdown content of the note]
```

Mark Stage 5 complete in TodoWrite before proceeding.

---

## Stage 6: Context + Compilation

**Goal:** Cross-reference with vault and compile final output.

### Vault Search

Search for relevant context:

1. **Projects:** Check `/projects/` for active work this relates to
   - Search for topic keywords
   - Check project descriptions

2. **Areas:** Check `/areas/` for ongoing domains
   - Health, career, learning, etc.

3. **Resources:** Check `/resources/` for related notes
   - Previous notes on similar topics
   - Authors or sources previously encountered

4. **Previous Clippings:** Find related articles
   - Same topic
   - Same author
   - Conflicting perspectives

### Cross-Reference Categories

#### Direct Connections (high confidence)
- Notes explicitly about the same topic
- Active projects this informs
- Previous articles by same author

#### Thematic Connections (medium confidence)
- Notes on related concepts
- Methodological similarities
- Contrasting viewpoints

#### Suggested Follow-up
- What to read next
- Questions to research
- Experiments to try

### Final Compilation

Assemble the final output following the format below. Insights MUST be ordered by priority score (highest first).

---

## Output Format

Write the final article note with this structure:

```markdown
---
analyzed: true
analyzed_date: YYYY-MM-DD
author: "Author Name"
source_url: "URL"
article_type: analysis
trustworthiness: high|medium|low
---

# Article: [Title] — [Author]

## Source & Metadata
- **Author:** [Name]
- **Source:** [Publication/URL]
- **Date:** [Publication date]
- **Type:** [opinion/research/etc.]
- **Read time:** ~X min
- **Trustworthiness:** 🟢/🟡/🔴 [high/medium/low]

## Executive Summary

[2-3 sentences capturing the core argument and its significance]

> "[The single most important quote]" — Author

**Core thesis:** [One sentence]

## Key Insights (Priority Order)

### 🔴 [Highest Priority Insight]
**Score:** 8.5/10 — [Brief rationale]

> "[Supporting quote]"

**Why it matters:** [Explanation]

**How to apply:** [Actionable next step]

**Caveats:** [Any limitations from critique]

---

### 🟡 [Medium Priority Insight]
**Score:** 5.5/10 — [Rationale]

[Same structure as above]

---

### 🟢 [Lower Priority Insight]
**Score:** 3.0/10 — [Rationale]

[Same structure as above]

## Argument Structure

### Main Claims
1. **[Claim 1]**
   - Evidence: [Supporting data/examples]
   - Strength: 🟢/🟡/🔴

2. **[Claim 2]**
   - Evidence: [Supporting data/examples]
   - Strength: 🟢/🟡/🔴

### Logical Flow
[How the argument builds from premise to conclusion]

## Critical Analysis

### Strengths
- [What the article does well]

### Limitations & Gaps
- [What's missing or weak]
- [Unstated assumptions]
- [Potential biases]

### Counterarguments Not Addressed
- [What opposing views are ignored]

## Permanent Notes Created

1. [[resources/topic/Insight Title 1]] — [Brief description]
2. [[resources/topic/Insight Title 2]] — [Brief description]

## Context & Cross-References

### Related to Projects
- [[projects/project-name]]: [How it connects]

### Related Notes in Vault
- [[resources/existing-note]]: [Connection]

### Contrasting Viewpoints
- [[Clippings/Opposing Article]]: [How it disagrees]

### Suggested Follow-up
- [What to read/research next]
- [Questions this raises]

---

## Processing Metadata

- **Analyzed:** [timestamp]
- **Stages completed:** structure ✓ arguments ✓ critique ✓ insights ✓ extract ✓ context ✓

---

## Original Content

[Full original article content preserved here, with existing highlights]
```

---

## Important Guidelines

### Quote Handling
- Use EXACT quotes from the article
- Preserve author attribution
- It's okay to truncate with [...] for very long quotes
- Prefer quotes that are already highlighted (==**text**==)

### Priority Ranking
- Be honest about priority; not everything is high-value
- An article with no 🔴 insights is fine
- Priority should reflect value to YOU, not general importance

### Linking
- Use [[wiki links]] for all notes, projects, concepts
- Link to existing notes; don't invent links to non-existent notes
- Permanent notes should be created in appropriate locations

### Preservation
- ALWAYS preserve the full original content at the end
- Keep any existing highlights and formatting
- The processed note should be additive, not destructive

### The Critique Step
- This is the most important innovation
- Don't skip it even for articles you agree with
- Articles you agree with often have hidden assumptions

---

## Example Critique in Action

**Before critique:**
```
Main claims:
1. AI agents need context engineering
2. Four strategies: write, select, compress, isolate
3. Multi-agent architectures help with context
```

**After critique:**
```
Critique findings:
- ASSUMPTION: Article assumes readers have LLM context window familiarity
- OMISSION: Doesn't address cost implications of different strategies
- BIAS: Author works at LangChain, so framework-specific examples may be biased
- EVIDENCE: Claims about multi-agent performance cite only one source (Anthropic)
- IMPLICATION: "Compression" via summarization risks losing critical details

Refined understanding:
- The four strategies are useful taxonomy, but evidence varies in strength
- Write/Select strategies have strong evidence (multiple sources)
- Compress/Isolate strategies have weaker evidence (fewer examples)
- Cost-performance tradeoffs not addressed but are crucial for real applications
```

---

## Troubleshooting

**Long articles (3000+ words):** The pipeline handles this naturally by breaking into stages. Focus on the most important claims and insights.

**No clear thesis:** Some articles are exploratory. Note this in the structure, focus on individual insights rather than overall argument.

**Already highlighted:** Use existing highlights as starting points for the quote pool. Don't re-highlight.

**Highly technical content:** Focus on extracting transferable principles, not technical details.

**Opinion pieces:** Emphasize the critique step. Opinion pieces often have weaker evidence but may have valuable perspectives.
