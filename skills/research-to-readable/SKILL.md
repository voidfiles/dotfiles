---
name: research-to-readable
description: Transform a research report or academic document into a compelling long-form article that reads like great narrative nonfiction. Use this skill when the user says "make this readable", "turn this into an article", "rewrite this for a general audience", "make this fun to read", "convert this research", or wants to transform any dense, citation-heavy, or academic document into engaging prose. Also trigger when the user provides a research report and asks for a "blog post", "essay", "article", or "readable version." This skill applies to research reports, literature reviews, white papers, technical analyses, and synthesis documents.
---

# Research-to-Readable: The Three-Layer Transformation

You are transforming a research report into a long-form article that gets the most valuable information in front of readers as efficiently as possible — while being genuinely enjoyable to read.

The priority is **information delivery**. Let the facts speak for themselves. Your job is to organize, clarify, and connect — not to narrate, dramatize, or editorialize. Every sentence should either deliver a fact, provide necessary context, or synthesize across facts. If it does none of those, cut it.

---

## Voice: Let the Facts Do the Work

The voice is an informed colleague who has done the reading and is giving you the important parts.

**Core principle: No rhetorical flourishes.** Don't announce what you're about to say. Don't narrate the reading experience. Don't write transitions that comment on the material instead of delivering it. Just deliver it.

**Bad:**
> "This reaction — and the forces behind it — explains a puzzle that has frustrated engineering leaders since GPT-3.5 launched in late 2022."

**Good:**
> "That is one of many reasons AI adoption struggles. Here are some others:"

**Bad:**
> "Understanding these barriers — and what actually resolves them — requires looking at each in turn."

**Good:**
> "To resolve adoption issues, we need to understand each barrier and what addresses it."

**Bad:**
> "That's not a junior developer hiding a shortcut. It's a professional engineer at IBM..."

**Good:**
> "A senior engineer at IBM, one of 669 surveyed, describing why social stigma suppresses AI tool adoption..."

**Calibration points:**
- Simple, direct transitions. "Here's why." "There are several reasons." "The data tells a different story."
- No meta-commentary about the research or the article itself
- Drop adjectives that editorialize ("unusually clean," "remarkably precise," "striking"). State the finding; let the reader decide if it's striking.
- Short paragraphs. Rarely more than 3-4 sentences of prose before switching to bullets.

---

## Layer 1: SUBTRACT (Clear the Runway)

Jargon triggers metacognitive resistance — readers monitor their own difficulty and conclude the content is harder and less trustworthy than it actually is. This happens *before* comprehension fails.

**Do this first, before any restructuring:**

- **Kill nominalizations.** "The implementation of the system produced an improvement" → "The team built a system that improved outcomes."

- **Translate jargon through brief inline context.** "Psychological safety — the feeling that you can raise a concern without getting punished for it —" Not a separate definition paragraph.

- **Define novel or technical terms the first time they appear.** If a term like "high-oversight AI roles" appears, give the reader a one-phrase explanation inline. Don't assume domain knowledge for specialized terms, but don't over-explain common concepts either.

- **Use ratios where they land harder, exact numbers where precision matters.** "One in five" beats "20%." But keep "only 3.1%" when the precision is the point.

- **Drop author names and method jargon from the body text.** Don't write "Reich et al. (2026) surveyed 2,257 employees and ran logistic regression on adoption outcomes." Write "2,257 employees surveyed at a global consulting firm found that..." The footnote handles attribution. The reader cares about the finding, not the author or the statistical method.

- **Cut hedging that doesn't earn its keep.** Keep hedging only where genuine uncertainty demands it.

- **Remove method details unless they're the story.** Readers need findings and implications.

---

## Layer 2: STRUCTURE (Pyramid First, Then Depth)

### The Pyramid: Survey Everything Upfront

The introduction gives readers the complete map. Every major theme — problems, infrastructure, solutions, open questions — gets mentioned in the introduction before any deep dive.

**The introduction should:**
1. Open with a hook (a striking quote, counterintuitive stat, or tension — 1-2 sentences max)
2. One short framing sentence connecting the hook to the broader topic
3. A bulleted list surveying ALL major themes with key data points
4. One sentence transitioning to the body: something simple like "To resolve these issues, we need to understand each one."

**Example:**
```markdown
"Obviously I would not want to be seen with generated code in my PRs,
so embarrassing!" [^1] A senior engineer at IBM, one of 669 surveyed,
describing why social stigma suppresses AI tool adoption.

That is one of many reasons AI adoption struggles. Here are some others:

- **Psychological safety is a gate.** A survey of 2,257 employees
  found it predicted whether people adopted AI tools — but not
  how much they used them afterward. [^2]
- **Identity grief hits seniors and juniors differently.** Engineers
  who define themselves by writing code experience AI adoption as
  loss. The split by career stage is sharp. [^3]
- **Infrastructure creates hard ceilings.** AI tools degrade
  predictably against large codebases, with specific documented
  thresholds. [^4]
- **Peer champions beat mandates.** Across 11 practitioner accounts,
  peer endorsement outperformed executive directives. [^5]
- **Cognitive sustainability is a real constraint.** Workers in
  high-oversight AI roles — roles requiring constant monitoring
  and validation of AI output — show 39% higher error rates. [^6]

To address adoption, we need to understand each barrier and what
resolves it.
```

Note: the hook is minimal, the transition is simple, and the bullets do the heavy lifting. No rhetorical buildup.

### Then Go Deep: Problem + Context → Solutions

After the introduction surveys the territory, each section goes deep on one theme. Problems and context come first, solutions and implications come second.

### Bullet-Heavy for Findings, Prose for Synthesis

This is the core formatting principle. When presenting evidence, data, or parallel findings, **default to bullets.** Use prose only when you're synthesizing — connecting dots across findings or explaining why something matters.

**The rhythm:**
1. One framing sentence (what this section is about)
2. Bullets delivering the evidence, with nested bullets for supporting data
3. One synthesis sentence or short paragraph connecting the dots

**Example — presenting adoption data:**
```markdown
## The 84% Adoption Number Is Misleading

This is the adoption depth problem.

- 84% of developers use or plan to use AI tools [^7]
    - But only 3.1% "highly trust" AI output. Nearly half — 45.7% —
      actively distrust it. [^8]
    - Among experienced developers (10+ years), high distrust rises
      to 20.7%, despite equivalent technical access. [^9]
- The gap between "using" and "trusting" is where productivity
  gains disappear
    - 88% of companies report regular AI use [^10]
    - Yet "AI initiatives often stall because employees'
      anxiety about relevance, identity, and job security drives
      surface-level use without real commitment" [^10]
    - Approximately four in five employees harbor significant
      concerns about AI's impact on their careers [^11]

Most engineers will try the tool. Few will reorganize their
professional practice around it.
```

**When to use prose instead of bullets:**
- When you're explaining *why* something happens (cause and effect)
- When two findings create a tension that needs to be held together
- When a quote is powerful enough to stand as a block quote
- When synthesizing across multiple bullet sections

**Keep section-framing language simple.** Avoid elaborate transitions between sections. "There's another dimension to this" or "The solutions look different than expected" is sufficient.

### Keep It Simple

When you're tempted to write something clever or elaborate, write the simpler version instead.

- "Infrastructure creates hard ceilings, not soft friction" → "Infrastructure creates hard ceilings"
- "The distance between those two states is where the interesting dynamics live" → just end the section after the last finding

Interesting phrasing occasionally earns its place (the "gate vs. volume knob" distinction is a keeper because it clarifies a concept). But most clever phrasings just slow the reader down. When in doubt, cut.

---

## Layer 3: ADD (Provide Thrust)

### Use the Best Quotes

A candid, surprising quote does more work than a paragraph of summary. Pull the most vivid quotes from the source material and anchor them with footnotes. Quotes serve as both evidence and rest moments — they break up the analytical voice.

### Concrete Details and Specific Numbers

Every finding should be grounded in specifics — sample sizes, percentages, concrete examples. But the details serve the finding, not the other way around. Don't build narrative scenes around details.

### Use Tension Between Findings

When two findings conflict, present both and let the tension sit. Don't rush to resolve it. "The evidence supports X. But Y complicates this, because..." This is where synthesis earns its keep — connecting what bullets alone can't.

---

## Failure Modes to Avoid

- **Sensationalized titles:** "Why Your Team's AI Adoption Is Stuck at the Shallow End" is clickbait. "AI adoption headwinds and techniques to improve" is descriptive. Titles should describe the content plainly, not sell it.
- **Rhetorical narration:** Announcing what you're about to say, commenting on the material's significance, writing transitions that editorialize. Just deliver the content.
- **Over-narrating:** Building dramatic scenes around findings that would land harder as clean bullet points.
- **TED-ification:** Forcing every finding into an epiphany.
- **Condescension:** Writing for an imagined idiot rather than a curious, intelligent adult who lacks domain-specific knowledge.
- **Undefined jargon:** Using specialized terms without inline context. Define novel terms the first time they appear.
- **Author/method clutter:** Naming researchers or statistical methods in the body text. Let footnotes handle attribution.
- **False certainty:** Stripping all uncertainty from findings.
- **Ornate transitions:** "This reaction — and the forces behind it — explains a puzzle that has frustrated..." → "Here's why:"

---

## Citations: Footnotes with Links

Every quote, data point, and attributed finding gets a footnote marker in the text.

**In-text format:**
```markdown
2,257 employees surveyed at a global consulting firm found that
psychological safety predicted whether employees adopted AI tools. [^1]
```

**Footnote format:**
```markdown
[^1]: Reich, A. et al. (2026). ["Safety First: Psychological Safety
as the Key to AI Transformation."](https://arxiv.org/abs/2602.23279) arXiv.
```

**Rules:**
- Every direct quote gets a footnote
- Every specific data point gets a footnote
- General synthesis in your own voice does not need footnotes
- Preserve URLs from the source material. If no URL exists, format as: `Author (Year). "Title." *Publication*.`
- Number footnotes sequentially
- Drop author names from body text — they belong in footnotes only

---

## Output Structure

```markdown
# [Descriptive Title — what this article covers, plainly stated]

[Hook — 1-2 sentences: striking quote, counterintuitive stat, or tension]

[One simple framing sentence]

[Bulleted survey of ALL major themes — the TL;DR]

[Simple transition sentence]

## [Section heading — finding or tension, not topic label]

[Framing sentence]
[Bullets with evidence and nested supporting data]
[Short synthesis paragraph if needed]

## [Next section...]

...

## What We Still Don't Know

[Bulleted honest gaps]

---

[^1]: Citation with link
[^2]: Citation with link
...
```

### Title and Heading Guidelines

- **Title should be descriptive and straightforward, not sensationalized.** Describe what the article covers plainly. "Report on AI adoption headwinds and techniques to improve" is better than "Why Your Team's AI Adoption Is Stuck at the Shallow End." Don't write clickbait headlines or try to be clever. Just say what it's about.
- **Subtitles are optional.** Only include one if it adds genuinely useful context. Don't use the subtitle to editorialize or create drama.
- Section headings: findings or topics described plainly, not clickbait or provocations
- Never use "Introduction," "Methodology," "Findings," "Conclusion"

### Length

Aim for 40-60% of the original report's word count. Bullets are denser than prose. The result should feel fast.

---

## Process

1. **Read the entire source document.** List ALL major themes.

2. **List the 3-7 most important findings.** Surprising, consequential, or in tension.

3. **Find the best quotes.** Candid, vivid, surprising. These become anchors.

4. **Write the introduction.** Must survey ALL themes with bullets. Reader should be able to stop here and walk away informed.

5. **Draft the body.** Bullet-heavy for findings, prose for synthesis. Problem-context first, solutions second. Simple transitions.

6. **Add footnotes.** Every quote and data point. Drop author names from body text.

7. **Trim.** Read every sentence and ask: is this delivering a fact, providing necessary context, or synthesizing? If none, cut it. Check especially for rhetorical narration, ornate transitions, and meta-commentary.

8. **Run through the humanizer.** After writing the article, invoke the `/humanizer` skill on the output file. This catches residual AI writing patterns — inflated symbolism, em dash overuse, rule of three, magic adverbs, false suspense, and other tells that make text feel machine-generated. The humanizer is the final quality gate before the article is done.
