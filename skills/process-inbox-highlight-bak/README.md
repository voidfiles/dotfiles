---
extracted: false
highlighted: true
highlighted_date: 2026-01-23
processed: false
type: unknown
---
# Process Inbox - Highlight

A skill for applying progressive summarization to inbox items using Claude's API.

## Quick Start

### Basic Usage

```bash
# Highlight all Clippings
/process-inbox-highlight Clippings/

# Highlight a specific file
/process-inbox-highlight "Clippings/Article Title.md"

# Highlight all daily notes
/process-inbox-highlight daily/

# Highlight specific date's notes
/process-inbox-highlight daily/2026/01/23/

# Highlight all meetings
/process-inbox-highlight Meetings/
```

### Advanced Options

```bash
# Re-highlight already processed files
/process-inbox-highlight Clippings/ --force

# Specify custom vault root (for testing)
/process-inbox-highlight Clippings/ --vault-root /path/to/vault
```

## What It Does

### Layer 1 - Bold Key Passages
Identifies and bolds the 10-20% most important passages in each file:
- Core arguments and insights
- Surprising or novel ideas
- Practical takeaways
- Content you'd want to remember in 5 years

Example result: `**This is a key insight about how learning works**`

### Layer 2 - Highlight Essence
From the bolded passages, identifies the 10-20% absolute essence:
- The most critical insights
- Core concepts you must remember
- The "if you only remember 2-3 things" content

Example result: `==**This is the absolute core idea**==`

### Action Items & Decisions (Meetings/Daily Only)
For meetings and daily notes, also extracts:
- **Action Items**: Tasks to complete
- **Decisions**: Decisions made in the meeting
- **Open Questions**: Unresolved topics

Creates a `## Summary` section at the top of the file with:
```markdown
### Action Items
- [ ] Task description - Owner: [[Name]]

### Decisions
1. Decision made with context

### Open Questions
- Open question for follow-up
```

## What Gets Updated

Each file receives:

### Frontmatter
```yaml
---
type: article|daily|meeting|asset
highlighted: true              # Marks file as processed
highlighted_date: 2026-01-23  # When highlighting was applied
extracted: false              # For later stages
processed: false              # For later stages
action_items: []              # For meetings/daily only
decisions: []                 # For meetings/daily only
---
```

### Content
- Key passages get `**bold formatting**`
- Essence passages get `==**highlighted bold**==` formatting
- Summary section added (for meetings/daily with items)

## Content Types

The skill automatically detects file type:
- `Clippings/` → article
- `daily/` → daily notes
- `Meetings/` → meeting transcript
- `assets/` → asset summary

## How to Use in Your Workflow

### Inbox Processing Pipeline

Use as part of the complete CODE method workflow:

1. **Capture** content to `/Clippings/`, `/Meetings/`, or `/daily/`
2. **Highlight** using this skill (Layer 1-2 summarization)
3. **Extract** permanent notes (creates atomic Zettelkasten notes)
4. **Archive** to appropriate PARA locations

### Weekly Inbox Review

```bash
# Monday: Check what's in inbox
/scan-inbox

# Tuesday-Thursday: Process items
/process-inbox-highlight Clippings/ --vault-root /path/to/vault
# ... do manual review and extraction ...

# Friday: Organize into PARA
/process-inbox-archive
```

### Sample Workflow

```bash
# Process new clippings from this week
/process-inbox-highlight Clippings/

# Process today's meeting notes
/process-inbox-highlight Meetings/2026/01/23/

# Process last week's daily notes
/process-inbox-highlight daily/2026/01/20/

# Re-process something that needs better highlighting
/process-inbox-highlight "Clippings/Important Article.md" --force
```

## Output Format

### Highlighted Article Example

**Before:**
```markdown
---
type: article
highlighted: false
---

# Article Title

This is the introduction. Here's a key insight that explains everything.

Some supporting details and evidence.

This is the core concept you need to remember.
```

**After:**
```markdown
---
type: article
highlighted: true
highlighted_date: 2026-01-23
---

# Article Title

This is the introduction. **Here's a key insight that explains everything.**

Some supporting details and evidence.

==**This is the core concept you need to remember.**==
```

### Meeting Notes Example

**After Processing:**
```markdown
---
type: meeting
highlighted: true
highlighted_date: 2026-01-23
action_items:
  - "Implement new feature - Owner: [[Jane Smith]]"
  - "Update documentation"
decisions:
  - "Moving deadline to end of month"
---

## Summary

### Action Items
- [ ] Implement new feature - Owner: [[Jane Smith]]
- [ ] Update documentation

### Decisions
1. Moving deadline to end of month due to resource constraints

### Open Questions
- What's the priority if features conflict?

---

# Meeting Notes

[Original meeting content with bold and highlight formatting...]
```

## Important Notes

### Non-Destructive
- Original content is always preserved
- Only formatting is added (bold and highlight)
- Can re-run with `--force` to re-highlight

### Requires API Key
- Needs `ANTHROPIC_API_KEY` environment variable set
- Uses Claude Haiku model (fast and cost-effective)
- Works offline after API call (content already processed)

### Smart Skipping
- Automatically skips already-highlighted files
- Use `--force` to re-highlight
- Prevents duplicate work in processing

### Preserves Existing Structure
- All existing frontmatter fields preserved
- Only new fields added (highlighted, highlighted_date, etc.)
- Existing formatting respected

## Troubleshooting

### "No markdown files found"
- Check the path is correct
- Use absolute path or path relative to vault root
- Verify files have `.md` extension

### "Error calling Claude API"
- Ensure `ANTHROPIC_API_KEY` is set: `export ANTHROPIC_API_KEY=your-key`
- Check API key is valid
- Verify internet connection

### File not being processed
- Check if already highlighted: `highlighted: true` in frontmatter
- Use `--force` flag to re-process
- Verify file has proper frontmatter with `---` delimiters

### Passages not being bolded
- File might be too short for meaningful passages
- Claude might not identify good passages (returns empty)
- Check file content type is correct (affects prompt)

## Performance

- **Single file**: ~5-10 seconds (API latency)
- **Batch (10 files)**: ~1-2 minutes
- **Large batch (100+ files)**: Processes sequentially

## See Also

- `/process-inbox` - Full pipeline orchestration
- `/process-inbox-extract` - Extract permanent notes
- `/process-inbox-archive` - Archive to PARA
- `/scan-inbox` - Discover unprocessed items
- `CLAUDE.md` - Complete vault management guide
