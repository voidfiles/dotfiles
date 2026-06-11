---
extracted: false
highlighted: true
highlighted_date: 2026-01-23
processed: false
type: unknown
---
# Process Inbox - Highlight Implementation

This document describes the implementation of the `process-inbox-highlight` skill.

## Overview

The `process-inbox-highlight` skill applies progressive summarization (Layer 1-2) to inbox items:
- **Layer 1**: Identifies and bolds 10-20% of key passages
- **Layer 2**: Highlights 10-20% of bolded passages as the essence
- **Extra for Meetings/Daily**: Extracts action items, decisions, and open questions

## Architecture

### File Structure

```
.claude/skills/process-inbox-highlight/
├── SKILL.md              # Skill definition and instructions
├── IMPLEMENTATION.md     # This file
└── scripts/
    └── highlight.py      # Main implementation script
```

### Key Components

#### 1. `highlight.py` - Main Implementation

A Python script that orchestrates the highlighting process:

**Core Functions:**

- `get_vault_root()` - Calculates the vault root path from the script location
- `parse_frontmatter()` - Extracts YAML frontmatter from markdown files
- `build_frontmatter()` - Reconstructs frontmatter from dictionary
- `detect_content_type()` - Determines content type from file path
- `call_claude_api()` - Calls Claude API to identify passages and extract metadata
- `extract_json_from_response()` - Parses JSON from Claude responses
- `identify_key_passages()` - Uses Claude to identify Layer 1 passages
- `identify_essence_passages()` - Uses Claude to identify Layer 2 essence
- `extract_action_items()` - Extracts action items for meetings/daily notes
- `apply_formatting()` - Applies bold and highlight formatting
- `process_file()` - Main processing logic for a single file
- `find_files()` - Locates files to process
- `main()` - Entry point and CLI argument parsing

### Processing Pipeline

#### Step 1: File Discovery
- Accepts file path or folder argument
- Converts relative paths to absolute paths using vault root
- Recursively finds all markdown files in directories

#### Step 2: Frontmatter Parsing
- Extracts existing frontmatter (if present)
- Checks if file already has `highlighted: true`
- Skips files unless `--force` flag is used

#### Step 3: Content Type Detection
- Determines type from path: `Clippings/` → article, `daily/` → daily, `Meetings/` → meeting, `assets/` → asset
- Uses detected type in Claude prompts for context-aware processing

#### Step 4: Layer 1 Passage Identification
Calls Claude with prompt to identify key passages:
```
You are helping with progressive summarization (Layer 1).
[content]
Return JSON with "passages" array of exact text matches
```

#### Step 5: Layer 2 Essence Identification
Calls Claude with the bolded passages:
```
From these bolded key passages, identify the 10-20% core essence
Return JSON with "essence" array of exact text matches from passages
```

#### Step 6: Formatting Application
- Replaces identified passages with `**passage**` (bold)
- Replaces identified essence with `==**passage**==` (highlighted bold)
- Handles edge cases like already-formatted text

#### Step 7: Action Item Extraction (Meetings/Daily Only)
For meetings and daily notes, calls Claude to extract:
- Action items (task descriptions with optional owners)
- Decisions made
- Open questions

Creates summary section at top of file if items found:
```markdown
## Summary

### Action Items
- [ ] Task description

### Decisions
1. Decision description

### Open Questions
- Question 1

---
```

#### Step 8: Frontmatter Update
Updates frontmatter with:
- `highlighted: true` - Marks file as processed
- `highlighted_date: YYYY-MM-DD` - Timestamp
- `action_items: [...]` - For meetings/daily (if present)
- `decisions: [...]` - For meetings/daily (if present)
- Preserves all existing frontmatter fields

#### Step 9: File Write
Writes updated content with new formatting back to file

### Output Format

**File Content Structure:**
```markdown
---
type: article
highlighted: true
extracted: false
processed: false
highlighted_date: 2026-01-23
action_items: []  # For meetings/daily only
decisions: []     # For meetings/daily only
---

## Summary  # Only if action items/decisions exist

### Action Items
- [ ] Task 1

### Decisions
1. Decision 1

### Open Questions
- Question 1

---

Original content with **bold passages** and ==**highlighted essence**==
```

## API Integration

### Claude API
- Uses Anthropic SDK to call Claude API
- Model: `claude-haiku-4-5-20251001`
- Max tokens: 4096 per request
- Requires `ANTHROPIC_API_KEY` environment variable

### Prompt Strategy
- Uses JSON-formatted responses for reliable parsing
- Includes clear guidelines in prompts
- Handles edge cases (already formatted text, no good passages)

## Usage Examples

### Process all Clippings
```bash
python .claude/skills/process-inbox-highlight/scripts/highlight.py Clippings/
```

### Process specific folder
```bash
python .claude/skills/process-inbox-highlight/scripts/highlight.py daily/2026/01/
```

### Process single file
```bash
python .claude/skills/process-inbox-highlight/scripts/highlight.py "Clippings/Article.md"
```

### Re-highlight already processed file
```bash
python .claude/skills/process-inbox-highlight/scripts/highlight.py "Clippings/Article.md" --force
```

### Specify custom vault root
```bash
python .claude/skills/process-inbox-highlight/scripts/highlight.py Clippings/ --vault-root /path/to/vault
```

## Error Handling

### API Failures
- If Claude API call fails, returns empty lists for passages
- File still marked as `highlighted: true` to avoid infinite retry loops
- Error logged to stderr

### Missing Files
- Gracefully handles files that don't exist
- Shows helpful error message with path checked

### Malformed Frontmatter
- Recreates frontmatter if missing
- Preserves all existing frontmatter fields
- Handles both YAML-style lists and simple values

### Text Matching
- Uses exact string matching to find passages
- Skips passages that can't be found in content
- Logs warnings for unmatched passages
- Doesn't double-format already-bold or highlighted text

## Edge Cases Handled

1. **No frontmatter** - Creates default frontmatter
2. **Already highlighted** - Skips unless `--force` flag
3. **Large files** - Works with files >10,000 words
4. **Special characters** - Handles in text matching
5. **Multi-line passages** - Correctly applies formatting
6. **Unicode/emojis** - Properly handled in file paths and content
7. **Assets** - Only processes `summary.md` in asset folders
8. **Empty content** - Returns empty passage lists

## Performance Characteristics

- **Single file**: ~5-10 seconds (API latency dependent)
- **Batch processing**: Sequential - processes files one at a time
- **Memory**: Low - streams files and only keeps current file in memory
- **API calls**: 2-3 per file (Layer 1, Layer 2, optional extraction)

## Testing

### Test with Sample File
```bash
# Create test file without highlighting
cat > /tmp/test.md << 'EOF'
---
type: article
highlighted: false
extracted: false
processed: false
---

Content here...
EOF

# Process it
python .claude/skills/process-inbox-highlight/scripts/highlight.py /tmp/test.md
```

### Verify Output
Check that file now has:
- `highlighted: true` in frontmatter
- `**bold passages**` in content
- `==**highlighted essence**==` in content
- `highlighted_date` set to today

## Future Enhancements

1. **Concurrent Processing** - Process multiple files in parallel
2. **Batch Mode** - Process many files with consolidated Claude calls
3. **Custom Thresholds** - Allow configuring 10-20% percentages
4. **Progressive Layers** - Support Layer 3-4 for deeper distillation
5. **Integration** - Hook into larger processing pipeline
6. **Caching** - Cache Claude responses for identical content
7. **Configuration** - YAML config file for defaults
8. **Rollback** - Track versions for re-highlighting

## Related Skills

This skill is part of the inbox processing pipeline:
- `scan-inbox` - Discover unprocessed items
- `process-inbox-highlight` - Apply Layer 1-2 summarization (this skill)
- `process-inbox-extract` - Generate atomic notes
- `process-inbox-archive` - Move to final locations

See `/Users/alex/Dropbox/obsidian/Alex3/CLAUDE.md` for integration details.
