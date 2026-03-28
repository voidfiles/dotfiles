# Extract Permanent Notes

Transform triaged content into atomic, self-contained permanent notes following Zettelkasten principles. Uses the note-generator agent to create literature notes and permanent notes with connections to existing knowledge.

## Input

- Path (optional): ${1}
  - Specific file path
  - Location (e.g., `Clippings/`, `resources/`)
  - Empty: Process all items with `next_action: extract-notes`
- Current date: !`date +%Y-%m-%d`
- Current time: !`date +%H%M` (for Zettelkasten IDs)

## Task

Create permanent notes that:
- Are atomic (one idea per note)
- Are self-contained (understandable alone)
- Have explicit connections to other notes
- Follow Zettelkasten naming: `YYYYMMDDHHMM Title.md`
- Link bidirectionally to source material

## Process

### Step 1: Find Candidate Items

**If no path provided:**
```bash
# Find all triaged items marked for note extraction
Glob: **/*.md

For each file:
  Read frontmatter
  If next_action: "extract-notes":
    Add to extraction queue
```

**If path provided:**
```bash
# Process specific file or location
Read frontmatter of file(s) in path
Add to extraction queue
```

**Candidates must have:**
- `processed: true` (been triaged)
- `processing_level: layer-2` or higher (has highlights)
- High-value content worth deeper processing

### Step 2: For Each Candidate Item

#### A. Read Source Content

```
Read complete file:
- Frontmatter (metadata, tags, links)
- Layer 2 highlights (==text==)
- Layer 1 bolded passages (**text**)
- Original full content
```

#### B. Extract Key Context

Prepare context for note-generator agent:

```
Source Information:
- File: [file_path]
- Title: [from frontmatter]
- Content type: [article|meeting|note]
- Source URL: [if available]
- Created date: [date]
- Tags: [tags from frontmatter]

Key Insights (from highlights):
[Extract all ==highlighted== passages]

Bolded Passages (supporting context):
[Extract all **bolded** passages]

Connections Mentioned:
[Extract all [[wiki links]] from content]
```

#### C. Launch Note-Generator Agent

Use Task tool to invoke the note-generator agent:

```python
Task(
  subagent_type="deep-reading",
  description="Generate permanent notes from source",
  prompt=f"""
Generate permanent notes from this triaged content following Zettelkasten principles.

SOURCE MATERIAL:
File: {file_path}
Title: {title}
Type: {content_type}
Tags: {tags}

KEY INSIGHTS (highlighted passages):
{highlights}

BOLDED PASSAGES (supporting context):
{bolded_passages}

EXISTING CONNECTIONS:
{wiki_links}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

YOUR TASK:

1. CREATE LITERATURE NOTE:
   - Title: "Literature Note - [Source Title]"
   - 3-5 sentence summary of source in your own words
   - Key arguments and evidence
   - Your critical assessment
   - Links to source material

2. EXTRACT PERMANENT NOTES (atomic ideas):
   - One distinct idea per note
   - Self-contained (understandable without source)
   - Written as complete thoughts (not bullet points)
   - Include examples or applications
   - Typical length: 2-4 paragraphs

3. IDENTIFY CONNECTIONS:
   - How does each note relate to existing notes?
   - Search vault for related concepts
   - Suggest connections with brief explanations

ZETTELKASTEN PRINCIPLES:
- Atomic: One clear idea per note
- Autonomous: Self-contained and understandable alone
- Connected: Explicit links to related ideas
- Personal: Written in your own words, your own understanding

OUTPUT FORMAT:

Return JSON:
{{
  "literature_note": {{
    "title": "Literature Note - [Source Title]",
    "summary": "3-5 sentence summary...",
    "key_arguments": ["argument 1", "argument 2"],
    "assessment": "Your critical thoughts on the material...",
    "tags": ["tag1", "tag2"]
  }},
  "permanent_notes": [
    {{
      "title": "Atomic Idea Title",
      "content": "Full content of permanent note (2-4 paragraphs)...",
      "connections": [
        {{
          "note": "[[Related Note 1]]",
          "relationship": "This builds on / contradicts / applies / extends..."
        }},
        {{
          "note": "[[Related Note 2]]",
          "relationship": "This provides an example of..."
        }}
      ],
      "tags": ["tag1", "tag2"]
    }},
    {{
      "title": "Another Atomic Idea",
      "content": "...",
      "connections": [...],
      "tags": [...]
    }}
  ]
}}

GUIDELINES:
- Extract 2-5 permanent notes (quality over quantity)
- Focus on ideas worth remembering in 5 years
- Make connections specific and meaningful
- Write clearly as if teaching someone
- Include practical applications where relevant
  """
)
```

#### D. Create Literature Note

From agent response, create literature note:

```markdown
---
title: Literature Note - [Source Title]
type: literature-note
source: [[path/to/source/file]]
created: 2026-01-08
tags:
  - literature-note
  - [additional tags from agent]
---

# Literature Note - [Source Title]

## Source
- **Type:** Article/Meeting/Book
- **Original:** [[path/to/source/file]]
- **Date:** YYYY-MM-DD
- **Author:** [if available]
- **URL:** [if available]

## Summary
[3-5 sentence summary from agent in your own words]

## Key Arguments
- [Argument 1]
- [Argument 2]
- [Argument 3]

## Assessment
[Your critical thoughts on the material]

## Permanent Notes Created
- [[YYYYMMDDHHMM Title of Note 1]]
- [[YYYYMMDDHHMM Title of Note 2]]
- [[YYYYMMDDHHMM Title of Note 3]]

## Tags
#literature-note #[additional-tags]
```

**Save to:** `resources/literature-notes/Literature Note - [Source Title].md`

#### E. Create Permanent Notes

For each permanent note from agent response:

**Generate Zettelkasten ID:**
```bash
# Format: YYYYMMDDHHMM (Year Month Day Hour Minute)
# Example: 202601081530 (2026-01-08 15:30)
ID=$(date +%Y%m%d%H%M)

# If multiple notes created in same minute, increment:
# 202601081530, 202601081531, 202601081532, etc.
```

**Create permanent note:**

```markdown
---
title: [Atomic Idea Title]
type: permanent-note
id: 202601081530
created: 2026-01-08
source: [[path/to/source/file]]
literature-note: [[Literature Note - Source Title]]
tags:
  - permanent-note
  - [tags from agent]
connections:
  - "[[Related Note 1]]"
  - "[[Related Note 2]]"
---

# [Atomic Idea Title]

[Full content from agent - 2-4 paragraphs]

[Atomic idea explained clearly and completely]

[Examples or applications if relevant]

## Connections

**[[Related Note 1]]**
[Relationship explanation from agent]

**[[Related Note 2]]**
[Relationship explanation from agent]

## Source
- Literature note: [[Literature Note - Source Title]]
- Original: [[path/to/source/file]]

## Tags
#permanent-note #[additional-tags]
```

**Naming:** `YYYYMMDDHHMM [Title].md`
Example: `202601081530 Progressive Summarization Technique.md`

**Save to:** `resources/permanent-notes/YYYYMMDDHHMM [Title].md`

#### F. Update Source File

Update original triaged file frontmatter:

```yaml
# Update these properties:
processing_level: layer-3  # advanced to Layer 3
permanent_notes:
  - "[[202601081530 Note Title 1]]"
  - "[[202601081531 Note Title 2]]"
  - "[[202601081532 Note Title 3]]"
literature_note: "[[Literature Note - Source Title]]"

# Update distillation tracking:
distillation:
  layer_1_date: 2026-01-05  # existing
  layer_2_date: 2026-01-05  # existing
  layer_3_date: 2026-01-08  # NEW - notes extracted
  layer_4_date: null

# Remove (no longer needed):
# next_action: extract-notes  # REMOVE - action completed
```

#### G. Create Bidirectional Links

Ensure bidirectional linking:

**In permanent note:**
```markdown
## Source
- Literature note: [[Literature Note - Source Title]]
- Original: [[path/to/source/file]]
```

**In literature note:**
```markdown
## Permanent Notes Created
- [[202601081530 Note Title 1]]
- [[202601081531 Note Title 2]]
```

**In source file:**
(Already done in frontmatter)

### Step 3: Generate Extraction Report

After processing all items:

```markdown
# Permanent Note Extraction Report - YYYY-MM-DD

## Summary
- **Items processed:** 3
- **Literature notes created:** 3
- **Permanent notes created:** 8
- **Total time:** ~15 minutes
- **Average per source:** ~5 minutes

---

## Extraction Results

### Source 1: Clippings/AI Agents for Philosophy.md

**Literature Note:**
- [[Literature Note - AI Agents for Philosophy]]
- Location: resources/literature-notes/
- Summary: 4-sentence overview of key arguments

**Permanent Notes Created (3):**
1. [[202601081530 AI Agents as Philosophical Tools]]
   - Connection to: [[Philosophical Method]], [[AI Applications]]
   - Tags: #philosophy #ai #methodology

2. [[202601081531 Argument Analysis Through Computation]]
   - Connection to: [[Logical Reasoning]], [[Computational Thinking]]
   - Tags: #philosophy #logic #ai

3. [[202601081532 Limitations of Algorithmic Philosophy]]
   - Connection to: [[Human Cognition]], [[AI Limitations]]
   - Tags: #philosophy #ai-ethics

**Source Updated:**
- processing_level: layer-2 → layer-3
- Added permanent_notes array (3 notes)
- Added literature_note reference

---

### Source 2: Clippings/Progressive Summarization Technique.md

**Literature Note:**
- [[Literature Note - Progressive Summarization]]
- Location: resources/literature-notes/
- Summary: Technique for distilling information over time

**Permanent Notes Created (2):**
1. [[202601081535 Four Layers of Progressive Distillation]]
   - Connection to: [[Note-Taking Systems]], [[Learning Methods]]
   - Tags: #note-taking #learning #productivity

2. [[202601081536 Evidence-Based Learning Principles]]
   - Connection to: [[Spaced Repetition]], [[Active Recall]]
   - Tags: #learning-science #cognitive-psychology

**Source Updated:**
- processing_level: layer-2 → layer-3
- Added permanent_notes array (2 notes)
- Added literature_note reference

---

### Source 3: Meetings/2025/12/15/Strategy Discussion.md

**Literature Note:**
- [[Literature Note - Q1 Strategy Discussion]]
- Location: resources/literature-notes/
- Summary: Key strategic decisions for Q1 initiatives

**Permanent Notes Created (3):**
1. [[202601081540 Customer-Centric Product Development]]
   - Connection to: [[Product Strategy]], [[User Research]]
   - Tags: #strategy #product #customer-focus

2. [[202601081541 Prioritization Framework for Features]]
   - Connection to: [[Decision Making]], [[Resource Allocation]]
   - Tags: #prioritization #strategy

3. [[202601081542 Balancing Innovation and Stability]]
   - Connection to: [[Risk Management]], [[Technical Debt]]
   - Tags: #strategy #innovation

**Source Updated:**
- processing_level: layer-2 → layer-3
- Added permanent_notes array (3 notes)
- Added literature_note reference

---

## Statistics

**Permanent Notes:**
- Total created: 8 notes
- Average per source: 2.67 notes
- With connections: 8 (100%)
- Average connections per note: 2.25

**Literature Notes:**
- Total created: 3 notes
- Average summary length: 4 sentences
- All include critical assessment: Yes

**Processing:**
- Atomic notes (1 idea): 8 (100%)
- Self-contained: 8 (100%)
- Connected to existing notes: 8 (100%)
- Zettelkasten naming: 8 (100%)

---

## Notes Created (All)

### Permanent Notes
1. [[202601081530 AI Agents as Philosophical Tools]]
2. [[202601081531 Argument Analysis Through Computation]]
3. [[202601081532 Limitations of Algorithmic Philosophy]]
4. [[202601081535 Four Layers of Progressive Distillation]]
5. [[202601081536 Evidence-Based Learning Principles]]
6. [[202601081540 Customer-Centric Product Development]]
7. [[202601081541 Prioritization Framework for Features]]
8. [[202601081542 Balancing Innovation and Stability]]

### Literature Notes
1. [[Literature Note - AI Agents for Philosophy]]
2. [[Literature Note - Progressive Summarization]]
3. [[Literature Note - Q1 Strategy Discussion]]

---

## Connection Graph

**Most Connected Topics:**
- Philosophy: 3 notes
- Strategy: 3 notes
- Learning: 2 notes
- AI: 3 notes

**New Connections Made:**
- To existing note [[Philosophical Method]]: 1 link
- To existing note [[Product Strategy]]: 1 link
- To existing note [[Learning Methods]]: 1 link

---

## Next Steps

1. **Review permanent notes:**
   Read through created notes and refine connections if needed.

2. **Link from existing notes:**
   Review related existing notes and add links back to new permanent notes.

3. **Continue extraction:**
   Run `/scan-inbox` to find more high-value items for extraction.

4. **Use permanent notes:**
   Reference these atomic ideas in your thinking, writing, and projects.

---

Generated: 2026-01-08 15:45
```

Save report to: `/extraction-report-YYYY-MM-DD-HHMM.md`

## Output

**For each processed source:**
- 1 literature note (summary and assessment)
- 2-5 permanent notes (atomic ideas)
- Updated source frontmatter
- Bidirectional links established

**Extraction report:**
- Saved to vault root: `extraction-report-YYYY-MM-DD-HHMM.md`
- Contains all notes created, statistics, connections

**Directory structure:**
```
resources/
├── literature-notes/
│   ├── Literature Note - Source 1.md
│   ├── Literature Note - Source 2.md
│   └── Literature Note - Source 3.md
└── permanent-notes/
    ├── 202601081530 Note Title 1.md
    ├── 202601081531 Note Title 2.md
    ├── 202601081532 Note Title 3.md
    └── ...
```

## Important Notes

### Zettelkasten Principles

**Atomic:**
- One clear idea per permanent note
- Focused and specific
- Not too broad, not too narrow

**Autonomous:**
- Self-contained and understandable without source
- Complete thoughts, not fragments
- Can be read and understood in isolation

**Connected:**
- Explicit links to related ideas
- Connections explain relationships
- Builds knowledge network over time

**Personal:**
- Written in your own words
- Your own understanding and interpretation
- Not just quotes or summaries

### Quality Over Quantity

- 2-5 permanent notes per source is typical
- Not every source needs extraction
- Focus on ideas worth remembering long-term
- Better to have 3 excellent notes than 10 mediocre ones

### Note-Generator Agent

- Leverages existing `.claude/agents/note-generator.md`
- Trained on Zettelkasten principles
- Generates autonomous, atomic notes
- Identifies connections to existing vault notes

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| No highlights in source | Use bolded passages for extraction |
| Source has no bold/highlight | Process full content (slower) |
| Duplicate note ID (same minute) | Increment minute: 1530 → 1531 → 1532 |
| No existing connections found | Create standalone note, connect later |
| Agent finds no atomic ideas | Report: "Source doesn't contain extractable ideas" |

## Example Usage

```bash
# Extract from all items marked extract-notes
/extract-permanent-notes

# Extract from specific file
/extract-permanent-notes "Clippings/AI Agents for Philosophy.md"

# Extract from all articles in Clippings
/extract-permanent-notes Clippings/

# Extract from specific location
/extract-permanent-notes resources/articles/
```

## Testing

Test extraction quality:

```bash
# 1. Extract from one source
/extract-permanent-notes "Clippings/Test Article.md"

# 2. Review output:
#    - Literature note clear and concise?
#    - Permanent notes atomic and self-contained?
#    - Connections meaningful and accurate?
#    - Zettelkasten naming correct?

# 3. Check bidirectional links:
#    - Source → literature note?
#    - Literature note → permanent notes?
#    - Permanent notes → source?

# 4. Verify frontmatter updates:
#    - Source has permanent_notes array?
#    - Source processing_level = layer-3?
```

## Performance

**Expected extraction times:**
- Per source: ~5 minutes (includes agent processing)
- Agent generation: ~2-3 minutes
- Note creation: ~1 minute
- Link updates: ~1 minute

**Batch extraction:**
- 3 sources: ~15 minutes
- 5 sources: ~25 minutes
- 10 sources: ~50 minutes

**Optimization:**
- Process high-value sources only
- Extract in focused sessions
- Review quality regularly
