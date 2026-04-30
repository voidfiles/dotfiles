---
name: superwhisper-import
description: Import today's SuperWhisper recordings into Obsidian vault meeting notes, matching by timestamp or creating new files.
argument-hint: [--date YYYY-MM-DD]
---

# SuperWhisper Import

Import SuperWhisper transcripts from today (or a specified date) into your Obsidian vault's Meetings folder. Matches recordings to existing meeting notes by timestamp proximity, or creates new notes for unmatched recordings.

## Usage

```
/superwhisper-import
/superwhisper-import --date 2026-04-29
```

## Prerequisites

- SuperWhisper installed with recordings in its SQLite database
- `$OBSIDIAN_ROOT` environment variable set (sourced from shell config)
- Python 3.10+ available

## Pipeline

```
[1. EXTRACT] → [2. DISCOVER] → [3. MATCH] → [4. CONFIRM] → [5. WRITE]
```

---

## Stage 1: Extract Recordings

Run the extraction script to get today's recordings as JSON.

### Instructions

1. Determine the target date:
   - If `$ARGUMENTS` contains `--date YYYY-MM-DD`, use that date
   - Otherwise use today's date
2. Run the extraction script:
   ```bash
   python3 skills/superwhisper-import/scripts/superwhisper-export.py --date {DATE}
   ```
3. Parse the JSON manifest
4. If the script exits with code 1, report the error to the user and stop

---

## Stage 2: Discover Existing Meeting Notes

Find meeting notes in the vault for the target date.

### Instructions

1. Resolve the vault path: use `$OBSIDIAN_ROOT` environment variable
   - If not set, check `~/Documents/Alex3/` as fallback
2. Glob for notes: `$OBSIDIAN_ROOT/Meetings/{YYYY}/{MM}/{DD}/*.md`
   - YYYY, MM, DD from the target date (MM and DD are zero-padded)
3. For each note file, read the first line to extract the `Date:` header
4. Parse the time from the header format: `Date: {Mon} {DD}, {YYYY} at {H:MM AM/PM}`
   - Example: `Date: Apr 29, 2026 at 11:33 AM`
   - Extract hours and minutes in 24h format

### Output (internal)

Build a list of note objects:
```
notes = [
  { path: "full/path/to/file.md", filename: "Alex + Chase.md", time_minutes: 693 }
]
```

Where `time_minutes` is minutes since midnight (e.g., 11:33 AM = 693).

---

## Stage 3: Match Recordings to Notes

Apply the matching algorithm.

### Instructions

For each recording:
1. Convert `datetime_local` to minutes since midnight
2. Find all notes where `abs(recording_minutes - note_minutes) <= 15`
3. If matches found: pick the note with the smallest time difference
4. If no match: assign filename `{YYYY-MM-DD} {HH-MM} Recording.md`

Handle conflicts:
- If multiple recordings match the same note, keep all matches (they'll be appended in order)

### Output (internal)

Build assignment list:
```
assignments = [
  { recording_index: 0, target_file: "path/to/existing.md", is_new: false, time: "08:30", duration: "31m 49s" },
  { recording_index: 3, target_file: "path/to/new.md", is_new: true, time: "12:32", duration: "31m 22s" }
]
```

---

## Stage 4: Confirm with User

Present the matching plan and wait for approval.

### Instructions

Display the assignments in this format:

```
SuperWhisper Import for {DATE}
===================================

Matched to existing notes:
  {time} ({duration})  →  {filename}
  {time} ({duration})  →  {filename}

New notes (no existing match):
  {time} ({duration})  →  {new filename}

Proceed? [y/n/edit]
```

- If user says **y** or **yes**: proceed to Stage 5
- If user says **n** or **no**: stop, do nothing
- If user says **edit**: ask which assignments to change, allow:
  - Skip a recording (remove from list)
  - Reassign a recording to a different existing note (show available notes)
  - Rename a new file

---

## Stage 5: Write Transcripts to Vault

Write each recording's transcript to its assigned file.

### Instructions

For each assignment (ordered by recording time):

**If `is_new` is true:**
1. Ensure the directory exists: `$OBSIDIAN_ROOT/Meetings/{YYYY}/{MM}/{DD}/`
2. Create the file with this template:
   ```
   Date: {Mon DD, YYYY} at {H:MM AM/PM}

   # Meeting Summary

   # Notes

   # Transcript

   {transcript content}
   ```

**If `is_new` is false (existing file):**
1. Read the existing file content
2. Find the `# Transcript` heading:
   - If found and content exists below it: append `\n\n---\n\n*Recording at {time} ({duration})*\n\n{transcript}`
   - If found but empty below: append `\n{transcript}`
   - If NOT found: append `\n\n# Transcript\n\n{transcript}` at end of file
3. Write the updated content

**Multiple recordings → same file:**
- Append in chronological order
- Separate with: `\n\n---\n\n*Recording at {time} ({duration})*\n\n`

### After writing

Report what was done:
```
Done! Wrote {N} transcripts:
  ✓ Alex + Chase.md (31m 49s)
  ✓ Kevin + Alex.md (19m 58s)
  + 2026-04-29 12-32 Recording.md (new, 31m 22s)
```

---

## Error Handling

| Error | Behavior |
|-------|----------|
| Database not found | Report: "SuperWhisper database not found. Is SuperWhisper installed?" |
| No recordings for date | Report: "No recordings found for {date} (after filtering < 2 min)" |
| `$OBSIDIAN_ROOT` not set and fallback missing | Report: "Cannot find Obsidian vault. Set $OBSIDIAN_ROOT or ensure ~/Documents/Alex3 exists." |
| Meeting note file unreadable | Skip it, warn user |
| Date header unparseable | Skip that note from matching, warn user |
