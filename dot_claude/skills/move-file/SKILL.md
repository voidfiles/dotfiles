---
extracted: false
highlighted: true
highlighted_date: 2026-01-23
processed: false
type: unknown
---

# Move File with Wiki Link Updates

Move files or folders within your Obsidian vault while automatically updating all wiki links that reference them. This ensures no broken links when reorganizing your vault structure.

## Features

- **Preserves all link formats**:
  - With/without `.md` extensions
  - Aliases (`[[file|alias]]`)
  - Embeds (`![[file]]`)
  - Relative paths (`[[folder/file]]`)

- **Handles both files and folders**:
  - Single file moves
  - Entire folder moves (updates all internal references)

- **Safe operations**:
  - Auto-detects vault root from `.obsidian` directory
  - Dry-run mode to preview changes
  - Verbose output for detailed change tracking

## Quick Start

```bash
# Move a single file
uv run .claude/skills/move-file/scripts/move_file.py \
    "resources/old-note.md" \
    "projects/active-project/new-note.md"

# Move a folder
uv run .claude/skills/move-file/scripts/move_file.py \
    "resources/research" \
    "projects/new-project/research"

# Dry run (preview changes without moving)
uv run .claude/skills/move-file/scripts/move_file.py \
    --dry-run \
    "areas/health/nutrition.md" \
    "projects/wellness/nutrition.md"

# Verbose output (see all link changes)
uv run .claude/skills/move-file/scripts/move_file.py \
    --verbose \
    "inbox/draft.md" \
    "projects/writing/draft.md"
```

## Instructions

When the user asks to move a file or folder in their Obsidian vault:

1. **Get the paths**:
   - Ask for source path (file or folder to move)
   - Ask for destination path (where to move it)

2. **Run the move command**:
   ```bash
   uv run .claude/skills/move-file/scripts/move_file.py SOURCE DESTINATION
   ```

3. **Optional flags**:
   - Add `--dry-run` if user wants to preview changes first
   - Add `--verbose` if user wants to see all link changes
   - Add `--vault-root PATH` if auto-detection fails

4. **Report results**:
   - Confirm the move
   - Report number of files with updated links
   - Report total number of links updated

## Examples

### Moving a note from resources to an active project

```bash
uv run .claude/skills/move-file/scripts/move_file.py \
    "/Users/alex/Dropbox/obsidian/Alex3/resources/machine-learning.md" \
    "/Users/alex/Dropbox/obsidian/Alex3/projects/ai-research/machine-learning.md"
```

Output:
```
Moving in vault: /Users/alex/Dropbox/obsidian/Alex3
Source: resources/machine-learning.md
Destination: projects/ai-research/machine-learning.md

✓ Moved: resources/machine-learning.md → projects/ai-research/machine-learning.md
✓ Files with updated links: 5
✓ Total links updated: 12

Files updated:
  - projects/ai-research/index.md (3 links)
  - areas/learning/study-notes.md (2 links)
  - daily/2024/01/15.md (1 links)
  - resources/reading-list.md (4 links)
  - projects/ai-research/related-papers.md (2 links)
```

### Moving a folder (dry run first)

```bash
# Preview the changes
uv run .claude/skills/move-file/scripts/move_file.py \
    --dry-run \
    --verbose \
    "resources/old-project" \
    "archives/projects/old-project"

# If looks good, run without --dry-run
uv run .claude/skills/move-file/scripts/move_file.py \
    "resources/old-project" \
    "archives/projects/old-project"
```

### Moving with verbose output

```bash
uv run .claude/skills/move-file/scripts/move_file.py \
    --verbose \
    "inbox/meeting-notes.md" \
    "meetings/2024/01/15-team-sync.md"
```

Output shows detailed changes:
```
Moving in vault: /Users/alex/Dropbox/obsidian/Alex3
Source: inbox/meeting-notes.md
Destination: meetings/2024/01/15-team-sync.md

✓ Moved: inbox/meeting-notes.md → meetings/2024/01/15-team-sync.md
✓ Files with updated links: 2
✓ Total links updated: 3

Detailed changes:

projects/team-project/index.md (2 links):
  [[meeting-notes]] → [[meetings/2024/01/15-team-sync]]
  [[meeting-notes|Team Sync]] → [[meetings/2024/01/15-team-sync|Team Sync]]

daily/2024/01/15.md (1 links):
  ![[meeting-notes]] → ![[meetings/2024/01/15-team-sync]]
```

## Command Options

| Option | Description |
|--------|-------------|
| `source` | Path to file or folder to move (required) |
| `destination` | Destination path (required) |
| `--vault-root PATH` | Explicitly set vault root (auto-detected by default) |
| `--dry-run` | Preview changes without moving files |
| `--verbose`, `-v` | Show detailed link changes for each file |

## How It Works

1. **Vault Detection**: Auto-detects vault root by searching for `.obsidian` directory
2. **Link Scanning**: Scans all markdown files in vault for wiki links
3. **Link Matching**: Identifies links that reference the file/folder being moved
4. **Link Updating**: Updates links to reflect new location while preserving format
5. **File Moving**: Moves the file/folder to new location

## Link Format Preservation

The script preserves the exact format of your links:

- `[[note]]` → `[[new-location/note]]`
- `[[note.md]]` → `[[new-location/note.md]]`
- `[[note|My Note]]` → `[[new-location/note|My Note]]`
- `![[image]]` → `![[new-location/image]]`

## Common Use Cases

### Organizing inbox notes into PARA structure

```bash
# Move from inbox to project
uv run .claude/skills/move-file/scripts/move_file.py \
    "inbox/project-idea.md" \
    "projects/new-project/project-idea.md"
```

### Archiving completed projects

```bash
# Move entire project folder to archives
uv run .claude/skills/move-file/scripts/move_file.py \
    "projects/completed-project" \
    "archives/projects/completed-project"
```

### Promoting resources to active areas

```bash
# Move resource to area when it becomes ongoing
uv run .claude/skills/move-file/scripts/move_file.py \
    "resources/fitness/workout-routine.md" \
    "areas/health/workout-routine.md"
```

### Consolidating related notes

```bash
# Move note into topic folder
uv run .claude/skills/move-file/scripts/move_file.py \
    "resources/python-tips.md" \
    "resources/programming/python-tips.md"
```

## Troubleshooting

**Vault root not detected**:
```bash
uv run .claude/skills/move-file/scripts/move_file.py \
    --vault-root "/Users/alex/Dropbox/obsidian/Alex3" \
    SOURCE DESTINATION
```

**Preview changes first**:
```bash
# Always safe to run with --dry-run first
uv run .claude/skills/move-file/scripts/move_file.py \
    --dry-run --verbose \
    SOURCE DESTINATION
```

**Destination already exists**:
- Choose a different destination name
- Or manually delete/move the existing file first

## Integration with PARA Workflow

This skill is particularly useful for:

1. **Processing inbox** → Moving notes to Projects/Areas/Resources
2. **Project completion** → Moving to Archives
3. **Evolving actionability** → Resources → Areas → Projects
4. **Refactoring structure** → Reorganizing folders without breaking links

The script ensures your Second Brain stays connected even as you reorganize.
