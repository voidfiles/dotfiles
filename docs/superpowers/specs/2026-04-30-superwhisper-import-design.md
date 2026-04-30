# SuperWhisper Import Skill Design

## Overview

A two-part system that imports SuperWhisper transcripts into Obsidian meeting notes. A Python script extracts recordings from the SuperWhisper SQLite database into a JSON manifest. A Claude skill matches recordings to existing meeting notes by timestamp proximity, confirms with the user, and writes transcripts to the vault.

## Data Sources

### SuperWhisper Database

- **Location:** `~/Library/Application Support/superwhisper/database/superwhisper.sqlite`
- **Table:** `recording` (metadata: id, datetime, duration, modeName, folderName)
- **Table:** `recording_fts_content` (transcripts: c1=llmResult, c2=rawResult, c3=result)
- **Join:** `recording.rowid = recording_fts_content.rowid`
- **Datetime:** stored in UTC
- **Duration:** stored in milliseconds
- **Transcript used:** `c2` (rawResult, includes filler words for verbatim accuracy)

### Obsidian Vault

- **Root:** `$OBSIDIAN_ROOT` (detected via `config/shell/20-tools.sh`, typically `~/Documents/Alex3/`)
- **Meetings path:** `$OBSIDIAN_ROOT/Meetings/{YYYY}/{MM}/{DD}/`
- **Note format:**
  ```
  Date: Apr 29, 2026 at 11:33 AM

  # Meeting Summary

  # Notes

  # Transcript
  ```

## Component 1: Python Script (`superwhisper-export.py`)

### Responsibilities

1. Open the SuperWhisper SQLite database (read-only)
2. Query recordings for the target date
3. Filter out recordings with duration < 2 minutes
4. Convert datetime from UTC to local system timezone
5. Output JSON manifest to stdout

### Interface

```bash
uv run scripts/superwhisper-export.py [--date YYYY-MM-DD]
```

- `--date` defaults to today
- Exit 0 with JSON on success
- Exit 1 with error message on stderr if database not found or no recordings

### Output Format

```json
{
  "date": "2026-04-29",
  "timezone": "America/Los_Angeles",
  "recordings": [
    {
      "rowid": 1234,
      "datetime_utc": "2026-04-29T15:30:51",
      "datetime_local": "2026-04-29T08:30:51",
      "duration_seconds": 1909,
      "duration_human": "31m 49s",
      "transcript": "Hey, good morning..."
    }
  ]
}
```

### Dependencies

- Python 3.10+ (stdlib only: `sqlite3`, `json`, `argparse`, `datetime`, `zoneinfo`)
- No third-party packages required

## Component 2: Skill (`SKILL.md`)

### Execution Steps

1. **Extract:** Run the Python script, capture JSON manifest
2. **Discover notes:** Glob `$OBSIDIAN_ROOT/Meetings/{year}/{month}/{day}/*.md`
3. **Parse note times:** Read each meeting note's `Date:` header, parse the timestamp
4. **Match:** For each recording, find the note whose time is within +/-15 minutes of the recording's start time
5. **Assign unmatched:** Recordings without a match get a new filename: `YYYY-MM-DD HH-MM Recording.md`
6. **Confirm:** Present the matching plan to the user for approval
7. **Write:** On confirmation, write transcripts to vault

### Matching Algorithm

```
for each recording R:
    candidates = notes where abs(R.datetime_local - note.time) <= 15 minutes
    if candidates:
        match = candidate with smallest time difference
    else:
        assign new filename: "{date} {HH-MM} Recording.md"

if multiple recordings match the same note:
    append all transcripts in chronological order, separated by:
    "\n\n---\n\n*Recording at {time} ({duration})*\n\n"
```

### Confirmation UX

```
SuperWhisper Import for 2026-04-29
===================================

Matched to existing notes:
  08:30 (31m 49s)  -> Alex + Chase.md
  08:59 (19m 58s)  -> Kevin + Alex.md
  09:16 (14m 19s)  -> Alex + David.md

New notes (no existing match):
  12:32 (31m 22s)  -> 2026-04-29 12-32 Recording.md

Skipped (< 2 min):
  2 recordings

Proceed? [y/n/edit]
```

If user says "edit", allow them to reassign or skip individual recordings.

### Write Logic

**Existing file with `# Transcript` heading:**
- Append transcript after the heading (below any existing content under that heading)

**Existing file without `# Transcript` heading:**
- Append `\n\n# Transcript\n\n` at end of file, then transcript content

**New file:**
```markdown
Date: {month} {day}, {year} at {HH:MM AM/PM}

# Meeting Summary

# Notes

# Transcript

{transcript content}
```

### Edge Cases

- Transcript heading already has content: append below with a separator line
- Empty transcript after filtering: skip entirely
- Database file not found: error with clear message about SuperWhisper not being installed
- No recordings for date: report "No recordings found for {date}" and exit
- `$OBSIDIAN_ROOT` not set: error with message to source shell config

## File Layout

```
skills/superwhisper-import/
  SKILL.md            # Skill definition
  scripts/
    superwhisper-export.py   # Python extraction script
```

## Not In Scope

- Speaker diarization (SuperWhisper doesn't label speakers in transcript text)
- Running the `meeting-notes` pipeline automatically (user can invoke separately)
- Syncing audio files (only transcripts are imported)
- Historical backfill (skill targets one day at a time)
