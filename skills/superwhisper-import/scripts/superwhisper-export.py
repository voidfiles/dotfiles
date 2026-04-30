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


def export_recordings(db_path: Path, target_date: str) -> dict:
    """Query recordings for target_date and return manifest dict.

    Args:
        db_path: Path to the SuperWhisper SQLite database.
        target_date: Date string in YYYY-MM-DD format.

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
            # The DB stores datetimes like "2026-04-29 15:30:51.220"
            dt_str = row["datetime"].replace("T", " ")[:19]
            dt_utc = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=timezone.utc
            )

            dt_local = dt_utc.astimezone(local_tz)

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
    args = parser.parse_args()

    try:
        manifest = export_recordings(args.db, args.date)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
