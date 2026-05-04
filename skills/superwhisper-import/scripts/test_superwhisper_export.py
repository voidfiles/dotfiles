#!/usr/bin/env python3
"""Tests for superwhisper-export.py."""

import json
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile

SCRIPT = Path(__file__).parent / "superwhisper-export.py"


def create_test_db(path: Path, recordings: list[dict]) -> None:
    """Create a minimal SuperWhisper test database.

    Each recording dict should have:
        datetime_utc: str  - UTC timestamp "YYYY-MM-DD HH:MM:SS.000"
        duration_ms: float - duration in milliseconds
        transcript: str    - the raw transcript text
        folder_name: str   - (optional) folder name for meta.json lookup
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

    for i, rec in enumerate(recordings):
        rec_id = f"rec-{i:04d}"
        folder_name = rec.get("folder_name", f"folder-{i:04d}")
        conn.execute(
            "INSERT INTO recording (id, datetime, duration, folderName) VALUES (?, ?, ?, ?)",
            (rec_id, rec["datetime_utc"], rec["duration_ms"], folder_name),
        )
        # The rowid is auto-assigned sequentially starting at 1
        rowid = i + 1
        conn.execute(
            "INSERT INTO recording_fts_content (rowid, c0, c1, c2, c3) VALUES (?, '', '', ?, '')",
            (rowid, rec["transcript"]),
        )

    conn.commit()
    conn.close()


def run_export(
    db_path: Path, date: str, recordings_dir: Path | None = None
) -> subprocess.CompletedProcess:
    """Run the export script and return the result."""
    cmd = [sys.executable, str(SCRIPT), "--db", str(db_path), "--date", date]
    if recordings_dir is not None:
        cmd.extend(["--recordings-dir", str(recordings_dir)])
    return subprocess.run(cmd, capture_output=True, text=True)


def get_local_date_for_utc(utc_hour: int = 18) -> tuple[str, str]:
    """Return a (utc_timestamp, local_date) pair that works regardless of timezone.

    We pick a UTC time at the given hour on 2026-05-01. Then we compute what
    local date that maps to, and return both the UTC string and local date string.
    """
    dt_utc = datetime(2026, 5, 1, utc_hour, 30, 0, tzinfo=timezone.utc)
    local_tz = datetime.now().astimezone().tzinfo
    dt_local = dt_utc.astimezone(local_tz)
    utc_str = dt_utc.strftime("%Y-%m-%d %H:%M:%S.000")
    local_date = dt_local.strftime("%Y-%m-%d")
    return utc_str, local_date


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_basic_export():
    """Recordings for a target date are exported with correct fields."""
    utc_ts, local_date = get_local_date_for_utc(18)

    with NamedTemporaryFile(suffix=".sqlite") as tmp:
        db_path = Path(tmp.name)
        create_test_db(db_path, [
            {
                "datetime_utc": utc_ts,
                "duration_ms": 300000.0,  # 5 minutes
                "transcript": "This is a test transcript with enough content.",
            },
        ])

        result = run_export(db_path, local_date)
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}: {result.stderr}"

        manifest = json.loads(result.stdout)
        assert manifest["date"] == local_date
        assert "timezone" in manifest
        assert len(manifest["recordings"]) == 1

        rec = manifest["recordings"][0]
        assert rec["rowid"] == 1
        assert rec["datetime_utc"].endswith("Z")
        assert "datetime_local" in rec
        assert rec["duration_seconds"] == 300
        assert rec["duration_human"] == "5m 00s"
        assert rec["transcript"] == "This is a test transcript with enough content."

    print("  PASS: test_basic_export")


def test_filters_short_recordings():
    """Recordings under 2 minutes are excluded."""
    utc_ts, local_date = get_local_date_for_utc(18)

    with NamedTemporaryFile(suffix=".sqlite") as tmp:
        db_path = Path(tmp.name)
        create_test_db(db_path, [
            {
                "datetime_utc": utc_ts,
                "duration_ms": 60000.0,  # 1 minute (too short)
                "transcript": "Short recording that should be filtered.",
            },
            {
                "datetime_utc": utc_ts,
                "duration_ms": 119999.0,  # Just under 2 minutes
                "transcript": "Also too short, just barely.",
            },
        ])

        result = run_export(db_path, local_date)
        # All recordings filtered out -> no recordings -> exit 1
        assert result.returncode == 1, f"Expected exit 1, got {result.returncode}"
        assert "No recordings found" in result.stderr

    print("  PASS: test_filters_short_recordings")


def test_filters_empty_transcripts():
    """Recordings with empty or whitespace-only transcripts are excluded."""
    utc_ts, local_date = get_local_date_for_utc(18)

    with NamedTemporaryFile(suffix=".sqlite") as tmp:
        db_path = Path(tmp.name)
        create_test_db(db_path, [
            {
                "datetime_utc": utc_ts,
                "duration_ms": 300000.0,  # 5 minutes
                "transcript": "",
            },
            {
                "datetime_utc": utc_ts,
                "duration_ms": 300000.0,
                "transcript": "   \n\t  ",
            },
        ])

        result = run_export(db_path, local_date)
        assert result.returncode == 1, f"Expected exit 1, got {result.returncode}"
        assert "No recordings found" in result.stderr

    print("  PASS: test_filters_empty_transcripts")


def test_no_recordings_exits_1():
    """Exit code 1 when no recordings exist for the date."""
    # Use a date that won't match any recordings
    utc_ts = "2020-01-15 12:00:00.000"
    # The local date for this UTC time
    dt_utc = datetime(2020, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    local_tz = datetime.now().astimezone().tzinfo
    dt_local = dt_utc.astimezone(local_tz)
    query_date = dt_local.strftime("%Y-%m-%d")

    # Put a recording on a completely different date
    other_utc_ts, _ = get_local_date_for_utc(18)

    with NamedTemporaryFile(suffix=".sqlite") as tmp:
        db_path = Path(tmp.name)
        create_test_db(db_path, [
            {
                "datetime_utc": other_utc_ts,
                "duration_ms": 300000.0,
                "transcript": "This recording is on a different date.",
            },
        ])

        result = run_export(db_path, query_date)
        assert result.returncode == 1, f"Expected exit 1, got {result.returncode}"
        assert "No recordings found" in result.stderr

    print("  PASS: test_no_recordings_exits_1")


def test_missing_database_exits_1():
    """Exit code 1 when database file doesn't exist."""
    fake_path = Path("/tmp/nonexistent_superwhisper_test_db_12345.sqlite")
    # Make sure it truly doesn't exist
    if fake_path.exists():
        fake_path.unlink()

    result = run_export(fake_path, "2026-05-01")
    assert result.returncode == 1, f"Expected exit 1, got {result.returncode}"
    assert "not found" in result.stderr

    print("  PASS: test_missing_database_exits_1")


def test_boundary_duration_included():
    """A recording exactly at 2 minutes (120s = 120000ms) is included."""
    utc_ts, local_date = get_local_date_for_utc(18)

    with NamedTemporaryFile(suffix=".sqlite") as tmp:
        db_path = Path(tmp.name)
        create_test_db(db_path, [
            {
                "datetime_utc": utc_ts,
                "duration_ms": 120000.0,  # Exactly 2 minutes
                "transcript": "Boundary case: exactly two minutes.",
            },
        ])

        result = run_export(db_path, local_date)
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}: {result.stderr}"

        manifest = json.loads(result.stdout)
        assert len(manifest["recordings"]) == 1
        assert manifest["recordings"][0]["duration_seconds"] == 120

    print("  PASS: test_boundary_duration_included")


def test_multiple_recordings_ordered():
    """Multiple valid recordings are returned in datetime order."""
    local_tz = datetime.now().astimezone().tzinfo

    # Two recordings 2 hours apart, both on the same local date
    dt1_utc = datetime(2026, 5, 1, 16, 0, 0, tzinfo=timezone.utc)
    dt2_utc = datetime(2026, 5, 1, 18, 0, 0, tzinfo=timezone.utc)

    # Verify both map to the same local date
    dt1_local = dt1_utc.astimezone(local_tz)
    dt2_local = dt2_utc.astimezone(local_tz)
    assert dt1_local.strftime("%Y-%m-%d") == dt2_local.strftime("%Y-%m-%d"), \
        "Test setup: both UTC times must map to the same local date"

    local_date = dt1_local.strftime("%Y-%m-%d")
    ts1 = dt1_utc.strftime("%Y-%m-%d %H:%M:%S.000")
    ts2 = dt2_utc.strftime("%Y-%m-%d %H:%M:%S.000")

    with NamedTemporaryFile(suffix=".sqlite") as tmp:
        db_path = Path(tmp.name)
        create_test_db(db_path, [
            {
                "datetime_utc": ts2,  # Insert later one first to test ordering
                "duration_ms": 180000.0,
                "transcript": "Second recording.",
            },
            {
                "datetime_utc": ts1,  # Earlier timestamp
                "duration_ms": 240000.0,
                "transcript": "First recording.",
            },
        ])

        result = run_export(db_path, local_date)
        assert result.returncode == 0, f"Expected exit 0, got {result.returncode}: {result.stderr}"

        manifest = json.loads(result.stdout)
        assert len(manifest["recordings"]) == 2
        # Should be ordered by datetime (earlier first)
        assert manifest["recordings"][0]["transcript"] == "First recording."
        assert manifest["recordings"][1]["transcript"] == "Second recording."

    print("  PASS: test_multiple_recordings_ordered")


def test_segments_transcript_preferred():
    """When meta.json has segments, the formatted speaker transcript is used."""
    utc_ts, local_date = get_local_date_for_utc(18)
    folder_name = "test-segments-folder"

    with tempfile.TemporaryDirectory() as tmpdir:
        recordings_dir = Path(tmpdir)
        # Create meta.json with segments
        folder_path = recordings_dir / folder_name
        folder_path.mkdir()
        meta = {
            "segments": [
                {"text": "Hello there.", "start": 0.0, "end": 1.0, "speaker": 0, "confidence": 1},
                {"text": "How are you?", "start": 1.0, "end": 2.0, "speaker": 0, "confidence": 1},
                {"text": "I'm good, thanks.", "start": 2.0, "end": 3.5, "speaker": 1, "confidence": 1},
                {"text": "Great to hear.", "start": 3.5, "end": 4.5, "speaker": 0, "confidence": 1},
            ]
        }
        (folder_path / "meta.json").write_text(json.dumps(meta))

        with NamedTemporaryFile(suffix=".sqlite") as tmp:
            db_path = Path(tmp.name)
            create_test_db(db_path, [
                {
                    "datetime_utc": utc_ts,
                    "duration_ms": 300000.0,
                    "transcript": "Hello there. How are you? I'm good, thanks. Great to hear.",
                    "folder_name": folder_name,
                },
            ])

            result = run_export(db_path, local_date, recordings_dir)
            assert result.returncode == 0, f"Expected exit 0, got {result.returncode}: {result.stderr}"

            manifest = json.loads(result.stdout)
            transcript = manifest["recordings"][0]["transcript"]
            # Should have speaker labels with timestamps
            assert "**Speaker 0** [00:00]:" in transcript
            assert "**Speaker 1** [00:02]:" in transcript
            # Consecutive same-speaker segments should be grouped
            assert "Hello there. How are you?" in transcript
            assert "I'm good, thanks." in transcript

    print("  PASS: test_segments_transcript_preferred")


def test_falls_back_to_db_transcript_without_meta():
    """When no meta.json exists, falls back to the database transcript."""
    utc_ts, local_date = get_local_date_for_utc(18)

    with tempfile.TemporaryDirectory() as tmpdir:
        recordings_dir = Path(tmpdir)
        # No meta.json created

        with NamedTemporaryFile(suffix=".sqlite") as tmp:
            db_path = Path(tmp.name)
            create_test_db(db_path, [
                {
                    "datetime_utc": utc_ts,
                    "duration_ms": 300000.0,
                    "transcript": "Plain transcript without speakers.",
                    "folder_name": "nonexistent-folder",
                },
            ])

            result = run_export(db_path, local_date, recordings_dir)
            assert result.returncode == 0, f"Expected exit 0, got {result.returncode}: {result.stderr}"

            manifest = json.loads(result.stdout)
            assert manifest["recordings"][0]["transcript"] == "Plain transcript without speakers."

    print("  PASS: test_falls_back_to_db_transcript_without_meta")


if __name__ == "__main__":
    tests = [
        test_basic_export,
        test_filters_short_recordings,
        test_filters_empty_transcripts,
        test_no_recordings_exits_1,
        test_missing_database_exits_1,
        test_boundary_duration_included,
        test_multiple_recordings_ordered,
        test_segments_transcript_preferred,
        test_falls_back_to_db_transcript_without_meta,
    ]

    print(f"Running {len(tests)} tests...")
    failures = []
    for test in tests:
        try:
            test()
        except AssertionError as e:
            failures.append((test.__name__, str(e)))
            print(f"  FAIL: {test.__name__}: {e}")
        except Exception as e:
            failures.append((test.__name__, str(e)))
            print(f"  ERROR: {test.__name__}: {e}")

    print()
    if failures:
        print(f"{len(failures)}/{len(tests)} tests FAILED:")
        for name, msg in failures:
            print(f"  - {name}: {msg}")
        sys.exit(1)
    else:
        print(f"All {len(tests)} tests passed.")
