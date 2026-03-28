---
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Skill
argument-hint: "[file/folder or YAML path, e.g., 'Clippings/Article.md' or '.claude/processing/extract-suggestions/2026-03-01-suggestions.yaml']"
context: fork
description: Archive extracted inbox content to appropriate locations, updating all wiki links. Supports direct file/folder mode and YAML suggestions file mode. Only archives content types that require archiving (articles, assets). Daily notes and meetings stay in place.
model: haiku
name: process-inbox-archive
version: 1.0.0
---
# Process Inbox - Archive

Archive extracted inbox items to their appropriate locations in the vault. This skill:
- Moves articles to `archive/Clippings/`
- Moves asset files (except summary) to `archive/assets/`
- Moves asset summaries to `resources/`
- Uses the `move-file` skill to maintain wiki link integrity
- Skips content types that don't archive (daily notes, meetings)

## Archive Rules by Content Type

| Content Type | Archive? | Destination |
|--------------|----------|-------------|
| Articles (`Clippings/`) | YES | `archive/Clippings/` |
| Daily Notes (`daily/`) | NO | Stay in place |
| Meetings (`Meetings/`) | NO | Stay in place |
| Assets (`assets/`) | PARTIAL | See below |

### Asset Archive Rules
Assets have special handling:
- `summary.md` → `resources/{topic}/` (extracted knowledge stays accessible)
- All other files → `archive/assets/{asset_name}/` (original files archived)

## Input Modes

### Mode 1: File/Folder (existing behavior)
- File path or folder to process
- Current date: !`date +%Y-%m-%d`

### Mode 2: YAML Suggestions File (new)
- Path to a reviewed YAML suggestions file (from `/process-inbox-extract`)
- Detects YAML mode when argument ends in `.yaml`
- Processes only items with `status: approved` associations

## Prerequisites

**File/folder mode:** Items should be extracted first (`extracted: true` in frontmatter).
Content must be eligible for archiving (articles or assets only).

**YAML mode:** Accept items with approved associations in YAML even if frontmatter `extracted` isn't set (YAML is proof of extraction in this mode).

## Frontmatter Schema

```yaml
---
type: article|daily|meeting|asset
highlighted: true
extracted: true            # Required - must be extracted first
processed: false           # Will become true after archiving
processed_date: null       # Will be set after archiving
archived_to: null          # Will contain archive path
---
```

## Process

### Step 1: Determine Target Items

**If file path provided:**
```
Process single file/folder: ${1}
```

**If folder provided:**
```bash
# Scan folder for markdown files
Glob: ${1}/**/*.md or ${1}/*.md

# Filter for items ready for archiving:
# - Files WITH extracted: true
# - AND WITHOUT processed: true (or processed: false)
# - AND content type supports archiving (article, asset)
```

### Step 2: Check Eligibility

For each item:
```
Read frontmatter
content_type = frontmatter.type OR detect_from_path(item)

# Skip types that don't archive
If content_type in ["daily", "meeting"]:
    Log: "Skipping {file} - {content_type} type does not archive"
    Continue to next item

# Check extraction status
If extracted != true:
    Log: "Skipping {file} - not yet extracted. Run /process-inbox-extract first."
    Continue to next item

# Check if already processed
If processed == true:
    Log: "Skipping {file} - already archived"
    Continue to next item
```

### Step 3: Determine Archive Destination

**For Articles (Clippings/):**
```python
# Clippings/Article Name.md → archive/Clippings/Article Name.md
source = "Clippings/Article Name.md"
destination = "archive/Clippings/Article Name.md"
```

**For Assets:**
```python
# Asset folder: assets/{asset_name}/
# Contains: summary.md, chunk_summary.md, headers.md, {name}.md, original file, chunks/

asset_folder = "assets/{asset_name}/"

# Summary goes to resources
# Determine topic from frontmatter or content analysis
topic = get_topic_from_content(summary)  # e.g., "software-engineering", "ai", "health"
summary_dest = f"resources/{topic}/{asset_name}_summary.md"

# Everything else goes to archive
archive_dest = f"archive/assets/{asset_name}/"
```

### Step 4: Create Destination Directories

```bash
# Ensure archive directories exist
mkdir -p archive/Clippings/
mkdir -p archive/assets/
mkdir -p resources/{topic}/  # For asset summaries
```

### Step 5: Archive Files Using move-file Skill

**CRITICAL**: Use the existing `move-file` skill to maintain wiki link integrity.

**For Articles:**
```bash
# Use move-file skill
uv run .claude/skills/move-file/scripts/move_file.py \
    "Clippings/{article}.md" \
    "archive/Clippings/{article}.md"
```

**For Assets:**
```bash
# Step 1: Move summary to resources
uv run .claude/skills/move-file/scripts/move_file.py \
    "assets/{asset_name}/summary.md" \
    "resources/{topic}/{asset_name}_summary.md"

# Step 2: Move entire remaining folder to archive
uv run .claude/skills/move-file/scripts/move_file.py \
    "assets/{asset_name}/" \
    "archive/assets/{asset_name}/"
```

### Step 6: Update Frontmatter (Before Move)

Before moving the file, update its frontmatter:

```yaml
# Update these fields
processed: true
processed_date: 2026-01-22
archived_to: archive/Clippings/  # or resources/{topic}/ for summaries
```

### Step 7: Verify Move Success

After moving, verify:
```bash
# Check destination exists
ls -la {destination}

# Check source is gone
ls -la {source}  # Should not exist

# Check links were updated
# The move-file skill reports link updates
```

### Step 8: Generate Archive Report

```markdown
# Archive Report - 2026-01-22

## Archived Items

### Articles (3 items)

1. **Clippings/AI Agents for Philosophy.md**
   - Archived to: archive/Clippings/AI Agents for Philosophy.md
   - Wiki links updated: 2 files

2. **Clippings/Context Engineering.md**
   - Archived to: archive/Clippings/Context Engineering.md
   - Wiki links updated: 5 files

3. **Clippings/Software Design.md**
   - Archived to: archive/Clippings/Software Design.md
   - Wiki links updated: 0 files

### Assets (1 item)

1. **assets/building_a_second_brain/**
   - Summary moved to: resources/productivity/building_a_second_brain_summary.md
   - Other files moved to: archive/assets/building_a_second_brain/
   - Total files archived: 8
   - Wiki links updated: 12 files

## Skipped (Not Archivable)

- daily/2026/01/20/notes.md (daily notes don't archive)
- Meetings/2026/01/19/standup.md (meetings don't archive)
- Clippings/New Article.md (not yet extracted)

## Summary

- Total items archived: 4
- Total wiki links updated: 19
- Errors: 0
```

## Output

**For each archived item:**
- File moved to archive location
- Wiki links updated across vault
- Frontmatter updated with `processed: true` and archive path

**Summary output:**
```
Archived X items:
1. Clippings/Article1.md → archive/Clippings/Article1.md (2 links updated)
2. assets/book_name/ → archive/assets/book_name/ + resources/topic/summary.md (8 links updated)
...
```

## Important Notes

### Wiki Link Integrity
- ALWAYS use the `move-file` skill for all file moves
- Never use raw `mv` command - it breaks wiki links
- The move-file skill handles all link format variations

### Preservation
- Frontmatter is updated BEFORE the move
- Original content is preserved exactly
- Only the location changes

### Asset Special Handling
- Summary.md is the valuable extracted knowledge - goes to resources/
- Original files, chunks, etc. go to archive/ (can be retrieved if needed)
- The asset folder structure is preserved in archive/

### Determining Asset Topic
For asset summaries, determine the topic from:
1. Frontmatter `topic` or `category` field if present
2. Frontmatter `associated_areas` if present
3. Content analysis of summary.md
4. Fall back to a generic topic based on content

## Edge Cases

### Destination Already Exists
```
Destination file exists: archive/Clippings/Article.md

Options:
1. Rename to: archive/Clippings/Article_2026-01-22.md
2. Overwrite existing (not recommended)
3. Skip this file

Choose option (1/2/3):
```

Default: Option 1 - append date to filename

### Asset Partially Archived
```
Asset folder: assets/book_name/
Status: summary.md already moved, other files remain

Continue archiving remaining files? (y/n):
```

### Move-file Script Error
```
Error from move-file script: {error}

Options:
1. Retry the move
2. Skip this file
3. Manual intervention needed

The file has NOT been moved. Frontmatter unchanged.
```

### Not Yet Extracted
```
File: Clippings/Article.md
Status: extracted: false

This item needs to be extracted first.
Run: /process-inbox-extract "Clippings/Article.md"

Skip this item? (y/n):
```

### Empty Archive Folder
After archiving an asset, if the source folder is empty:
```bash
# Remove empty source folder
rmdir "assets/{asset_name}/"
```

### Missing Topic for Asset Summary
```
Could not determine topic for: assets/book_name/summary.md

Options:
1. Use generic: resources/reference/
2. Specify topic manually
3. Skip archiving this summary

Enter topic or choose option (1/2/3):
```

---

## YAML Suggestions File Mode

When given a `.yaml` path as input, the archive skill operates differently:

### YAML Step 1: Load and Parse YAML

```python
# Load the reviewed suggestions YAML
data = yaml.safe_load(Read(yaml_path))
items = data.get('items', [])
```

### YAML Step 2: Process Approved Associations

For each item with approved associations:

```python
for item in items:
    source_file = item['source_file']
    for assoc in item.get('associations', []):
        if assoc['status'] != 'approved':
            continue

        note = assoc['note_to_create']
        dest_path = note['path']
        content = note['content']

        # Create integration note
        if dest_path exists:
            # Append "See also" link, don't overwrite
            append "See also: [[source_file]]" to existing note
        else:
            # Create the integration note at the approved path
            Write(dest_path, content)

    # Update source frontmatter BEFORE moving
    Update source file frontmatter:
        processed: true
        processed_date: {today}
        archived_to: archive/{relative_path}
```

### YAML Step 3: Archive Source Files

For each processed source file, archive using `move-file` skill:

```bash
uv run .claude/skills/move-file/scripts/move_file.py \
    "{source_file}" \
    "archive/{source_file}"
```

### YAML Step 4: Update Processing Ledger

Append to `_meta/processing-log.md` after each operation.
Create `_meta/` and the ledger file on first run if absent.

```markdown
## {today's date}

### Archived
- `Clippings/Article.md` -> `archive/Clippings/Article.md` (N links updated)

### Integration Notes Created
- `projects/foo/insight.md` (from: Clippings/Article.md)
```

---

## Processing Ledger

All archive operations (both file/folder mode and YAML mode) append to the processing ledger at `_meta/processing-log.md`.

The ledger provides an audit trail of what was archived, where, and what integration notes were created. It is append-only and never overwritten.
