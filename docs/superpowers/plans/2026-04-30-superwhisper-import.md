# SuperWhisper Import Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code skill that imports today's SuperWhisper transcripts into the Obsidian vault's Meetings folder, matching recordings to existing notes by timestamp or creating new ones.

**Architecture:** A Python script (`superwhisper-export.py`) queries the SQLite database and outputs a JSON manifest. A Claude skill (`SKILL.md`) orchestrates the matching, confirmation, and file writing.

**Tech Stack:** Python 3.10+ (stdlib only), Claude Code skill (markdown), SQLite, bash.

**Spec:** See `docs/superpowers/specs/2026-04-30-superwhisper-import-design.md`.

---

## Conventions

- **Working directory:** `/Users/alexkessinger/.local/share/dotfiles`
- **Commit style:** `feat(superwhisper-import): <summary>`
- **Python style:** Type hints everywhere, no third-party deps, stdlib only.
- **Testing:** We'll test the Python script with a fixture SQLite database. The skill itself is tested by invoking it.

---

## File Structure

```
skills/superwhisper-import/
  SKILL.md                          # Skill definition
  scripts/
    superwhisper-export.py          # Python extraction script
    test_superwhisper_export.py     # Unit tests for the script
    fixtures/
      test.sqlite                   # Test fixture database (created by test setup)
```

---

## Task 1: Create the Python extraction script

**Files:**
- Create: `skills/superwhisper-import/scripts/superwhisper-export.py`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p skills/superwhisper-import/scripts/fixtures
```

- [ ] **Step 2: Write the extraction script**

```python
#!/usr/bin/env python3
"""Export SuperWhisper recordings for a given date as JSON."""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

DB_PATH = Path.home() / "Library/Application Support/superwhisper/database/superwhisper.sqlite"

def get_local_timezone() -> ZoneInfo:
    """Get the system's local timezone."""
    # datetime.now().astimezone() gives us the local tz
    local_tz = datetime.now().astimezone().tzinfo
    # Convert to ZoneInfo for proper handling
    tz_name = str(local_tz)
    try:
        return ZoneInfo(tz_name)
    except (KeyError, Exception):
        # Fallback: compute offset and use it
        import time
        offset = -time.timezone if time.daylight == 0 else -time.altzone
        # Use the tzinfo from astimezone directly
        return datetime.now().astimezone().tzinfo


def format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes > 0:
        return f"{minutes}m {secs:02d}s"
    return f"{secs}s"


def export_recordings(db_path: Path, target_date: str) -> dict:
    """Query recordings for target_date and return manifest dict.

    Args:
        db_path: Path to the SuperWhisper SQLite database.
        target_date: Date string in YYYY-MM-DD format.

    Returns:
        Dict with date, timezone, and recordings list.
    """
    if not db_path.exists():
        print(
            f"Error: SuperWhisper database not found at {db_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    local_tz = get_local_timezone()

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    # Query recordings for the target date (datetime is stored in UTC)
    # We need to find recordings where the LOCAL date matches target_date.
    # Strategy: convert target_date boundaries to UTC, then query.
    target = datetime.strptime(target_date, "%Y-%m-%d")
    # Start of day in local time -> UTC
    day_start_local = datetime(target.year, target.month, target.day, tzinfo=local_tz)
    day_end_local = day_start_local + timedelta(days=1)
    day_start_utc = day_start_local.astimezone(timezone.utc)
    day_end_utc = day_end_local.astimezone(timezone.utc)

    cursor = conn.execute(
        """
        SELECT r.rowid, r.datetime, r.duration, f.c2 as transcript
        FROM recording r
        JOIN recording_fts_content f ON f.rowid = r.rowid
        WHERE r.datetime >= ? AND r.datetime < ?
        ORDER BY r.datetime
        """,
        (
            day_start_utc.strftime("%Y-%m-%d %H:%M:%S"),
            day_end_utc.strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )

    recordings = []
    for row in cursor:
        duration_ms = row["duration"]
        duration_secs = duration_ms / 1000.0

        # Filter: skip recordings under 2 minutes
        if duration_secs < 120:
            continue

        # Skip empty transcripts
        transcript = row["transcript"] or ""
        if not transcript.strip():
            continue

        # Parse UTC datetime from DB
        dt_utc = datetime.strptime(row["datetime"][:19], "%Y-%m-%dT%H:%M:%S")
        if dt_utc.tzinfo is None:
            # The DB stores datetimes like "2026-04-29 15:30:51.220"
            dt_str = row["datetime"].replace("T", " ")[:19]
            dt_utc = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=timezone.utc
            )

        dt_local = dt_utc.astimezone(local_tz)

        recordings.append(
            {
                "rowid": row["rowid"],
                "datetime_utc": dt_utc.strftime("%Y-%m-%dT%H:%M:%S"),
                "datetime_local": dt_local.strftime("%Y-%m-%dT%H:%M:%S"),
                "duration_seconds": int(duration_secs),
                "duration_human": format_duration(duration_secs),
                "transcript": transcript,
            }
        )

    conn.close()

    if not recordings:
        print(
            f"No recordings found for {target_date} (after filtering < 2 min)",
            file=sys.stderr,
        )
        sys.exit(1)

    return {
        "date": target_date,
        "timezone": str(local_tz),
        "recordings": recordings,
    }


def main():
    parser = argparse.ArgumentParser(description="Export SuperWhisper recordings to JSON")
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Target date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DB_PATH,
        help="Path to SuperWhisper database (for testing)",
    )
    args = parser.parse_args()

    manifest = export_recordings(args.db, args.date)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Make the script executable**

```bash
chmod +x skills/superwhisper-import/scripts/superwhisper-export.py
```

- [ ] **Step 4: Verify the script runs against the real database**

```bash
cd /Users/alexkessinger/.local/share/dotfiles
python3 skills/superwhisper-import/scripts/superwhisper-export.py --date 2026-04-29 | python3 -m json.tool | head -30
```

Expected: JSON output with recordings array, each having datetime_local, duration_human, and transcript fields.

- [ ] **Step 5: Commit**

```bash
git add skills/superwhisper-import/scripts/superwhisper-export.py
git commit -m "feat(superwhisper-import): add Python extraction script"
```

---

## Task 2: Write tests for the Python extraction script

**Files:**
- Create: `skills/superwhisper-import/scripts/test_superwhisper_export.py`

- [ ] **Step 1: Write unit tests using a fixture database**

```python
#!/usr/bin/env python3
"""Tests for superwhisper-export.py."""

import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile

SCRIPT = Path(__file__).parent / "superwhisper-export.py"


def create_test_db(path: Path, recordings: list[dict]) -> None:
    """Create a minimal SuperWhisper test database.

    Args:
        path: Where to write the SQLite file.
        recordings: List of dicts with keys: datetime_utc, duration_ms, transcript
    """
    conn = sqlite3.connect(str(path))
    conn.execute("""
        CREATE TABLE recording (
            id TEXT PRIMARY KEY,
            datetime DATETIME NOT NULL,
            duration DOUBLE NOT NULL,
            appVersion TEXT NOT NULL DEFAULT '',
            modelKey TEXT NOT NULL DEFAULT '',
            modelName TEXT NOT NULL DEFAULT '',
            languageModelName TEXT NOT NULL DEFAULT '',
            recordingDevice TEXT NOT NULL DEFAULT '',
            rawWordCount INTEGER NOT NULL DEFAULT 0,
            llmWordCount INTEGER NOT NULL DEFAULT 0,
            prompt TEXT NOT NULL DEFAULT '',
            processingTime INTEGER NOT NULL DEFAULT 0,
            languageModelProcessingTime INTEGER NOT NULL DEFAULT 0,
            modeName TEXT NOT NULL DEFAULT 'Multi Speaker',
            promptContext TEXT NOT NULL DEFAULT '',
            folderName TEXT NOT NULL DEFAULT '',
            fromFile BOOLEAN NOT NULL DEFAULT 0,
            createdAt DATETIME NOT NULL DEFAULT '2025-01-01 00:00:00',
            languageModelKey TEXT NOT NULL DEFAULT ''
        )
    """)
    conn.execute("""
        CREATE TABLE recording_fts_content (
            id INTEGER PRIMARY KEY,
            c0,
            c1,
            c2,
            c3
        )
    """)

    for i, rec in enumerate(recordings, 1):
        conn.execute(
            "INSERT INTO recording (rowid, id, datetime, duration) VALUES (?, ?, ?, ?)",
            (i, f"id-{i}", rec["datetime_utc"], rec["duration_ms"]),
        )
        conn.execute(
            "INSERT INTO recording_fts_content (rowid, c0, c1, c2, c3) VALUES (?, ?, ?, ?, ?)",
            (i, f"id-{i}", "", rec["transcript"], rec["transcript"]),
        )

    conn.commit()
    conn.close()


def run_export(db_path: Path, date: str) -> subprocess.CompletedProcess:
    """Run the export script and return the result."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--db", str(db_path), "--date", date],
        capture_output=True,
        text=True,
    )


def test_basic_export():
    """Recordings for the target date are exported with correct fields."""
    with NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = Path(f.name)

    recordings = [
        {
            "datetime_utc": "2026-05-01 18:00:00.000",  # UTC
            "duration_ms": 300000.0,  # 5 minutes
            "transcript": "Hello this is a test recording with enough content.",
        },
        {
            "datetime_utc": "2026-05-01 19:30:00.000",  # UTC
            "duration_ms": 600000.0,  # 10 minutes
            "transcript": "Second recording of the day, also has content.",
        },
    ]
    create_test_db(db_path, recordings)

    # Use UTC date since we're testing; the script converts to local
    # We need the local date for --date arg
    from zoneinfo import ZoneInfo
    local_tz = datetime.now().astimezone().tzinfo
    dt_utc = datetime(2026, 5, 1, 18, 0, 0, tzinfo=timezone.utc)
    dt_local = dt_utc.astimezone(local_tz)
    target_date = dt_local.strftime("%Y-%m-%d")

    result = run_export(db_path, target_date)
    assert result.returncode == 0, f"stderr: {result.stderr}"

    manifest = json.loads(result.stdout)
    assert manifest["date"] == target_date
    assert len(manifest["recordings"]) == 2
    assert manifest["recordings"][0]["duration_seconds"] == 300
    assert manifest["recordings"][0]["duration_human"] == "5m 00s"
    assert "Hello" in manifest["recordings"][0]["transcript"]

    db_path.unlink()


def test_filters_short_recordings():
    """Recordings under 2 minutes are excluded."""
    with NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = Path(f.name)

    recordings = [
        {
            "datetime_utc": "2026-05-01 18:00:00.000",
            "duration_ms": 30000.0,  # 30 seconds - should be filtered
            "transcript": "Short recording.",
        },
        {
            "datetime_utc": "2026-05-01 18:05:00.000",
            "duration_ms": 180000.0,  # 3 minutes - should pass
            "transcript": "Longer recording that passes the filter.",
        },
    ]
    create_test_db(db_path, recordings)

    from zoneinfo import ZoneInfo
    local_tz = datetime.now().astimezone().tzinfo
    dt_utc = datetime(2026, 5, 1, 18, 0, 0, tzinfo=timezone.utc)
    dt_local = dt_utc.astimezone(local_tz)
    target_date = dt_local.strftime("%Y-%m-%d")

    result = run_export(db_path, target_date)
    assert result.returncode == 0, f"stderr: {result.stderr}"

    manifest = json.loads(result.stdout)
    assert len(manifest["recordings"]) == 1
    assert manifest["recordings"][0]["duration_seconds"] == 180

    db_path.unlink()


def test_filters_empty_transcripts():
    """Recordings with empty transcripts are excluded."""
    with NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = Path(f.name)

    recordings = [
        {
            "datetime_utc": "2026-05-01 18:00:00.000",
            "duration_ms": 300000.0,
            "transcript": "",  # empty
        },
        {
            "datetime_utc": "2026-05-01 19:00:00.000",
            "duration_ms": 300000.0,
            "transcript": "   ",  # whitespace only
        },
    ]
    create_test_db(db_path, recordings)

    from zoneinfo import ZoneInfo
    local_tz = datetime.now().astimezone().tzinfo
    dt_utc = datetime(2026, 5, 1, 18, 0, 0, tzinfo=timezone.utc)
    dt_local = dt_utc.astimezone(local_tz)
    target_date = dt_local.strftime("%Y-%m-%d")

    result = run_export(db_path, target_date)
    # Should exit 1 because no valid recordings remain
    assert result.returncode == 1
    assert "No recordings found" in result.stderr

    db_path.unlink()


def test_no_recordings_exits_1():
    """Exit code 1 when no recordings exist for the date."""
    with NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = Path(f.name)

    create_test_db(db_path, [])

    result = run_export(db_path, "2026-05-01")
    assert result.returncode == 1
    assert "No recordings found" in result.stderr

    db_path.unlink()


def test_missing_database_exits_1():
    """Exit code 1 when database file doesn't exist."""
    result = run_export(Path("/tmp/nonexistent.sqlite"), "2026-05-01")
    assert result.returncode == 1
    assert "not found" in result.stderr


if __name__ == "__main__":
    test_basic_export()
    test_filters_short_recordings()
    test_filters_empty_transcripts()
    test_no_recordings_exits_1()
    test_missing_database_exits_1()
    print("All tests passed.")
```

- [ ] **Step 2: Run the tests**

```bash
cd /Users/alexkessinger/.local/share/dotfiles
python3 skills/superwhisper-import/scripts/test_superwhisper_export.py
```

Expected: "All tests passed."

- [ ] **Step 3: Fix any failures, re-run until green**

- [ ] **Step 4: Commit**

```bash
git add skills/superwhisper-import/scripts/test_superwhisper_export.py
git commit -m "feat(superwhisper-import): add unit tests for extraction script"
```

---

## Task 3: Write the SKILL.md

**Files:**
- Create: `skills/superwhisper-import/SKILL.md`

- [ ] **Step 1: Write the skill definition**

```markdown
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
```

- [ ] **Step 2: Verify the skill file is valid**

```bash
head -5 skills/superwhisper-import/SKILL.md
```

Expected: YAML frontmatter with name, description, argument-hint.

- [ ] **Step 3: Commit**

```bash
git add skills/superwhisper-import/SKILL.md
git commit -m "feat(superwhisper-import): add skill definition"
```

---

## Task 4: End-to-end verification

- [ ] **Step 1: Run the extraction script for a known date with real data**

```bash
python3 skills/superwhisper-import/scripts/superwhisper-export.py --date 2026-04-29 | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'Date: {data[\"date\"]}')
print(f'Timezone: {data[\"timezone\"]}')
print(f'Recordings: {len(data[\"recordings\"])}')
for r in data['recordings']:
    print(f'  {r[\"datetime_local\"][11:16]} ({r[\"duration_human\"]}) - {len(r[\"transcript\"])} chars')
"
```

Expected: List of recordings with local times, durations, and transcript lengths.

- [ ] **Step 2: Run the unit tests one final time**

```bash
python3 skills/superwhisper-import/scripts/test_superwhisper_export.py
```

Expected: "All tests passed."

- [ ] **Step 3: Invoke the skill to verify it loads**

Test that the skill is discoverable:
```bash
ls skills/superwhisper-import/SKILL.md
```

- [ ] **Step 4: Final commit (if any fixes were needed)**

```bash
git status
# If changes exist:
git add -A skills/superwhisper-import/
git commit -m "fix(superwhisper-import): address issues from e2e verification"
```
