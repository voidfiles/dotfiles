#!/usr/bin/env python3
"""Export SuperWhisper recordings for a given date as JSON."""

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timedelta, timezone, tzinfo
from pathlib import Path

DB_PATH = Path.home() / "Library/Application Support/superwhisper/database/superwhisper.sqlite"
RECORDINGS_DIR = Path.home() / "Documents/superwhisper/recordings"


def get_local_timezone() -> tzinfo:
    """Get the system's local timezone."""
    return datetime.now().astimezone().tzinfo


def format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes > 0:
        return f"{minutes}m {secs:02d}s"
    return f"{secs}s"


def format_timestamp(seconds: float) -> str:
    """Format seconds into HH:MM:SS or MM:SS timestamp."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_segments_transcript(segments: list[dict]) -> str:
    """Format segments with speaker labels and timestamps into a readable transcript.

    Groups consecutive segments by the same speaker into paragraphs,
    labeled with Speaker N and the timestamp of when they started speaking.
    """
    if not segments:
        return ""

    lines = []
    current_speaker = None
    current_start: float = 0.0
    current_texts: list[str] = []

    for seg in segments:
        speaker = seg.get("speaker")
        text = seg.get("text", "").strip()
        if not text:
            continue

        if speaker != current_speaker:
            if current_texts:
                ts = format_timestamp(current_start)
                lines.append(f"**Speaker {current_speaker}** [{ts}]: {''.join(current_texts)}")
            current_speaker = speaker
            current_start = seg.get("start", 0.0)
            current_texts = [text]
        else:
            current_texts.append(f" {text}" if not text.startswith(" ") else text)

    # Flush remaining
    if current_texts:
        ts = format_timestamp(current_start)
        lines.append(f"**Speaker {current_speaker}** [{ts}]: {''.join(current_texts)}")

    return "\n\n".join(lines)


def load_segments_from_meta(folder_name: str, recordings_dir: Path) -> list[dict] | None:
    """Load segments array from the recording's meta.json file.

    Returns None if the file doesn't exist or has no segments.
    """
    meta_path = recordings_dir / folder_name / "meta.json"
    if not meta_path.exists():
        return None

    try:
        with open(meta_path) as f:
            meta = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

    segments = meta.get("segments", [])
    if not segments:
        return None

    return segments


def export_recordings(
    db_path: Path, target_date: str, recordings_dir: Path = RECORDINGS_DIR
) -> dict:
    """Query recordings for target_date and return manifest dict.

    Args:
        db_path: Path to the SuperWhisper SQLite database.
        target_date: Date string in YYYY-MM-DD format.
        recordings_dir: Path to the SuperWhisper recordings directory.

    Returns:
        Dict with date, timezone, and recordings list.

    Raises:
        FileNotFoundError: If the database file does not exist.
        ValueError: If no recordings are found for the given date.
    """
    if not db_path.exists():
        raise FileNotFoundError(f"SuperWhisper database not found at {db_path}")

    local_tz = get_local_timezone()

    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        conn.row_factory = sqlite3.Row

        # Query recordings for the target date (datetime is stored in UTC)
        # Strategy: convert target_date boundaries to UTC, then query.
        target = datetime.strptime(target_date, "%Y-%m-%d")
        day_start_local = datetime(target.year, target.month, target.day, tzinfo=local_tz)
        # Query window: since DB stores END times, we need to extend the
        # window forward to catch recordings that started on target_date
        # but whose end time spills into the next day (e.g. 11:30 PM + 45 min).
        # We also can't start earlier than target_date since an end time before
        # the day start means the recording definitely didn't start on this day.
        day_end_local = day_start_local + timedelta(days=1, hours=2)
        day_start_utc = day_start_local.astimezone(timezone.utc)
        day_end_utc = day_end_local.astimezone(timezone.utc)

        cursor = conn.execute(
            """
            SELECT r.rowid, r.datetime, r.duration, r.folderName,
                   f.c2 as transcript
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
            # The DB stores datetimes like "2026-04-29 15:30:51.220"
            # NOTE: the DB datetime is the recording END time, not start.
            # Subtract duration to get when the recording actually began.
            dt_str = row["datetime"].replace("T", " ")[:19]
            dt_end_utc = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=timezone.utc
            )
            dt_utc = dt_end_utc - timedelta(seconds=duration_secs)

            dt_local = dt_utc.astimezone(local_tz)

            # Filter: ensure the computed start time is actually on target_date
            if dt_local.strftime("%Y-%m-%d") != target_date:
                continue

            # Prefer multi-speaker segmented transcript from meta.json
            folder_name = row["folderName"]
            segments = load_segments_from_meta(folder_name, recordings_dir)
            if segments:
                transcript = format_segments_transcript(segments)

            recordings.append(
                {
                    "rowid": row["rowid"],
                    "datetime_utc": dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "datetime_local": dt_local.strftime("%Y-%m-%dT%H:%M:%S"),
                    "duration_seconds": int(duration_secs),
                    "duration_human": format_duration(duration_secs),
                    "transcript": transcript,
                }
            )
    finally:
        conn.close()

    if not recordings:
        raise ValueError(
            f"No recordings found for {target_date} (after filtering < 2 min)"
        )

    return {
        "date": target_date,
        "timezone": str(local_tz),
        "recordings": recordings,
    }


def _validate_date(value: str) -> str:
    """Validate that value is a YYYY-MM-DD date string."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise argparse.ArgumentTypeError(
            f"invalid date format: '{value}' (expected YYYY-MM-DD)"
        )
    # Also confirm it's a real date, not something like 2026-02-30
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"invalid date: '{value}' is not a real calendar date"
        )
    return value


def main():
    parser = argparse.ArgumentParser(description="Export SuperWhisper recordings to JSON")
    parser.add_argument(
        "--date",
        type=_validate_date,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Target date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DB_PATH,
        help="Path to SuperWhisper database (for testing)",
    )
    parser.add_argument(
        "--recordings-dir",
        type=Path,
        default=RECORDINGS_DIR,
        help="Path to SuperWhisper recordings directory (for testing)",
    )
    args = parser.parse_args()

    try:
        manifest = export_recordings(args.db, args.date, args.recordings_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
