#!/usr/bin/env python3
"""
Process Inbox - Concurrent Pipeline Orchestrator

This script orchestrates the inbox processing pipeline with maximum concurrency:
1. Discovery: Find all items to process
2. Highlight: Run highlighting concurrently (parallel across items)
3. Extract: Generate extraction suggestions (writes YAML file)
4. Review: Interactive review of suggestions (approve/reject/edit)
5. Apply: Apply approved changes from reviewed YAML
6. Archive: Run archiving concurrently (parallel across items)

Usage:
    python process_inbox.py [content_types] [--vault-root PATH] [--max-concurrent N]

    content_types: Comma-separated list (articles,daily,meetings,assets) or empty for all

Examples:
    python process_inbox.py                    # Process all types
    python process_inbox.py articles           # Only articles
    python process_inbox.py daily,meetings     # Daily and meetings
"""

import argparse
import asyncio
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class ContentType(Enum):
    ARTICLES = "articles"
    DAILY = "daily"
    MEETINGS = "meetings"
    ASSETS = "assets"


@dataclass
class InboxItem:
    """Represents an item to be processed."""
    path: Path
    content_type: ContentType
    highlighted: bool = False
    extracted: bool = False
    processed: bool = False

    @property
    def needs_highlighting(self) -> bool:
        return not self.highlighted

    @property
    def needs_extraction(self) -> bool:
        return self.highlighted and not self.extracted

    @property
    def needs_archiving(self) -> bool:
        # Only articles and assets are archived
        if self.content_type not in (ContentType.ARTICLES, ContentType.ASSETS):
            return False
        return self.extracted and not self.processed


@dataclass
class ProcessingResult:
    """Result from processing an item."""
    item: InboxItem
    stage: str
    success: bool
    message: str = ""
    error: Optional[str] = None


@dataclass
class PipelineStats:
    """Statistics for the processing pipeline."""
    items_found: dict = field(default_factory=dict)
    highlighted: int = 0
    extracted: int = 0
    reviewed: int = 0
    applied: int = 0
    archived: int = 0
    skipped: int = 0
    errors: list = field(default_factory=list)
    suggestions_file: Optional[str] = None


def parse_frontmatter(content: str) -> dict:
    """Extract frontmatter from markdown content."""
    if not content.startswith('---'):
        return {}

    # Find the closing ---
    end_match = re.search(r'\n---\s*\n', content[3:])
    if not end_match:
        return {}

    frontmatter_text = content[4:end_match.start() + 3]

    # Simple YAML parsing for key: value pairs
    result = {}
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip()

            # Parse boolean values
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value == 'null' or value == '':
                value = None

            result[key] = value

    return result


def detect_content_type(path: Path, vault_root: Path) -> Optional[ContentType]:
    """Detect content type from file path."""
    rel_path = str(path.relative_to(vault_root))

    if rel_path.startswith('Clippings/'):
        return ContentType.ARTICLES
    elif rel_path.startswith('daily/'):
        return ContentType.DAILY
    elif rel_path.startswith('Meetings/'):
        return ContentType.MEETINGS
    elif rel_path.startswith('assets/'):
        return ContentType.ASSETS

    return None


def find_items_to_process(
    vault_root: Path,
    content_types: list[ContentType],
    days_back: int = 15
) -> list[InboxItem]:
    """Find all items that need processing."""
    items = []
    cutoff_date = datetime.now() - timedelta(days=days_back)

    for content_type in content_types:
        if content_type == ContentType.ARTICLES:
            # Clippings/*.md - no date filter, process all unprocessed
            for path in (vault_root / 'Clippings').glob('*.md'):
                items.append(create_item_from_path(path, content_type, vault_root))

        elif content_type == ContentType.DAILY:
            # daily/{year}/{month}/{day}/*.md - last 15 days
            for path in (vault_root / 'daily').rglob('*.md'):
                if path.stat().st_mtime >= cutoff_date.timestamp():
                    items.append(create_item_from_path(path, content_type, vault_root))

        elif content_type == ContentType.MEETINGS:
            # Meetings/{year}/{month}/{day}/*.md
            for path in (vault_root / 'Meetings').rglob('*.md'):
                if path.stat().st_mtime >= cutoff_date.timestamp():
                    items.append(create_item_from_path(path, content_type, vault_root))

        elif content_type == ContentType.ASSETS:
            # assets/*/summary.md
            for path in (vault_root / 'assets').glob('*/summary.md'):
                items.append(create_item_from_path(path, content_type, vault_root))

    return items


def create_item_from_path(path: Path, content_type: ContentType, vault_root: Path) -> InboxItem:
    """Create an InboxItem from a file path, reading its frontmatter state."""
    try:
        content = path.read_text(encoding='utf-8')
        frontmatter = parse_frontmatter(content)

        return InboxItem(
            path=path,
            content_type=content_type,
            highlighted=frontmatter.get('highlighted', False) is True,
            extracted=frontmatter.get('extracted', False) is True,
            processed=frontmatter.get('processed', False) is True,
        )
    except Exception:
        return InboxItem(
            path=path,
            content_type=content_type,
        )


async def run_claude_skill(skill_name: str, args: str, vault_root: Path) -> tuple[bool, str]:
    """
    Run a Claude Code skill using the CLI.

    Returns (success, output)
    """
    cmd = [
        'claude',
        '--print',  # Non-interactive mode
        '--dangerously-skip-permissions',  # Skip permission prompts for automation
        f'/{skill_name}',
        args
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=vault_root
        )

        stdout, stderr = await proc.communicate()

        success = proc.returncode == 0
        output = stdout.decode('utf-8') if stdout else ''
        if stderr:
            output += f"\nSTDERR: {stderr.decode('utf-8')}"

        return success, output

    except Exception as e:
        return False, f"Error running skill: {e}"


async def highlight_item(item: InboxItem, vault_root: Path, semaphore: asyncio.Semaphore) -> ProcessingResult:
    """Run highlighting on a single item with concurrency control."""
    async with semaphore:
        if not item.needs_highlighting:
            return ProcessingResult(
                item=item,
                stage='highlight',
                success=True,
                message='Already highlighted, skipped'
            )

        rel_path = str(item.path.relative_to(vault_root))
        print(f"  ⏳ Highlighting: {rel_path}")

        success, output = await run_claude_skill(
            'process-inbox-highlight',
            f'"{rel_path}"',
            vault_root
        )

        if success:
            item.highlighted = True
            print(f"  ✓ Highlighted: {rel_path}")
            return ProcessingResult(
                item=item,
                stage='highlight',
                success=True,
                message=output
            )
        else:
            print(f"  ✗ Failed: {rel_path}")
            return ProcessingResult(
                item=item,
                stage='highlight',
                success=False,
                error=output
            )


async def run_extraction_batch(items: list[InboxItem], vault_root: Path) -> tuple[bool, str]:
    """
    Run extraction on a batch of items, generating a YAML suggestions file.

    Returns (success, suggestions_file_path)
    """
    if not items:
        return True, ""

    # Build list of paths to extract
    paths = [str(item.path.relative_to(vault_root)) for item in items]
    paths_arg = ",".join(paths)

    print(f"  ⏳ Generating extraction suggestions for {len(items)} items...")

    success, output = await run_claude_skill(
        'process-inbox-extract',
        f'"{paths_arg}"',
        vault_root
    )

    if success:
        # Parse output to find the suggestions file path
        # Look for pattern like: .claude/processing/extract-suggestions/XXXX-suggestions.yaml
        import re
        match = re.search(r'(\.claude/processing/extract-suggestions/[^\s]+\.yaml)', output)
        if match:
            suggestions_file = match.group(1)
            print(f"  ✓ Suggestions written to: {suggestions_file}")
            return True, suggestions_file
        else:
            print(f"  ✓ Extraction complete (no suggestions file found in output)")
            return True, ""
    else:
        print(f"  ✗ Extraction failed")
        return False, output


def load_yaml_file(file_path: Path) -> Optional[dict]:
    """Load a YAML file, using PyYAML if available, otherwise basic parsing."""
    content = file_path.read_text(encoding='utf-8')

    if HAS_YAML:
        return yaml.safe_load(content)

    # Fallback: basic YAML parsing for our known structure
    # This is a simplified parser - for complex YAML, install PyYAML
    print("  ⚠ PyYAML not installed. Install with: pip install pyyaml")
    print("    Attempting basic parsing...")

    # For now, require PyYAML for proper YAML handling
    return None


def save_yaml_file(file_path: Path, data: dict) -> bool:
    """Save data to a YAML file."""
    if not HAS_YAML:
        print("  ✗ PyYAML required to save YAML files. Install with: pip install pyyaml")
        return False

    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return True


def truncate_text(text: str, max_len: int = 500) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def print_separator(char: str = "━", width: int = 60):
    """Print a separator line."""
    print(char * width)


async def regenerate_association(
    source_file: str,
    target: str,
    user_instructions: str,
    vault_root: Path
) -> Optional[dict]:
    """
    Call the extract command with user instructions to regenerate a suggestion.

    Returns the new association dict, or None if failed.
    """
    print(f"\n  ⏳ Regenerating suggestion with your instructions...")

    # Build the prompt for extraction with user guidance
    prompt = f'"{source_file}" --target "{target}" --instructions "{user_instructions}"'

    success, output = await run_claude_skill(
        'process-inbox-extract',
        prompt,
        vault_root
    )

    if not success:
        print(f"  ✗ Failed to regenerate: {output}")
        return None

    # Try to parse the new suggestion from output
    # The extract command should output YAML for a single association
    if HAS_YAML:
        try:
            # Look for YAML block in output
            yaml_match = re.search(r'```yaml\s*(.*?)\s*```', output, re.DOTALL)
            if yaml_match:
                new_assoc = yaml.safe_load(yaml_match.group(1))
                if new_assoc:
                    print(f"  ✓ Suggestion regenerated")
                    return new_assoc
        except Exception as e:
            print(f"  ⚠ Could not parse regenerated suggestion: {e}")

    return None


def display_association(assoc: dict, assoc_num: int, total_assocs: int):
    """Display an association for review."""
    print()
    print_separator()
    print(f"ASSOCIATION {assoc_num} of {total_assocs}: [{assoc.get('relevance', 'unknown').upper()}] → {assoc.get('target', 'unknown')}")
    print_separator()

    print(f"\nTarget: {assoc.get('target')} ({assoc.get('type', 'unknown')})")
    print(f"Reason: {assoc.get('reason', 'No reason provided')}")

    note = assoc.get('note_to_create', {})
    if note:
        print(f"\nNote to create: {note.get('path', 'unknown')}")
        print("─" * 60)
        content = note.get('content', '')
        print(truncate_text(content, 600))
        print("─" * 60)


async def review_association(
    assoc: dict,
    assoc_num: int,
    total_assocs: int,
    source_file: str,
    vault_root: Path
) -> tuple[str, Optional[dict]]:
    """
    Present an association for review and get user decision.

    Returns: (status, updated_assoc)
        status: 'approved', 'rejected', 'skipped', or 'quit'
        updated_assoc: If user edited, the new association dict; otherwise None
    """
    display_association(assoc, assoc_num, total_assocs)
    note = assoc.get('note_to_create', {})

    print("\nOptions:")
    print("  [a] Approve - create this note as-is")
    print("  [e] Edit    - describe changes, regenerate suggestion")
    print("  [r] Reject  - skip this association")
    print("  [s] Skip    - decide later (keep pending)")
    print("  [v] View    - see full note content")
    print("  [q] Quit    - stop review (save progress)")

    while True:
        choice = input("\nChoice [a/e/r/s/v/q]: ").strip().lower()

        if choice == 'a':
            return 'approved', None
        elif choice == 'r':
            return 'rejected', None
        elif choice == 's':
            return 'skipped', None
        elif choice == 'q':
            return 'quit', None
        elif choice == 'v':
            print("\n" + "─" * 60)
            print("FULL NOTE CONTENT:")
            print("─" * 60)
            print(note.get('content', 'No content'))
            print("─" * 60)
        elif choice == 'e':
            print("\n" + "─" * 60)
            print("EDIT: Describe what you want instead")
            print("─" * 60)
            print("Examples:")
            print("  - 'Focus more on the practical applications'")
            print("  - 'Change target to projects/other-project'")
            print("  - 'Make it shorter and more actionable'")
            print("  - 'Include the quote about X from the source'")
            print()
            instructions = input("Your instructions (or 'cancel'): ").strip()

            if instructions.lower() == 'cancel':
                display_association(assoc, assoc_num, total_assocs)
                continue

            # Regenerate with user instructions
            new_assoc = await regenerate_association(
                source_file,
                assoc.get('target', ''),
                instructions,
                vault_root
            )

            if new_assoc:
                # Show the new suggestion
                print("\n  📝 NEW SUGGESTION:")
                display_association(new_assoc, assoc_num, total_assocs)
                print("\nAccept this version? [a] Approve / [e] Edit again / [r] Reject / [s] Skip")

                sub_choice = input("\nChoice: ").strip().lower()
                if sub_choice == 'a':
                    return 'approved', new_assoc
                elif sub_choice == 'r':
                    return 'rejected', None
                elif sub_choice == 's':
                    return 'skipped', None
                elif sub_choice == 'e':
                    # Update assoc to new version and loop again
                    assoc.update(new_assoc)
                    continue
            else:
                print("  ⚠ Regeneration failed, keeping original suggestion")
                display_association(assoc, assoc_num, total_assocs)
        else:
            print("Invalid choice. Please enter a, e, r, s, v, or q.")


def review_new_creation(creation: dict) -> str:
    """
    Present a new project/area creation for review.

    Returns: 'approved', 'rejected', 'skipped', or 'quit'
    """
    print()
    print_separator()
    print(f"NEW {creation.get('type', 'PROJECT').upper()} SUGGESTED: {creation.get('name', 'unknown')}")
    print_separator()

    print(f"\nType: {creation.get('type', 'unknown')}")
    print(f"Reason: {creation.get('reason', 'No reason provided')}")
    print(f"Description: {creation.get('description', 'No description')}")

    print("\nOptions:")
    print("  [a] Approve - create this project/area")
    print("  [e] Edit    - change name or description")
    print("  [r] Reject  - don't create")
    print("  [s] Skip    - decide later")
    print("  [q] Quit    - stop review (save progress)")

    while True:
        choice = input("\nChoice [a/e/r/s/q]: ").strip().lower()

        if choice == 'a':
            return 'approved'
        elif choice == 'r':
            return 'rejected'
        elif choice == 's':
            return 'skipped'
        elif choice == 'q':
            return 'quit'
        elif choice == 'e':
            print("\nEdit options:")
            print("  [n] Change name")
            print("  [d] Change description")
            print("  [c] Cancel")
            edit_choice = input("\nWhat to edit? ").strip().lower()

            if edit_choice == 'n':
                new_name = input(f"New name (current: {creation.get('name')}): ").strip()
                if new_name:
                    creation['name'] = new_name
                    print(f"  ✓ Name updated to: {new_name}")
            elif edit_choice == 'd':
                new_desc = input(f"New description: ").strip()
                if new_desc:
                    creation['description'] = new_desc
                    print(f"  ✓ Description updated")
            # Re-display after edit
            print()
            print_separator()
            print(f"UPDATED: {creation.get('name')}")
            print(f"Type: {creation.get('type')}")
            print(f"Description: {creation.get('description')}")
        else:
            print("Invalid choice. Please enter a, e, r, s, or q.")


async def run_interactive_review(suggestions_file: Path, vault_root: Path) -> tuple[bool, dict]:
    """
    Run interactive review of extraction suggestions.

    Returns (success, stats_dict)
    """
    if not HAS_YAML:
        print("  ✗ PyYAML is required for review. Install with: pip install pyyaml")
        return False, {}

    # Load suggestions
    data = load_yaml_file(suggestions_file)
    if not data:
        print("  ✗ Failed to load suggestions file")
        return False, {}

    items = data.get('items', [])
    if not items:
        print("  ℹ No items to review")
        return True, {'approved': 0, 'rejected': 0, 'pending': 0}

    # Statistics
    stats = {'approved': 0, 'rejected': 0, 'pending': 0, 'skipped': 0}
    quit_requested = False

    # Review each item
    for item in items:
        if quit_requested:
            break

        source_file = item.get('source_file', 'Unknown')
        source_title = item.get('source_title', Path(source_file).stem if source_file else 'Unknown')

        # Check if item has pending associations or creations
        associations = item.get('associations', [])
        new_creations = item.get('new_creations', [])

        pending_assocs = [a for a in associations if a.get('status') == 'pending']
        pending_creations = [c for c in new_creations if c.get('status') == 'pending']

        if not pending_assocs and not pending_creations:
            continue

        # Print item header
        print("\n")
        print_separator("━")
        print(f"REVIEW: {source_title}")
        print_separator("━")
        print(f"\nSource: {source_file}")
        print(f"Type: {item.get('source_type', 'unknown')}")

        # Show highlighted passages
        passages = item.get('highlighted_passages', [])
        if passages:
            print("\nHighlighted passages:")
            for p in passages[:3]:  # Show first 3
                print(f"  • \"{truncate_text(p, 100)}\"")

        # Review associations
        total_assocs = len(pending_assocs)
        for assoc_idx, assoc in enumerate(associations):
            if assoc.get('status') != 'pending':
                continue

            result, updated_assoc = await review_association(
                assoc, assoc_idx + 1, total_assocs, source_file, vault_root
            )

            # If user edited the association, update it
            if updated_assoc:
                associations[assoc_idx] = updated_assoc
                assoc = updated_assoc

            if result == 'quit':
                quit_requested = True
                break

            assoc['status'] = result if result != 'skipped' else 'pending'

            if result == 'approved':
                stats['approved'] += 1
            elif result == 'rejected':
                stats['rejected'] += 1
            else:
                stats['pending'] += 1

        if quit_requested:
            break

        # Review new creations
        for creation in new_creations:
            if creation.get('status') != 'pending':
                continue

            result = review_new_creation(creation)

            if result == 'quit':
                quit_requested = True
                break

            creation['status'] = result if result != 'skipped' else 'pending'

            if result == 'approved':
                stats['approved'] += 1
            elif result == 'rejected':
                stats['rejected'] += 1
            else:
                stats['pending'] += 1

    # Update metadata
    if 'metadata' not in data:
        data['metadata'] = {}
    data['metadata']['status'] = 'reviewed'
    data['metadata']['reviewed_date'] = datetime.now().isoformat()

    # Save updated YAML
    if save_yaml_file(suggestions_file, data):
        print(f"\n  ✓ Saved review to: {suggestions_file}")
    else:
        print(f"\n  ✗ Failed to save review")
        return False, stats

    return True, stats


async def run_review(suggestions_file: str, vault_root: Path) -> tuple[bool, str]:
    """
    Run interactive review of extraction suggestions.

    Returns (success, output)
    """
    if not suggestions_file:
        return True, "No suggestions to review"

    print(f"\n  📋 Starting review of suggestions...")
    print(f"     File: {suggestions_file}")

    suggestions_path = vault_root / suggestions_file
    if not suggestions_path.exists():
        print(f"  ✗ Suggestions file not found: {suggestions_file}")
        return False, "Suggestions file not found"

    success, stats = await run_interactive_review(suggestions_path, vault_root)

    if success:
        # Print summary
        print()
        print_separator("━")
        print("REVIEW COMPLETE")
        print_separator("━")
        print(f"\n  ✓ Approved: {stats.get('approved', 0)}")
        print(f"  ✗ Rejected: {stats.get('rejected', 0)}")
        print(f"  ⏸ Pending:  {stats.get('pending', 0)}")

        return True, "Review complete"
    else:
        return False, "Review failed"


def update_frontmatter_in_file(file_path: Path, updates: dict) -> bool:
    """Update frontmatter fields in a markdown file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        if not content.startswith('---'):
            return False

        end_match = re.search(r'\n---\s*\n', content[3:])
        if not end_match:
            return False

        fm_text = content[3:3 + end_match.start()]
        body = content[3 + end_match.end():]

        fm_dict = {}
        for line in fm_text.split('\n'):
            if ':' in line and not line.startswith(' '):
                key, _, value = line.partition(':')
                key = key.strip()
                value = value.strip()
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value == 'null' or value == '':
                    value = None
                fm_dict[key] = value

        fm_dict.update(updates)

        lines = ['---']
        for key, value in fm_dict.items():
            if isinstance(value, bool):
                lines.append(f"{key}: {str(value).lower()}")
            elif value is None:
                lines.append(f"{key}: null")
            else:
                lines.append(f"{key}: {value}")
        lines.append('---')

        new_content = '\n'.join(lines) + '\n' + body
        file_path.write_text(new_content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"  ⚠ Failed to update frontmatter for {file_path}: {e}")
        return False


def append_to_processing_log(vault_root: Path, archived: list[str], notes_created: list[str]):
    """Append to _meta/processing-log.md. Creates dir and file on first run."""
    meta_dir = vault_root / '_meta'
    meta_dir.mkdir(exist_ok=True)

    log_path = meta_dir / 'processing-log.md'
    today = datetime.now().strftime('%Y-%m-%d')

    entry_lines = [f"\n## {today}\n"]

    if archived:
        entry_lines.append("\n### Archived\n")
        for item in archived:
            entry_lines.append(f"- {item}\n")

    if notes_created:
        entry_lines.append("\n### Integration Notes Created\n")
        for item in notes_created:
            entry_lines.append(f"- {item}\n")

    entry = ''.join(entry_lines)

    if log_path.exists():
        existing = log_path.read_text(encoding='utf-8')
        log_path.write_text(existing + entry, encoding='utf-8')
    else:
        header = "# Processing Log\n\nAudit trail of vault processing operations.\n"
        log_path.write_text(header + entry, encoding='utf-8')

    print(f"  ✓ Updated processing log: {log_path.relative_to(vault_root)}")


async def run_apply(suggestions_file: str, vault_root: Path) -> tuple[bool, str]:
    """
    Apply approved suggestions from the reviewed YAML file.

    Directly creates integration notes and updates frontmatter instead of
    delegating to a separate skill.

    Returns (success, output)
    """
    if not suggestions_file:
        return True, "No suggestions to apply"

    print(f"\n  ⏳ Applying approved suggestions...")

    suggestions_path = vault_root / suggestions_file
    if not suggestions_path.exists():
        print(f"  ✗ Suggestions file not found: {suggestions_file}")
        return False, "Suggestions file not found"

    data = load_yaml_file(suggestions_path)
    if not data:
        print(f"  ✗ Failed to load suggestions file")
        return False, "Failed to load YAML"

    items = data.get('items', [])
    notes_created = []
    source_files_updated = []

    for item in items:
        source_file = item.get('source_file', '')
        source_path = vault_root / source_file

        for assoc in item.get('associations', []):
            if assoc.get('status') != 'approved':
                continue

            note = assoc.get('note_to_create', {})
            note_path_str = note.get('path', '')
            note_content = note.get('content', '')

            if not note_path_str or not note_content:
                continue

            note_path = vault_root / note_path_str

            # Create parent directories
            note_path.parent.mkdir(parents=True, exist_ok=True)

            if note_path.exists():
                # Append "See also" link instead of overwriting
                existing = note_path.read_text(encoding='utf-8')
                see_also = f"\n\nSee also: [[{source_file}]]\n"
                if source_file not in existing:
                    note_path.write_text(existing + see_also, encoding='utf-8')
                    print(f"  ✓ Appended link to existing: {note_path_str}")
                else:
                    print(f"  ℹ Already linked: {note_path_str}")
            else:
                note_path.write_text(note_content, encoding='utf-8')
                print(f"  ✓ Created: {note_path_str}")

            notes_created.append(f"`{note_path_str}` (from: {source_file})")

        # Update source frontmatter
        if source_path.exists():
            today = datetime.now().strftime('%Y-%m-%d')
            update_frontmatter_in_file(source_path, {
                'extracted': True,
                'extracted_date': today,
            })
            source_files_updated.append(source_file)

    # Handle new_creations (approved project/area folders)
    for item in items:
        for creation in item.get('new_creations', []):
            if creation.get('status') != 'approved':
                continue

            creation_type = creation.get('type', 'project')
            name = creation.get('name', '')
            description = creation.get('description', '')

            if not name:
                continue

            base = 'projects' if creation_type == 'project' else 'areas'
            folder = vault_root / base / name
            folder.mkdir(parents=True, exist_ok=True)

            index_path = folder / 'index.md'
            if not index_path.exists():
                index_content = f"---\ncreated: {datetime.now().strftime('%Y-%m-%d')}\ntype: {creation_type}\n---\n\n# {name}\n\n{description}\n"
                index_path.write_text(index_content, encoding='utf-8')
                print(f"  ✓ Created {creation_type}: {base}/{name}/")
                notes_created.append(f"`{base}/{name}/index.md` (new {creation_type})")

    # Write processing log
    if notes_created or source_files_updated:
        append_to_processing_log(vault_root, source_files_updated, notes_created)

    print(f"\n  ✓ Applied: {len(notes_created)} notes created, {len(source_files_updated)} sources updated")
    return True, f"Applied {len(notes_created)} notes"


async def extract_item(item: InboxItem, vault_root: Path) -> ProcessingResult:
    """
    Run extraction on a single item.

    Note: This is now only used for single-item extraction.
    For batch processing, use run_extraction_batch instead.
    """
    if not item.needs_extraction:
        return ProcessingResult(
            item=item,
            stage='extract',
            success=True,
            message='Not ready for extraction or already extracted'
        )

    rel_path = str(item.path.relative_to(vault_root))
    print(f"  ⏳ Extracting: {rel_path}")

    success, error_output = await run_claude_skill(
        'process-inbox-extract',
        f'"{rel_path}"',
        vault_root
    )

    if success:
        item.extracted = True
        print(f"  ✓ Extracted: {rel_path}")
        return ProcessingResult(
            item=item,
            stage='extract',
            success=True,
            message='Extraction complete'
        )
    else:
        print(f"  ✗ Failed: {rel_path}")
        return ProcessingResult(
            item=item,
            stage='extract',
            success=False,
            error=error_output or 'Extraction failed'
        )


async def archive_item(item: InboxItem, vault_root: Path, semaphore: asyncio.Semaphore) -> ProcessingResult:
    """Run archiving on a single item with concurrency control."""
    async with semaphore:
        if not item.needs_archiving:
            return ProcessingResult(
                item=item,
                stage='archive',
                success=True,
                message='Not archivable or already archived'
            )

        rel_path = str(item.path.relative_to(vault_root))
        print(f"  ⏳ Archiving: {rel_path}")

        success, output = await run_claude_skill(
            'process-inbox-archive',
            f'"{rel_path}"',
            vault_root
        )

        if success:
            item.processed = True
            print(f"  ✓ Archived: {rel_path}")
            return ProcessingResult(
                item=item,
                stage='archive',
                success=True,
                message=output
            )
        else:
            print(f"  ✗ Failed: {rel_path}")
            return ProcessingResult(
                item=item,
                stage='archive',
                success=False,
                error=output
            )


def print_discovery_summary(items: list[InboxItem], stats: PipelineStats):
    """Print a summary of discovered items."""
    print("\n" + "━" * 60)
    print(f"INBOX PROCESSING - {datetime.now().strftime('%Y-%m-%d')}")
    print("━" * 60)

    # Count by type and stage
    for ct in ContentType:
        type_items = [i for i in items if i.content_type == ct]
        if type_items:
            needs_highlight = sum(1 for i in type_items if i.needs_highlighting)
            needs_extract = sum(1 for i in type_items if i.needs_extraction)
            needs_archive = sum(1 for i in type_items if i.needs_archiving)

            stats.items_found[ct.value] = len(type_items)

            print(f"\n{ct.value.capitalize()}: {len(type_items)} items")
            print(f"  - Needs highlighting: {needs_highlight}")
            print(f"  - Needs extraction: {needs_extract}")
            if ct in (ContentType.ARTICLES, ContentType.ASSETS):
                print(f"  - Needs archiving: {needs_archive}")

    total = len(items)
    total_highlight = sum(1 for i in items if i.needs_highlighting)
    total_extract = sum(1 for i in items if i.needs_extraction)
    total_archive = sum(1 for i in items if i.needs_archiving)

    print(f"\n{'─' * 60}")
    print(f"Total: {total} items")
    print(f"  - To highlight: {total_highlight}")
    print(f"  - To extract: {total_extract}")
    print(f"  - To archive: {total_archive}")
    print("━" * 60)


def print_final_summary(stats: PipelineStats):
    """Print final processing summary."""
    print("\n" + "━" * 60)
    print("PROCESSING COMPLETE")
    print("━" * 60)

    print(f"\nHighlighted: {stats.highlighted} items")
    print(f"Extracted: {stats.extracted} items")
    print(f"Reviewed: {stats.reviewed} items")
    print(f"Applied: {stats.applied} items")
    print(f"Archived: {stats.archived} items")
    print(f"Skipped: {stats.skipped} items")

    if stats.suggestions_file:
        print(f"\nSuggestions file: {stats.suggestions_file}")

    if stats.errors:
        print(f"\nErrors: {len(stats.errors)}")
        for error in stats.errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(stats.errors) > 5:
            print(f"  ... and {len(stats.errors) - 5} more")

    print("━" * 60)


async def batch_approve_suggestions(
    suggestions_file: Path,
    approve_all: bool = False
) -> tuple[bool, dict]:
    """
    Auto-approve suggestions in a YAML file without interactive review.

    If approve_all is True, approves everything.
    Otherwise, only approves HIGH relevance associations.

    Returns (success, stats_dict)
    """
    if not HAS_YAML:
        print("  ✗ PyYAML is required for batch mode. Install with: pip install pyyaml")
        return False, {}

    data = load_yaml_file(suggestions_file)
    if not data:
        print("  ✗ Failed to load suggestions file")
        return False, {}

    stats = {'approved': 0, 'rejected': 0, 'skipped': 0}

    for item in data.get('items', []):
        for assoc in item.get('associations', []):
            if assoc.get('status') != 'pending':
                continue

            relevance = assoc.get('relevance', '').lower()
            if approve_all or relevance == 'high':
                assoc['status'] = 'approved'
                stats['approved'] += 1
            else:
                stats['skipped'] += 1

        for creation in item.get('new_creations', []):
            if creation.get('status') != 'pending':
                continue
            if approve_all:
                creation['status'] = 'approved'
                stats['approved'] += 1
            else:
                stats['skipped'] += 1

    if 'metadata' not in data:
        data['metadata'] = {}
    data['metadata']['status'] = 'reviewed'
    data['metadata']['reviewed_date'] = datetime.now().isoformat()
    data['metadata']['review_mode'] = 'batch-all' if approve_all else 'batch-high'

    if save_yaml_file(suggestions_file, data):
        print(f"\n  ✓ Batch approved: {stats['approved']} items")
        if stats['skipped']:
            print(f"  ⏸ Skipped (not HIGH): {stats['skipped']} items")
        return True, stats
    else:
        return False, stats


async def run_pipeline(
    vault_root: Path,
    content_types: list[ContentType],
    max_concurrent: int = 5,
    days_back: int = 15,
    batch: bool = False,
    batch_all: bool = False,
):
    """Run the full processing pipeline with maximum concurrency."""
    stats = PipelineStats()

    # Step 1: Discovery
    print("\n🔍 Discovering items to process...")
    items = find_items_to_process(vault_root, content_types, days_back)

    if not items:
        print("\nNo items found for processing.")
        return

    print_discovery_summary(items, stats)

    # Ask for confirmation
    response = input("\nContinue with processing? (y/n): ")
    if response.lower() != 'y':
        print("Aborted.")
        return

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(max_concurrent)

    # Step 2: Highlighting (concurrent)
    items_to_highlight = [i for i in items if i.needs_highlighting]
    if items_to_highlight:
        print(f"\n{'━' * 60}")
        print(f"STAGE 1: HIGHLIGHTING ({len(items_to_highlight)} items)")
        print("━" * 60)

        highlight_tasks = [
            highlight_item(item, vault_root, semaphore)
            for item in items_to_highlight
        ]

        results = await asyncio.gather(*highlight_tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                stats.errors.append(str(result))
            elif result.success:
                if 'skipped' not in result.message.lower():
                    stats.highlighted += 1
                else:
                    stats.skipped += 1
            else:
                stats.errors.append(result.error or 'Unknown error')

    # Refresh item states after highlighting
    for item in items:
        try:
            content = item.path.read_text(encoding='utf-8')
            fm = parse_frontmatter(content)
            item.highlighted = fm.get('highlighted', False) is True
        except Exception:
            pass

    # Step 3: Extraction (generates YAML suggestions file)
    items_to_extract = [i for i in items if i.needs_extraction]
    if items_to_extract:
        print(f"\n{'━' * 60}")
        print(f"STAGE 2: EXTRACTION ({len(items_to_extract)} items)")
        print("━" * 60)
        print("\nGenerating extraction suggestions...\n")

        success, suggestions_file = await run_extraction_batch(
            items_to_extract, vault_root
        )

        if success and suggestions_file:
            stats.extracted = len(items_to_extract)
            stats.suggestions_file = suggestions_file

            # Step 4: Review (interactive or batch)
            print(f"\n{'━' * 60}")
            print("STAGE 3: REVIEW")
            print("━" * 60)

            if batch or batch_all:
                mode_label = "all" if batch_all else "HIGH relevance only"
                print(f"\nBatch mode: auto-approving {mode_label}...\n")
                suggestions_path = vault_root / suggestions_file
                review_success, _ = await batch_approve_suggestions(
                    suggestions_path, approve_all=batch_all
                )
            else:
                print("\nReview suggestions and approve/reject each one.\n")
                review_success, _ = await run_review(suggestions_file, vault_root)

            if review_success:
                stats.reviewed = len(items_to_extract)

                # Step 5: Apply (applies approved changes)
                print(f"\n{'━' * 60}")
                print("STAGE 4: APPLY")
                print("━" * 60)

                apply_success, _ = await run_apply(suggestions_file, vault_root)

                if apply_success:
                    stats.applied = len(items_to_extract)

                    # Refresh item states after apply
                    for item in items:
                        try:
                            content = item.path.read_text(encoding='utf-8')
                            fm = parse_frontmatter(content)
                            item.extracted = fm.get('extracted', False) is True
                        except Exception:
                            pass
                else:
                    stats.errors.append("Apply step failed")
            else:
                stats.errors.append("Review step cancelled or failed")
        elif not success:
            stats.errors.append("Extraction failed to generate suggestions")

    # Step 6: Archiving (concurrent)
    items_to_archive = [i for i in items if i.needs_archiving]
    if items_to_archive:
        print(f"\n{'━' * 60}")
        print(f"STAGE 5: ARCHIVING ({len(items_to_archive)} items)")
        print("━" * 60)

        archive_tasks = [
            archive_item(item, vault_root, semaphore)
            for item in items_to_archive
        ]

        results = await asyncio.gather(*archive_tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                stats.errors.append(str(result))
            elif result.success:
                if 'not archivable' not in result.message.lower():
                    stats.archived += 1
            else:
                stats.errors.append(result.error or 'Unknown error')

    # Final summary
    print_final_summary(stats)


def find_vault_root(start_path: Path) -> Path:
    """Find the Obsidian vault root by looking for .obsidian folder."""
    current = start_path.resolve()

    while current != current.parent:
        if (current / '.obsidian').exists():
            return current
        current = current.parent

    # Fallback to current directory
    return Path.cwd()


def main():
    parser = argparse.ArgumentParser(
        description='Process inbox items concurrently using the inbox processing pipeline'
    )
    parser.add_argument(
        'content_types',
        nargs='?',
        default='',
        help='Comma-separated content types (articles,daily,meetings,assets) or empty for all'
    )
    parser.add_argument(
        '--vault-root',
        type=Path,
        help='Root directory of Obsidian vault (default: auto-detect)'
    )
    parser.add_argument(
        '--max-concurrent',
        type=int,
        default=5,
        help='Maximum concurrent operations (default: 5)'
    )
    parser.add_argument(
        '--days-back',
        type=int,
        default=15,
        help='Number of days back to look for items (default: 15)'
    )
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Auto-approve HIGH relevance suggestions, skip interactive review'
    )
    parser.add_argument(
        '--batch-all',
        action='store_true',
        help='Auto-approve ALL suggestions, skip interactive review'
    )

    args = parser.parse_args()

    # Determine vault root
    vault_root = args.vault_root or find_vault_root(Path.cwd())
    print(f"Vault root: {vault_root}")

    # Parse content types
    if args.content_types:
        type_names = [t.strip() for t in args.content_types.split(',')]
        content_types = []
        for name in type_names:
            try:
                content_types.append(ContentType(name))
            except ValueError:
                print(f"Unknown content type: {name}")
                print(f"Valid types: {', '.join(ct.value for ct in ContentType)}")
                sys.exit(1)
    else:
        content_types = list(ContentType)

    # Run the pipeline
    asyncio.run(run_pipeline(
        vault_root=vault_root,
        content_types=content_types,
        max_concurrent=args.max_concurrent,
        days_back=args.days_back,
        batch=args.batch,
        batch_all=args.batch_all,
    ))


if __name__ == '__main__':
    main()
