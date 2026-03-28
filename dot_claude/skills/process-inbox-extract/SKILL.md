---
argument-hint: file path or folder, e.g., "Clippings/Article.md" or "daily/2026/01/"
description: Analyze highlighted inbox items and generate YAML extraction suggestions mapping content to PARA destinations with proposed integration notes.
name: process-inbox-extract
---
# Process Inbox - Extract

Analyze highlighted inbox items and generate extraction suggestions as a YAML file for human review. This skill:
- Analyzes content for relevance to existing projects/areas
- Suggests new projects/areas if appropriate
- Writes suggestions to a YAML file in `.claude/processing/`
- Does NOT make any changes - only generates suggestions for review

## Workflow Overview

```
/process-inbox-extract → generates YAML → human reviews → /process-vault applies approved changes
```

This skill generates suggestions. The `/process-vault` orchestrator handles review and apply.

## Input

- File path or folder to process
- Current date: !`date +%Y-%m-%d`

## Prerequisites

Items should be highlighted first (`highlighted: true` in frontmatter).
If an item is not highlighted, skip it and suggest running `/process-inbox-highlight` first.

## Output Location

All suggestion files are written to:
```
.claude/processing/extract-suggestions/
```

Each run creates a timestamped YAML file:
```
.claude/processing/extract-suggestions/{timestamp}-suggestions.yaml
```

## Process

### Step 1: Determine Target Items

**If file path provided:**
```
Process single file: ${1}
```

**If folder provided:**
```bash
# Scan folder for markdown files
Glob: ${1}/**/*.md or ${1}/*.md

# Filter for items ready for extraction:
# - Files WITH highlighted: true
# - AND WITHOUT extracted: true (or extracted: false)
```

### Step 2: Check Eligibility

For each item:
```
Read frontmatter

If highlighted != true:
    Log: "Skipping {file} - not yet highlighted. Run /process-inbox-highlight first."
    Continue to next item

If extracted == true:
    Log: "Skipping {file} - already extracted"
    Continue to next item
```

### Step 3: Read and Analyze Content

```python
content = Read(item)

# Focus on highlighted (==**text**==) and bolded (**text**) passages
highlights = extract_highlighted(content)  # ==**text**==
bolded = extract_bolded(content)           # **text**

# These represent the key insights identified during highlighting
```

### Step 4: Scan Projects and Areas

```bash
# Get all projects
Glob: projects/*/index.md
Glob: projects/**/index.md

# Get all areas
Glob: areas/*/
Glob: areas/**/

# Read project/area descriptions for richer context
For each project index.md:
    Extract: H1 title, first paragraph, and any "scope"/"goals" sections
    (not just first 500 chars, get the semantic structure)
```

Build a context of available projects and areas:
```
PROJECTS:
- projects/ai-research/ - "Research on AI capabilities and applications"
  Goals: Evaluate agent architectures, benchmark reasoning
- projects/second-brain/ - "Building personal knowledge management system"
  Scope: Obsidian vault processing, PARA methodology
...

AREAS:
- areas/health/ - Ongoing health and fitness tracking
- areas/career/ - Career development and skills
...
```

### Step 5: Generate Association Suggestions

Use LLM to analyze content and suggest associations:

```
PROMPT:
Analyze this content for associations with existing Projects and Areas.

CONTENT TITLE: {filename}
CONTENT TYPE: {type}

HIGHLIGHTED PASSAGES (essence - most important):
{highlights}

BOLDED PASSAGES (key points):
{bolded}

EXISTING PROJECTS:
{list of project names and descriptions}

EXISTING AREAS:
{list of area names}

Analyze this content and suggest:
1. An `essence` field: 1-3 sentences distilling what this note is fundamentally about
2. Which existing projects/areas it relates to
3. Whether new projects or areas should be created
4. What notes should be created - INCLUDING the actual key ideas to include

Guidelines:
- Generate a 1-3 sentence `essence` per source that captures the fundamental insight
- Only suggest HIGH relevance associations for strong connections
- MEDIUM for tangential but useful connections
- LOW for weak connections (usually skip these)
- Suggest new projects only if there's clear evidence of an emerging initiative
- Suggest new areas only if content doesn't fit existing areas
- Be conservative - fewer high-quality associations are better than many weak ones
- If no strong PARA association exists, explicitly say so with rationale (don't force weak connections)
- CRITICAL: Extract ACTUAL ideas, not just descriptions. The key_ideas should contain
  the distilled insights themselves, rewritten in clear language, not "this note would
  contain insights about X". The project/area note must be valuable on its own.
- Integration notes must be standalone-readable: actual insights rewritten in clear
  language, with a "How This Applies" or "Implications" section
```

### Step 6: Write Suggestions to YAML File

Create the processing directory if needed:
```bash
mkdir -p .claude/processing/extract-suggestions/
```

Write all suggestions to a single YAML file:

```yaml
# .claude/processing/extract-suggestions/{timestamp}-suggestions.yaml
# Generated: 2026-01-23T10:30:00
# Source: Clippings/ (or specific file path)
# Status: pending_review

metadata:
  generated: "2026-01-23T10:30:00"
  source_path: "Clippings/"
  items_processed: 3
  items_skipped: 1
  status: pending_review

items:
  - source_file: "Clippings/AI Philosophy Article.md"
    source_title: "AI Philosophy Article"
    source_type: article
    essence: "AI agents exhibit emergent philosophical reasoning patterns, including implicit argument detection and Socratic dialogue, suggesting dialectical architectures improve agent robustness."
    highlighted_passages:
      - "AI agents can identify implicit philosophical arguments..."
      - "Socratic dialogue patterns emerge in multi-agent reasoning..."

    associations:
      - target: "projects/ai-research"
        type: project
        relevance: high
        reason: "Content directly relates to AI capabilities research"
        status: pending  # pending | approved | rejected | skipped

        note_to_create:
          path: "projects/ai-research/AI Philosophy Applications.md"
          title: "AI Philosophy Applications"
          content: |
            ---
            source: "[[Clippings/AI Philosophy Article]]"
            created: 2026-01-23
            type: extracted-insight
            ---

            # AI Philosophy Applications

            Insights from philosophical analysis of AI agent behavior and reasoning patterns.

            ## Key Ideas

            - **Implicit argument detection**: AI agents can identify unstated philosophical
              arguments embedded in text, revealing assumptions that human readers often miss.

            - **Socratic dialogue emergence**: When multiple agents interact, natural Socratic
              dialogue patterns emerge, with agents questioning each other's premises.

            - **Edge case robustness**: Philosophy-trained models demonstrate better handling
              of edge cases, likely due to exposure to thought experiments and edge-case reasoning.

            ## Implications for AI Research

            These findings suggest our agent architecture should incorporate dialectical
            reasoning patterns. Consider adding a "devil's advocate" agent to challenge
            conclusions before finalizing outputs.

            ## Source

            Extracted from [[Clippings/AI Philosophy Article]].

      - target: "areas/learning"
        type: area
        relevance: medium
        reason: "Contains methodology insights for learning"
        status: pending

        note_to_create:
          path: "areas/learning/Dialectical Learning Methods.md"
          title: "Dialectical Learning Methods"
          content: |
            ---
            source: "[[Clippings/AI Philosophy Article]]"
            created: 2026-01-23
            type: extracted-insight
            ---

            # Dialectical Learning Methods

            Insights on learning through questioning and counter-arguments.

            ## Key Takeaways

            - Questioning assumptions accelerates understanding by forcing explicit
              examination of premises
            - Counter-arguments strengthen mental models by stress-testing conclusions

            ## How This Applies

            When learning new concepts, actively generate counter-arguments and
            alternative explanations. This dialectical approach builds more robust
            understanding than passive consumption.

            ## Source

            Extracted from [[Clippings/AI Philosophy Article]].

    new_creations:
      - name: "Philosophy of AI"
        type: project
        reason: "Multiple related items suggest an emerging research interest"
        description: "Research and notes on philosophical aspects of AI"
        status: pending

  - source_file: "Clippings/Another Article.md"
    source_title: "Another Article"
    source_type: article
    highlighted_passages:
      - "Key passage 1..."

    associations: []
    new_creations: []
    no_associations_reason: "Content is standalone reference material, no strong project/area connections"

skipped_items:
  - file: "Clippings/Not Highlighted.md"
    reason: "Not yet highlighted (highlighted: false)"
  - file: "Clippings/Already Done.md"
    reason: "Already extracted (extracted: true)"

summary:
  total_associations_suggested: 2
  total_new_creations_suggested: 1
  items_with_no_associations: 1

next_steps: |
  Review this file and update status fields:
  - Change 'pending' to 'approved' for suggestions you want to apply
  - Change 'pending' to 'rejected' for suggestions you don't want
  - Optionally edit note content before approval

  Then run: /process-vault --apply .claude/processing/extract-suggestions/{timestamp}-suggestions.yaml
```

### Step 6b: Update Source Frontmatter

For each processed item, update frontmatter to mark extraction complete:

```yaml
extracted: true
extracted_date: {today}
```

This is critical for idempotency. Without it, re-running extract processes the same files again.

### Step 7: Generate Summary Output

After writing the YAML file, output a summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXTRACTION SUGGESTIONS GENERATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Output file: .claude/processing/extract-suggestions/2026-01-23T103000-suggestions.yaml

Processed: 3 items
Skipped: 1 item (not highlighted or already extracted)

Suggestions generated:
- 2 project/area associations
- 1 new project creation
- 1 item with no associations (standalone)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEP: REVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Review and apply via the orchestrator:
  /process-vault --apply .claude/processing/extract-suggestions/2026-01-23T103000-suggestions.yaml

Or manually edit the YAML file and change 'status: pending' to 'approved' or 'rejected'.
```

---

# Process Inbox - Review

Review extraction suggestions and approve, reject, or request changes. This is called after `/process-inbox-extract` generates suggestions.

## Input

- Path to suggestions YAML file (from extract step)
- Example: `.claude/processing/extract-suggestions/2026-01-23T103000-suggestions.yaml`

## Process

### Step 1: Load Suggestions File

```python
suggestions = Read(yaml_file_path)
# Parse YAML content
```

### Step 2: Present Each Item for Review

For each item with pending associations or new_creations:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REVIEW: {source_title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Source: {source_file}
Type: {source_type}

Highlighted passages:
  • "{passage_1}..."
  • "{passage_2}..."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ASSOCIATION 1 of N: [{relevance}] → {target}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Target: {target} ({type})
Reason: {reason}

Note to create: {note_path}
───────────────────────────────────────────────────────
{note_content_preview - first 500 chars}
───────────────────────────────────────────────────────

Options:
  [A] Approve - create this note as-is
  [R] Reject - skip this association
  [E] Edit - modify the note content
  [S] Skip - decide later (keep pending)
  [V] View full - see complete note content

Choice:
```

Use AskUserQuestion tool for each decision.

### Step 3: Handle User Choices

**If Approved:**
```yaml
# Update status in YAML
status: approved
```

**If Rejected:**
```yaml
# Update status in YAML
status: rejected
```

**If Edit requested:**
1. Show full note content
2. Ask user what changes they want
3. Apply changes to the `content` field
4. Re-present for approval

```
What changes would you like to make?

Options:
  - Change title
  - Edit key ideas
  - Modify implications section
  - Change target location
  - Custom edit (describe changes)
```

After edits, update the YAML:
```yaml
status: approved
note_to_create:
  content: |
    {updated content with user's changes}
review_notes: "User edited: changed title, added context about X"
```

**If Skip:**
```yaml
# Keep status as pending
status: pending
```

### Step 4: Handle New Creations

For suggested new projects/areas:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEW PROJECT SUGGESTED: {name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type: {project|area}
Reason: {reason}
Description: {description}

Options:
  [A] Approve - create this {type}
  [R] Reject - don't create
  [E] Edit - modify name/description
  [S] Skip - decide later

Choice:
```

### Step 5: Save Updated YAML

After all reviews, write the updated YAML file:

```yaml
metadata:
  generated: "2026-01-23T10:30:00"
  source_path: "Clippings/"
  items_processed: 3
  status: reviewed  # Changed from pending_review
  reviewed_date: "2026-01-23T11:45:00"

items:
  - source_file: "Clippings/AI Philosophy Article.md"
    associations:
      - target: "projects/ai-research"
        status: approved  # Was: pending
        # ... rest unchanged

      - target: "areas/learning"
        status: rejected  # Was: pending
        rejection_reason: "Not relevant to current learning goals"

    new_creations:
      - name: "Philosophy of AI"
        status: approved
        # ...
```

### Step 6: Generate Review Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REVIEW COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reviewed: 3 items

Associations:
  ✓ Approved: 2
  ✗ Rejected: 1
  ⏸ Pending: 0

New creations:
  ✓ Approved: 1
  ✗ Rejected: 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEXT STEP: APPLY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Apply the approved changes:
  /process-vault --apply .claude/processing/extract-suggestions/2026-01-23T103000-suggestions.yaml

This will:
  - Create 2 notes in projects/areas
  - Create 1 new project
  - Update source file frontmatter
```

## Review Modes

### Interactive Mode (default)
- Present each suggestion one at a time
- Wait for user decision before continuing
- Good for careful review of small batches

### Batch Mode (--batch)
- Show summary of all suggestions
- Allow bulk approve/reject by relevance level
- Good for processing many items quickly

```
Batch review options:
  [1] Approve all HIGH relevance (3 items)
  [2] Approve HIGH + MEDIUM (5 items)
  [3] Review each individually
  [4] Reject all and skip extraction

Choice:
```

## Important Notes

### Edits are Preserved
- User edits to note content are saved in the YAML
- Original suggestion preserved in `original_content` field if edited
- Review notes captured for audit trail

### Partial Reviews OK
- Can review some items and skip others
- Re-run review to continue with pending items
- Already-reviewed items show their status but can be changed

### No Files Modified Yet
- Review step only updates the YAML file
- Actual note creation happens in `/process-inbox-apply`
- Safe to review multiple times before applying

## YAML Schema Reference

### Status Values

```yaml
status: pending   # Not yet reviewed
status: approved  # Will be applied
status: rejected  # Will be skipped
status: skipped   # Explicitly skipped (preserved for record)
```

### Item Structure

```yaml
items:
  - source_file: string       # Path to source file
    source_title: string      # Title from frontmatter or filename
    source_type: string       # article|daily|meeting|asset
    essence: string           # 1-3 sentence distillation of what this note is fundamentally about
    highlighted_passages:     # Key passages from source
      - string

    associations:             # Suggested links to projects/areas
      - target: string        # Path to project/area
        type: project|area
        relevance: high|medium|low
        reason: string        # Why this association makes sense
        status: pending|approved|rejected

        note_to_create:       # The actual note to create
          path: string        # Full path for the new note
          title: string       # Note title
          content: string     # Complete markdown content (with frontmatter)

    new_creations:            # Suggested new projects/areas
      - name: string
        type: project|area
        reason: string
        description: string
        status: pending|approved|rejected

    no_associations_reason: string  # If no associations, explain why
```

## Important Notes

### No Direct Changes (except frontmatter)
- This skill generates suggestions and marks source files `extracted: true`
- No integration notes are created (those happen via `/process-vault`)
- YAML file is the proposal, frontmatter is the durable state

### Note Content is Complete
- The `content` field contains the FULL note ready to write
- Includes frontmatter, headings, and all text
- Reviewer can edit content directly in YAML before approving

### Conservative Suggestions
- Quality over quantity
- HIGH relevance associations only for strong connections
- It's okay to have items with no associations

### Idempotency
- Skip items already extracted (`extracted: true`)
- Each run creates a new timestamped file (won't overwrite)

## Edge Cases

### No Eligible Items Found
```yaml
metadata:
  generated: "2026-01-23T10:30:00"
  source_path: "Clippings/"
  items_processed: 0
  items_skipped: 5
  status: no_items

items: []

skipped_items:
  - file: "Clippings/File1.md"
    reason: "Already extracted"
  # ...

summary:
  message: "No eligible items found for extraction"

next_steps: |
  All items in this folder have either been extracted already or need highlighting first.
  Run /process-inbox-highlight on items that need highlighting.
```

### No Associations for an Item
```yaml
- source_file: "Clippings/Random Article.md"
  source_title: "Random Article"
  highlighted_passages:
    - "Some interesting but unrelated content..."

  associations: []
  new_creations: []
  no_associations_reason: |
    This content doesn't strongly relate to any existing projects or areas.
    Consider filing in resources/ as general reference material.
```
