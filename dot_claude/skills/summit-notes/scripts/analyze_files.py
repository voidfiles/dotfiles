#!/usr/bin/env python3
"""
Summit Notes - File Analysis and Categorization

Step 1 of the summit-notes pipeline.
Analyzes files in a summit folder concurrently and creates manifest.yaml.

Usage:
    python analyze_files.py <summit_folder> [--max-concurrent N] [--force]

Examples:
    python analyze_files.py /path/to/summit/
    python analyze_files.py /path/to/summit/ --max-concurrent 3
    python analyze_files.py /path/to/summit/ --force  # Re-analyze all files
"""

import argparse
import asyncio
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    print("Warning: PyYAML not installed. Install with: pip install pyyaml")


# File type constants
FILE_TYPES = ["transcript", "notes", "agenda", "summary", "pre_read", "other"]


@dataclass
class FileMetadata:
    """Metadata extracted from file analysis."""
    speakers: list[str] = field(default_factory=list)
    date_referenced: str = ""
    tags: list[str] = field(default_factory=list)
    line_count: int = 0
    duration_estimate: str = ""


@dataclass
class FileEntry:
    """Entry for a single file in the manifest."""
    path: str
    filename: str
    type: str = "pending"
    status: str = "pending"  # pending | analyzing | analyzed | error
    analyzed_at: str = ""
    size_bytes: int = 0
    checksum: str = ""
    metadata: FileMetadata = field(default_factory=FileMetadata)
    error_message: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        d = {
            "path": self.path,
            "filename": self.filename,
            "type": self.type,
            "status": self.status,
            "analyzed_at": self.analyzed_at,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
            "metadata": {
                "speakers": self.metadata.speakers,
                "date_referenced": self.metadata.date_referenced,
                "tags": self.metadata.tags,
                "line_count": self.metadata.line_count,
            }
        }
        if self.metadata.duration_estimate:
            d["metadata"]["duration_estimate"] = self.metadata.duration_estimate
        if self.error_message:
            d["error_message"] = self.error_message
        return d


@dataclass
class Manifest:
    """The complete manifest.yaml structure."""
    version: str = "1.0"
    summit_folder: str = ""
    created_at: str = ""
    updated_at: str = ""
    analyzed_by: str = ""
    files: list[FileEntry] = field(default_factory=list)

    def get_summary(self) -> dict:
        """Generate summary statistics."""
        by_type = {}
        by_status = {}
        for f in self.files:
            by_type[f.type] = by_type.get(f.type, 0) + 1
            by_status[f.status] = by_status.get(f.status, 0) + 1
        return {
            "total_files": len(self.files),
            "by_type": by_type,
            "by_status": by_status
        }

    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        return {
            "version": self.version,
            "summit_folder": self.summit_folder,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "analyzed_by": self.analyzed_by,
            "files": [f.to_dict() for f in self.files],
            "summary": self.get_summary()
        }


def calculate_checksum(file_path: Path) -> str:
    """Calculate SHA256 checksum for a file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return f"sha256:{sha256.hexdigest()[:16]}"


def get_file_preview(file_path: Path, num_lines: int = 100) -> str:
    """Read first N lines of a file for analysis."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= num_lines:
                    break
                lines.append(line)
            return ''.join(lines)
    except Exception as e:
        return f"Error reading file: {e}"


def count_lines(file_path: Path) -> int:
    """Count total lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


async def classify_file_with_claude(
    file_path: Path,
    summit_folder: Path,
    semaphore: asyncio.Semaphore
) -> tuple[str, FileMetadata, Optional[str]]:
    """
    Use Claude to classify a file and extract metadata.

    Returns: (file_type, metadata, error_message)
    """
    async with semaphore:
        rel_path = file_path.relative_to(summit_folder)
        print(f"  Analyzing: {rel_path}")

        # Get file preview
        preview = get_file_preview(file_path, 150)

        # Build the classification prompt
        prompt = f'''Analyze this file and classify its type for summit note processing.

File: {file_path.name}

<content_preview>
{preview}
</content_preview>

Classify as ONE of these types:
- transcript: Meeting transcript with speaker dialogue, timestamps, raw conversation
- notes: Handwritten or informal meeting notes, bullet points
- agenda: Schedule, topic list, or meeting plan
- summary: Existing summary document (already processed)
- pre_read: Background material shared before the event
- other: Doesn't fit above categories

Also extract if identifiable:
- speakers: List of speaker names mentioned
- date_referenced: Any specific dates mentioned (format: YYYY-MM-DD)
- tags: Relevant topic keywords (3-5 max)
- duration_estimate: Estimated duration if a transcript

Return ONLY valid JSON in this exact format:
{{"type": "transcript", "speakers": ["Alice", "Bob"], "date_referenced": "2026-02-03", "tags": ["strategy", "planning"], "duration_estimate": "2 hours"}}
'''

        # Call Claude CLI
        cmd = [
            'claude',
            '--print',
            '--dangerously-skip-permissions',
            '-p', prompt
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=summit_folder
            )

            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                error = stderr.decode('utf-8') if stderr else 'Unknown error'
                print(f"    Error: {rel_path}")
                return "other", FileMetadata(), error

            output = stdout.decode('utf-8').strip()

            # Parse JSON response
            # Find JSON in the output (in case there's extra text)
            json_match = re.search(r'\{[^}]+\}', output)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    file_type = result.get("type", "other")
                    if file_type not in FILE_TYPES:
                        file_type = "other"

                    metadata = FileMetadata(
                        speakers=result.get("speakers", []),
                        date_referenced=result.get("date_referenced", ""),
                        tags=result.get("tags", []),
                        duration_estimate=result.get("duration_estimate", ""),
                        line_count=count_lines(file_path)
                    )

                    print(f"    Classified: {rel_path} -> {file_type}")
                    return file_type, metadata, None

                except json.JSONDecodeError as e:
                    print(f"    JSON parse error: {rel_path}")
                    return "other", FileMetadata(line_count=count_lines(file_path)), f"JSON parse error: {e}"
            else:
                print(f"    No JSON found: {rel_path}")
                return "other", FileMetadata(line_count=count_lines(file_path)), "No JSON in response"

        except Exception as e:
            print(f"    Exception: {rel_path} - {e}")
            return "other", FileMetadata(), str(e)


async def analyze_file(
    file_path: Path,
    summit_folder: Path,
    semaphore: asyncio.Semaphore,
    existing_entry: Optional[FileEntry] = None,
    force: bool = False
) -> FileEntry:
    """Analyze a single file and return a FileEntry."""
    rel_path = str(file_path.relative_to(summit_folder))

    # Calculate checksum
    checksum = calculate_checksum(file_path)

    # Check if already analyzed and unchanged
    if existing_entry and not force:
        if existing_entry.checksum == checksum and existing_entry.status == "analyzed":
            print(f"  Skipping (unchanged): {rel_path}")
            return existing_entry

    # Get file info
    stat = file_path.stat()

    # Create entry
    entry = FileEntry(
        path=rel_path,
        filename=file_path.name,
        size_bytes=stat.st_size,
        checksum=checksum,
        status="analyzing"
    )

    # Classify with Claude
    file_type, metadata, error = await classify_file_with_claude(
        file_path, summit_folder, semaphore
    )

    entry.type = file_type
    entry.metadata = metadata
    entry.analyzed_at = datetime.now().isoformat()

    if error:
        entry.status = "error"
        entry.error_message = error
    else:
        entry.status = "analyzed"

    return entry


def find_files(summit_folder: Path) -> list[Path]:
    """Find all markdown files in the summit folder (excluding hidden/generated)."""
    files = []

    # Patterns to exclude
    exclude_patterns = [
        'manifest.yaml',
        'conversations.yaml',
        'conversations/',
        'chunk_summaries/',
        'chunks/',
        'downloads/',
        '.DS_Store',
        'summit_summary.md',
    ]

    for file_path in summit_folder.rglob('*.md'):
        rel_path = str(file_path.relative_to(summit_folder))

        # Skip excluded patterns
        skip = False
        for pattern in exclude_patterns:
            if rel_path.startswith(pattern) or pattern in rel_path:
                skip = True
                break

        if not skip:
            files.append(file_path)

    return sorted(files)


def load_existing_manifest(summit_folder: Path) -> Optional[Manifest]:
    """Load existing manifest.yaml if it exists."""
    manifest_path = summit_folder / 'manifest.yaml'
    if not manifest_path.exists():
        return None

    if not HAS_YAML:
        print("Warning: Cannot load existing manifest without PyYAML")
        return None

    try:
        with open(manifest_path, 'r') as f:
            data = yaml.safe_load(f)

        manifest = Manifest(
            version=data.get('version', '1.0'),
            summit_folder=data.get('summit_folder', ''),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
            analyzed_by=data.get('analyzed_by', ''),
        )

        for f_data in data.get('files', []):
            meta_data = f_data.get('metadata', {})
            metadata = FileMetadata(
                speakers=meta_data.get('speakers', []),
                date_referenced=meta_data.get('date_referenced', ''),
                tags=meta_data.get('tags', []),
                line_count=meta_data.get('line_count', 0),
                duration_estimate=meta_data.get('duration_estimate', ''),
            )
            entry = FileEntry(
                path=f_data.get('path', ''),
                filename=f_data.get('filename', ''),
                type=f_data.get('type', 'pending'),
                status=f_data.get('status', 'pending'),
                analyzed_at=f_data.get('analyzed_at', ''),
                size_bytes=f_data.get('size_bytes', 0),
                checksum=f_data.get('checksum', ''),
                metadata=metadata,
                error_message=f_data.get('error_message', ''),
            )
            manifest.files.append(entry)

        return manifest
    except Exception as e:
        print(f"Warning: Could not load existing manifest: {e}")
        return None


def save_manifest(manifest: Manifest, summit_folder: Path) -> bool:
    """Save manifest to YAML file."""
    if not HAS_YAML:
        print("Error: PyYAML required to save manifest. Install with: pip install pyyaml")
        return False

    manifest_path = summit_folder / 'manifest.yaml'

    try:
        with open(manifest_path, 'w') as f:
            yaml.dump(
                manifest.to_dict(),
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )
        return True
    except Exception as e:
        print(f"Error saving manifest: {e}")
        return False


async def main():
    parser = argparse.ArgumentParser(description='Analyze summit folder files')
    parser.add_argument('summit_folder', type=str, help='Path to summit folder')
    parser.add_argument('--max-concurrent', type=int, default=5,
                        help='Maximum concurrent Claude calls (default: 5)')
    parser.add_argument('--force', action='store_true',
                        help='Force re-analysis of all files')

    args = parser.parse_args()

    summit_folder = Path(args.summit_folder).resolve()

    if not summit_folder.exists():
        print(f"Error: Summit folder does not exist: {summit_folder}")
        sys.exit(1)

    if not summit_folder.is_dir():
        print(f"Error: Path is not a directory: {summit_folder}")
        sys.exit(1)

    print(f"\n Summit Notes - File Analysis")
    print(f"{'=' * 50}")
    print(f"Folder: {summit_folder}")
    print(f"Max concurrent: {args.max_concurrent}")
    print(f"Force re-analyze: {args.force}")
    print()

    # Load existing manifest for incremental processing
    existing_manifest = load_existing_manifest(summit_folder)
    existing_by_path = {}
    if existing_manifest:
        existing_by_path = {e.path: e for e in existing_manifest.files}
        print(f"Found existing manifest with {len(existing_by_path)} files")

    # Find files to analyze
    files = find_files(summit_folder)
    print(f"Found {len(files)} files to analyze")
    print()

    if not files:
        print("No files found to analyze.")
        sys.exit(0)

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(args.max_concurrent)

    # Analyze all files concurrently
    tasks = [
        analyze_file(
            file_path,
            summit_folder,
            semaphore,
            existing_by_path.get(str(file_path.relative_to(summit_folder))),
            args.force
        )
        for file_path in files
    ]

    print("Analyzing files...")
    entries = await asyncio.gather(*tasks)

    # Create manifest
    now = datetime.now().isoformat()
    manifest = Manifest(
        version="1.0",
        summit_folder=str(summit_folder),
        created_at=existing_manifest.created_at if existing_manifest else now,
        updated_at=now,
        analyzed_by=os.environ.get('USER', 'claude-summit-notes'),
        files=list(entries)
    )

    # Save manifest
    print()
    print("Saving manifest.yaml...")
    if save_manifest(manifest, summit_folder):
        print(f"  Saved to: {summit_folder / 'manifest.yaml'}")
    else:
        print("  Failed to save manifest!")
        sys.exit(1)

    # Print summary
    summary = manifest.get_summary()
    print()
    print(f"Analysis Complete")
    print(f"{'=' * 50}")
    print(f"Total files: {summary['total_files']}")
    print()
    print("By type:")
    for t, count in summary['by_type'].items():
        print(f"  {t}: {count}")
    print()
    print("By status:")
    for s, count in summary['by_status'].items():
        print(f"  {s}: {count}")

    # Check for errors
    errors = [e for e in entries if e.status == "error"]
    if errors:
        print()
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e.path}: {e.error_message}")


if __name__ == '__main__':
    asyncio.run(main())
