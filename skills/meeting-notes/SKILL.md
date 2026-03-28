---
name: meeting-notes
description: Transform a meeting transcript into rich, prioritized notes with critical quotes, ranked themes, and cross-references to your vault.
argument-hint: [path-to-meeting-file]
---

# Meeting Notes (Multi-Stage Pipeline)

Transform a meeting transcript into rich, contextualized notes using a 6-stage DAG pipeline with antagonistic refinement.

## Usage

```
/meeting-notes meetings/2026/02/01/standup.md
```

The meeting file should contain the transcript (and optionally pre-meeting notes to preserve).

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      MEETING NOTES DAG                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   [1. STRUCTURE] → [2. THEMES] → [3. CRITIQUE] ←──┐            │
│                                        │          │            │
│                                        ▼          │            │
│                                   [3b. REFINE] ───┘            │
│                                        │                       │
│                                        ▼                       │
│   [4. EXPAND + RANK] → [5. EXTRACT] → [6. CONTEXT + COMPILE]   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**CRITICAL:** Execute stages sequentially. Use TodoWrite to track progress. Do NOT skip the critique step.

---

## Stage 1: Structure Extraction

**Goal:** Extract meeting metadata and build a pool of ALL notable quotes.

### Instructions

1. Read the meeting file at `$ARGUMENTS`
2. Preserve any pre-meeting notes (handwritten content before transcript)
3. Extract:
   - **Date and time** (from filename or content)
   - **Participants** with roles if apparent
   - **Estimated speaking time** per participant (rough %)
   - **Meeting type**: decision | brainstorm | status | planning | 1:1
   - **Duration estimate**

4. **Build the quote pool**: Extract EVERY potentially notable quote. Be generous here; we'll rank later. Look for:
   - Statements of commitment ("I'll have that by...")
   - Decisions ("Let's go with...")
   - Strong opinions ("I really think we need to...")
   - Concerns or risks ("What worries me is...")
   - Insights or realizations ("Oh, that's interesting because...")
   - Questions that shaped discussion
   - Humor or memorable moments that capture tone

### Stage 1 Output (internal)

```yaml
structure:
  date: "YYYY-MM-DD"
  duration_estimate: "X minutes"
  meeting_type: "decision"
  participants:
    - name: "Person Name"
      role: "Title/Role"
      speaking_pct: "40%"
  pre_meeting_notes: |
    [Preserved content]
  quote_pool:
    - quote: "Exact quote text"
      speaker: "Person Name"
      context: "Brief context of when this was said"
```

Mark Stage 1 complete in TodoWrite before proceeding.

---

## Stage 2: Theme Identification

**Goal:** Identify ALL distinct themes/topics. Cast a wide net. Don't rank yet.

### Instructions

1. Read through the transcript looking for topic shifts
2. Identify every distinct theme, even if briefly discussed
3. For each theme, note:
   - Approximate time range or position in transcript
   - Key speakers who contributed
   - Whether it resulted in decisions or remained open

### Theme Identification Prompt

Ask yourself:
- What distinct topics were discussed?
- When did the conversation shift direction?
- What questions or concerns drove different parts of the discussion?
- Were there any tangents worth noting?

### Stage 2 Output (internal)

```yaml
themes_raw:
  - id: 1
    name: "Theme name (descriptive, outcome-oriented)"
    time_range: "early/middle/late or timestamps"
    key_speakers: ["Person A", "Person B"]
    had_decision: true/false
    had_action_items: true/false
```

Mark Stage 2 complete in TodoWrite before proceeding.

---

## Stage 3: Antagonistic Critique (CRITICAL STEP)

**Goal:** Challenge the theme list. Find what's missing or wrong.

### The Critique Protocol

Review your theme list and ACTIVELY LOOK FOR PROBLEMS:

#### 1. OMISSIONS - What's Missing?
- Side conversations that shifted the meeting's direction
- Implicit concerns raised through questions rather than statements
- Topics that were started but tabled ("Let's discuss that later")
- The elephant in the room that no one directly addressed
- Context from previous meetings that informed this one

#### 2. GRANULARITY - Split or Merge?
- Are two "themes" actually the same topic approached differently?
- Is one theme actually two distinct discussions that should be separated?
- Are you capturing symptoms vs. root issues?

#### 3. FRAMING - Named Correctly?
- Are themes named for decisions/outcomes or just discussions?
- Would someone reading just the theme names understand what mattered?
- Are you using insider jargon that won't make sense later?

#### 4. HIDDEN THEMES - What's the Subtext?
- Tensions between participants that shaped the discussion
- Unstated concerns driving surface-level debates
- Political dynamics affecting what got decided (or avoided)
- What DIDN'T get discussed that probably should have?

### Stage 3 Output (internal)

```yaml
critique_findings:
  omissions:
    - "Description of missing theme"
  granularity_issues:
    - "Theme X and Y should be merged because..."
    - "Theme Z should be split into..."
  framing_improvements:
    - "Rename 'Budget discussion' to 'Q2 budget constraints forcing scope cut'"
  hidden_themes:
    - "Tension between engineering and product on timeline"

themes_refined:
  - id: 1
    name: "Improved theme name"
    # ... rest of fields
  - id: 2
    # ... new theme from critique
```

**If critique found significant issues:** Apply refinements and run critique again (max 2 iterations).

Mark Stage 3 complete in TodoWrite before proceeding.

---

## Stage 4: Theme Expansion + Priority Ranking

**Goal:** Deep dive into each theme. Extract detailed notes with quotes. Rank by importance.

### For Each Theme, Extract:

#### Direct Quotes (3-5 per theme)
Select quotes that capture:
- Key decisions or commitments
- Critical insights or realizations
- Points of tension or disagreement
- The essence of the discussion

Format:
```markdown
> "Exact quote from transcript" — Speaker Name
```

#### Key Points
- Bullet points summarizing the discussion
- Include specific numbers, dates, names mentioned
- Note any external references or dependencies

#### Decisions Made
- What was decided (be specific)
- Who made or approved the decision
- What alternatives were considered and rejected
- Any caveats or conditions

#### Open Questions
- What remains unresolved
- Who needs to answer
- Blockers identified

### Priority Scoring

Score each theme on 5 dimensions (1-5 scale):

| Dimension | Weight | What to Assess |
|-----------|--------|----------------|
| Decision Impact | 2x | Was a significant decision made? |
| Action Generation | 1.5x | Did it produce concrete action items? |
| Strategic Importance | 2x | Does it affect long-term direction? |
| Urgency | 1.5x | Does it require immediate follow-up? |
| Participant Energy | 1x | How much engagement/debate? |

**Priority Score** = (Decision×2 + Action×1.5 + Strategic×2 + Urgency×1.5 + Energy×1) / 8

- **High Priority (7-10):** 🔴 Red indicator
- **Medium Priority (4-6.9):** 🟡 Yellow indicator
- **Lower Priority (1-3.9):** 🟢 Green indicator

### Stage 4 Output (internal)

```yaml
themes_expanded:
  - id: 1
    name: "Theme name"
    priority_score: 8.5
    priority_level: "high"  # 🔴
    priority_rationale: "High decision impact, urgent follow-up needed"
    key_points:
      - "Point 1"
      - "Point 2"
    decisions:
      - decision: "What was decided"
        made_by: "Person"
        rationale: "Why"
        rejected_alternatives: ["Option A", "Option B"]
    quotes:
      - quote: "Quote text"
        speaker: "Person"
    open_questions:
      - "Question 1"
```

Mark Stage 4 complete in TodoWrite before proceeding.

---

## Stage 5: Structured Extraction

**Goal:** Extract and organize action items, decisions, and critical quotes across all themes.

### Action Items

For each action item identified:
- **Task:** Clear, actionable description
- **Owner:** Who's responsible (use [[wiki links]])
- **Deadline:** If mentioned (otherwise note "TBD")
- **Priority:** urgent | soon | later
- **Context:** Which theme it came from
- **Quote:** The moment it was assigned (if available)

**IMPORTANT:** Distinguish commitments from suggestions:
- "I'll do X" = action item
- "Maybe we could..." = NOT an action item (note as suggestion if valuable)
- "Can you...?" with affirmative response = action item
- "We should..." without owner = open question, not action item

### Decisions Log

For each decision:
- **Decision:** What was decided
- **Made by:** Who made it
- **Rationale:** Why (in their words if possible)
- **Alternatives rejected:** What was considered but not chosen
- **Supporting quote:** The moment of decision

### Critical Quotes (Meeting-Wide)

Select 3-5 quotes that best capture:
1. The most important outcome of the meeting
2. A key insight or realization
3. The central tension or debate
4. A moment of clarity or resolution
5. The overall tone or energy

For each, note WHY it matters.

### Stage 5 Output (internal)

```yaml
extraction:
  action_items:
    - task: "Description"
      owner: "[[Person]]"
      deadline: "Date or TBD"
      priority: "urgent"
      theme: "Theme name"
      quote: "Assignment quote"

  decisions:
    - decision: "What"
      made_by: "[[Person]]"
      rationale: "Why"
      rejected: ["Alt 1", "Alt 2"]
      quote: "Decision quote"

  critical_quotes:
    - quote: "Quote text"
      speaker: "[[Person]]"
      significance: "Why this matters"
      theme: "Related theme"
```

Mark Stage 5 complete in TodoWrite before proceeding.

---

## Stage 6: Context + Compilation

**Goal:** Cross-reference with vault and compile final output.

### Vault Search

Search for relevant context (last 1-2 weeks):

1. **People mentioned:** Find notes about participants
   - Search: `[[Person Name]]` mentions
   - Check: `/people/` folder if it exists

2. **Topics discussed:** Find related notes
   - Search for theme keywords
   - Check active projects in `/projects/`

3. **Previous meetings:** Find related discussions
   - Same participants
   - Same topics
   - Recent meetings in `/meetings/`

4. **Active projects:** Link to relevant work
   - Check `/projects/` for connections

### Cross-Reference Categories

#### Direct Connections (high confidence)
- Notes explicitly about the same topic
- Projects mentioned in the meeting
- Person notes for participants

#### Thematic Connections (medium confidence)
- Notes on related concepts
- Previous discussions that inform this one
- Patterns across meetings

#### Suggested New Notes
For important topics WITHOUT existing notes, suggest creating:
- Person notes for recurring participants
- Project notes for new initiatives
- Concept notes for recurring themes

### Final Compilation

Assemble the final output following the format below. Themes MUST be ordered by priority score (highest first).

---

## Output Format

Write the final meeting note with this structure:

```markdown
# Meeting: [Descriptive Title] - [Date]

## Pre-Meeting Notes
[Preserve any handwritten notes that existed before processing]

## Participants
- [[Person 1]] - Role (est. X% speaking time)
- [[Person 2]] - Role (est. Y% speaking time)

## Executive Summary

[2-3 sentences capturing the meeting's most important outcomes]

> "[The single most important quote from the meeting]" — Speaker

**Key outcome:** [One sentence on the primary result]

## Critical Quotes

> "[Quote 1]" — Speaker
> **Why it matters:** [Brief explanation]

> "[Quote 2]" — Speaker
> **Why it matters:** [Brief explanation]

> "[Quote 3]" — Speaker
> **Why it matters:** [Brief explanation]

## Themes (Priority Order)

### 🔴 Theme 1: [Highest Priority Theme]
**Priority:** 8.5/10 — [Brief rationale: e.g., "Major decision made, urgent follow-up"]

#### Key Points
- Point 1
- Point 2

#### Decisions
- **[Decision]**
  - Made by: [[Person]]
  - Rationale: [Why]
  > "[Supporting quote]" — Speaker

#### Notable Quotes
> "[Quote]" — Speaker

#### Related: [[project]], [[concept]]

---

### 🟡 Theme 2: [Medium Priority Theme]
**Priority:** 5.5/10 — [Rationale]

[Same structure as above]

---

### 🟢 Theme 3: [Lower Priority Theme]
**Priority:** 3.0/10 — [Rationale]

[Same structure as above]

## Action Items

### 🔴 Urgent (This Week)
- [ ] [Action] — @[[Person]] — Due: [Date]
  > "[Quote that spawned this]" — Speaker

### 🟡 Soon (This Month)
- [ ] [Action] — @[[Person]]

### 🟢 Later / Ongoing
- [ ] [Action] — @[[Person]]

## Decisions Log

| Decision | Made By | Rationale | Rejected Alternatives |
|----------|---------|-----------|----------------------|
| [What] | [[Person]] | [Why] | [Options not chosen] |

## Open Questions
- [ ] [Question] — Needs answer from: [[Person]]
- [ ] [Question] — Blocker for: [what it blocks]

## Context & Cross-References

### This Meeting Connects To
- [[Active Project]]: [Specific connection]
- [[Previous Meeting]]: [How thinking evolved]
- [[Person Note]]: [Relevant background]

### Thematic Connections
- [[Related Concept]]: [Why relevant]

### Suggested New Notes
- **[[Proposed Title]]**: [Why this deserves its own note]

---

## Processing Metadata

- **Processed:** [timestamp]
- **Stages completed:** structure ✓ themes ✓ critique ✓ expand ✓ extract ✓ context ✓
- **Critique iterations:** [1 or 2]
- **Themes identified:** [N] → refined to [M]

---

## Transcript

[Full original transcript preserved here]
```

---

## Important Guidelines

### Quote Handling
- Use EXACT quotes from the transcript
- Preserve speaker attribution always
- Don't paraphrase in quote blocks
- It's okay to truncate with [...] for very long quotes

### Priority Ranking
- Be honest about priority; not everything is urgent
- A meeting with no 🔴 themes is fine
- Priority should reflect ACTUAL importance, not time spent

### Linking
- Use [[wiki links]] for all people, projects, concepts
- Link to existing notes; don't invent links to non-existent notes
- In "Suggested New Notes," propose notes worth creating

### Preservation
- NEVER delete pre-meeting notes
- ALWAYS preserve the full transcript at the end
- The processed note should be strictly additive

### The Critique Step
- This is the most important innovation
- Don't skip it even for "simple" meetings
- Simple meetings often have hidden themes

---

## Example Critique in Action

**Before critique:**
```
Themes:
1. Q1 planning
2. Budget
3. Hiring
```

**After critique:**
```
Critique findings:
- OMISSION: "Q1 planning" and "Budget" are intertwined; the real theme is
  "Budget constraints forcing Q1 scope reduction"
- HIDDEN: Tension between Sarah (wants to hire) and John (wants to ship with
  current team) was never directly addressed but shaped the whole discussion
- FRAMING: "Hiring" is too generic; actual discussion was "Whether to delay
  launch to onboard new engineer"

Refined themes:
1. Budget constraints forcing Q1 scope reduction (merged Q1 planning + Budget)
2. Launch timing vs. team capacity tradeoff (reframed Hiring)
3. Sarah-John alignment gap on growth vs. delivery (new hidden theme)
```

---

## Troubleshooting

**Long transcripts (45+ min):** The pipeline handles this naturally by breaking into stages. Each theme gets focused attention in Stage 4.

**No clear decisions:** Some meetings are exploratory. That's fine. Score themes on strategic importance and participant energy instead of decision impact.

**Unclear speakers:** Note uncertainty with "(unclear speaker)" or "(possibly John)". Don't guess if genuinely ambiguous.

**Pre-meeting notes mixed with transcript:** Identify the boundary. Preserve pre-meeting notes in their own section.
