---
argument-hint: file path or folder, e.g., "Clippings/Article.md" or "daily/2026/01/"
description: Apply Layer 1-2 progressive summarization (bold key passages, highlight essence) to inbox items. For meetings and daily notes, also extracts action items and decisions.
name: process-inbox-highlight
---
# Process Inbox - Highlight

Apply Layer 1-2 Progressive Summarization to inbox items:
- **Layer 1**: Bold 10-20% of key passages
- **Layer 2**: Highlight 10-20% of bolded essence

For meetings and daily notes, also extract action items and decisions.

## Input

- File path or folder to process
- Current date: !`date +%Y-%m-%d`

## Frontmatter Schema

Items should have or will receive this frontmatter:

```yaml
---
type: article|daily|meeting|asset
highlighted: false
extracted: false
processed: false
highlighted_date: null
---
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

# Filter for unhighlighted items:
# - Files WITHOUT highlighted: true in frontmatter
# - OR files with highlighted: false
```

### Step 2: Skip if Already Highlighted

For each item:

Read frontmatter
If highlighted: true:
    Log: "Skipping {file} - already highlighted"
    Continue to next item

### Step 3: Detect Content Type

Determine content type from path:

If path contains "Clippings/" → type: article
If path contains "daily/" → type: daily
If path contains "Meetings/" → type: meeting
If path contains "assets/" → type: asset (process summary.md)

### Step 4: Read and Understand Content

Read entire file content
Extract main themes and topics for context
For assets: Read the summary.md file within the asset folder

### Step 5: Identify Key Passages (Layer 1 - Bold)

Use LLM to identify the 10-20% most important passages.

Content-type-specific guidance:
- **article**: Focus on novel claims, evidence-backed arguments, actionable frameworks, surprising data
- **meeting**: Focus on decisions made, commitments given, open questions, strategic directions
- **daily**: Focus on patterns noticed, reflections, commitments to self, mood/energy shifts
- **asset**: Focus on core thesis, key frameworks, memorable examples, actionable takeaways

Guidelines:
- Select passages that someone would want to remember in 5 years
- Prioritize: core arguments > evidence > examples
- Each passage should be at least 1-3 sentences, but can be longer if needed
- Multiple paragraphs are okay if they form a coherent thought
- Total bolded content should be ~10-20% of the content
- Return EXACT text matches (for reliable replacement)
- Do NOT include any text that is already bold (**text**) or highlighted (==text==)

### Step 6: Apply Bolding

For each passage:

Find passage in content
Replace with: **passage**

If passage spans multiple paragraphs: Bold each paragraph separately: **paragraph1**\n\n**paragraph2**


### Step 7: Identify Essence (Layer 2 - Highlight)

From bolded passages, identify the absolute essence:

You are helping with progressive summarization (Layer 2 - essence).

From these bolded key passages, identify the 10-20% that represent the absolute core essence - the most important insights you'd want to remember.

Guidelines:
- These are the insights that matter most
- If you could only remember 2-3 things from this content, what would they be?
- Total highlighted should be ~10-20% of bolded content
- Return EXACT text matches from the bolded passages

### Step 8: Apply Highlighting

For each essence passage in the response:

Find **passage** in content
Replace with: ==**passage**==


### Step 9: Write Updated Content

Use Edit tool to update the file with:
- Updated frontmatter
- Bold formatting applied
- Highlight formatting applied
- Summary section (for meetings/daily)

## Output

**For each processed file:**
- Content updated with **bold** and ==**highlight**== formatting
- Frontmatter updated with `highlighted: true` and date
- Original content preserved (non-destructive - only formatting added)

**Summary output:**
```
Highlighted X items:
1. Clippings/Article1.md - 5 passages bolded, 2 highlighted
2. daily/2026/01/20/notes.md - 3 passages bolded, 1 highlighted, 2 action items extracted
...
```

## Important Notes

### Preservation
- **Original content always preserved** - only formatting added
- **All existing frontmatter preserved** - only new/updated properties added
- **Non-destructive** - can be re-run if needed

### Text Matching
- Match passages EXACTLY to avoid breaking formatting
- Handle edge cases like quotes, special characters
- If exact match fails, log warning and skip that passage

### Large Files
For files >10,000 words:
```
Warning: This file is very long ({word_count} words)
Processing may take longer than usual.
```

### Already Formatted Content
- Skip text that is already bold or highlighted
- Don't double-apply formatting

## Edge Cases

### Missing Frontmatter
```
File has no frontmatter

Create frontmatter section with default values:
---
type: {detected from path}
highlighted: true
extracted: false
processed: false
highlighted_date: {today}
---
```

### Re-processing Request
```
File already has highlighted: true

Ask user: "Re-highlight this item? This will replace existing bold/highlight formatting. (y/n)"
If yes:
  - Remove existing **bold** and ==highlight== formatting
  - Re-process
  - Add reprocessed_date to frontmatter
```

### No Good Passages Found
```
LLM couldn't identify meaningful passages

Log: "No key passages identified for {file}. Content may be too short or unclear."
Set highlighted: true anyway (to avoid re-processing)
Add note to frontmatter: highlight_note: "No key passages identified"
```

### Passage Not Found in Content
```
Passage from LLM response doesn't match content exactly

Log: "Warning: Could not find passage in content: {first 50 chars}..."
Skip that passage, continue with others
```

### Asset Files
```
For assets/, process the summary.md file:
assets/{name}/summary.md

Do NOT process other files in the asset folder (chunks, original, etc.)
```
