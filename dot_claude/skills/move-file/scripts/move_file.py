#!/usr/bin/env python3
"""
Move files or folders in an Obsidian vault while updating wiki links.

This script:
1. Finds all markdown files that reference the source file/folder
2. Updates wiki links to reflect the new location
3. Moves the file/folder to the destination
4. Preserves link formats (with/without extensions, aliases, embeds)
"""

import argparse
import re
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class WikiLink:
    """Represents a wiki link found in a file."""
    original: str  # Full match including [[ ]]
    target: str    # The file/path being linked to
    alias: Optional[str]  # Display text if using |alias
    is_embed: bool  # True if ![[...]]
    has_extension: bool  # True if .md is included


def parse_wiki_links(content: str) -> List[WikiLink]:
    """
    Extract all wiki links from markdown content.

    Matches:
    - [[filename]]
    - [[filename.md]]
    - [[filename|alias]]
    - [[folder/filename]]
    - ![[filename]]  (embeds)
    """
    # Pattern: optional !, [[, target (path), optional |alias, ]]
    pattern = r'(!?)\[\[([^\]|]+)(\|[^\]]+)?\]\]'
    links = []

    for match in re.finditer(pattern, content):
        is_embed = match.group(1) == '!'
        target = match.group(2).strip()
        alias = match.group(3)[1:].strip() if match.group(3) else None
        has_extension = target.endswith('.md')

        links.append(WikiLink(
            original=match.group(0),
            target=target,
            alias=alias,
            is_embed=is_embed,
            has_extension=has_extension
        ))

    return links


def normalize_path(path: str, has_extension: bool = False) -> str:
    """
    Normalize a file path for comparison.
    Removes .md extension if not explicitly included in the link.
    """
    path = path.replace('\\', '/')
    if not has_extension and path.endswith('.md'):
        path = path[:-3]
    return path


def should_update_link(link: WikiLink, old_path: Path, vault_root: Path, is_folder_move: bool = False) -> bool:
    """
    Determine if a wiki link should be updated.

    Args:
        link: The wiki link to check
        old_path: Original path of file/folder being moved
        vault_root: Root of the Obsidian vault
        is_folder_move: True if moving a folder

    Returns:
        True if the link references the file/folder being moved
    """
    # Normalize the link target
    link_target = normalize_path(link.target, link.has_extension)

    if is_folder_move:
        # For folder moves, check if link is to any file within the folder
        old_rel = old_path.relative_to(vault_root)
        # Check if link starts with the folder path
        if '/' in link_target:
            link_folder = link_target.split('/')[0]
            return str(old_rel).startswith(link_folder) or link_folder == old_rel.name
        return False
    else:
        # For file moves, check if link matches the file
        old_rel = old_path.relative_to(vault_root)

        # Try matching with and without .md extension
        old_path_no_ext = str(old_rel)[:-3] if str(old_rel).endswith('.md') else str(old_rel)
        old_name_no_ext = old_path.stem

        # Match on full relative path or just filename
        return (link_target == old_path_no_ext or
                link_target == str(old_rel) or
                link_target == old_name_no_ext or
                link_target == old_path.name)


def calculate_new_link_target(
    link: WikiLink,
    old_path: Path,
    new_path: Path,
    vault_root: Path,
    linking_file: Path,
    is_folder_move: bool = False
) -> str:
    """
    Calculate the new wiki link target after the move.

    Args:
        link: Original wiki link
        old_path: Original path of file/folder
        new_path: New path of file/folder
        vault_root: Root of the Obsidian vault
        linking_file: File containing the link
        is_folder_move: True if moving a folder

    Returns:
        New link target (without [[ ]])
    """
    # Get relative paths from vault root
    new_rel = new_path.relative_to(vault_root)
    old_rel = old_path.relative_to(vault_root)

    if is_folder_move and '/' in link.target:
        # For folder moves with path-based links, replace the folder portion
        # e.g., [[old-folder/file]] becomes [[new-folder/file]]
        link_parts = link.target.split('/')
        old_folder_name = old_rel.name

        # Check if first part matches old folder name
        if link_parts[0] == old_folder_name:
            # Replace first part with new folder path
            link_parts[0] = str(new_rel).replace('\\', '/')
            new_target = '/'.join(link_parts)
        else:
            # Link uses full path - replace the old folder path
            old_path_str = str(old_rel).replace('\\', '/')
            new_path_str = str(new_rel).replace('\\', '/')
            new_target = link.target.replace(old_path_str, new_path_str)
    elif '/' in link.target:
        # File move with path - use full relative path
        new_target = str(new_rel).replace('\\', '/')
    else:
        # Use just the filename (works for both file and folder moves)
        new_target = new_path.name

    # Remove .md extension if original link didn't have it
    if not link.has_extension and new_target.endswith('.md'):
        new_target = new_target[:-3]

    return new_target


def update_links_in_file(
    file_path: Path,
    old_path: Path,
    new_path: Path,
    vault_root: Path,
    is_folder_move: bool = False,
    dry_run: bool = False
) -> Tuple[int, List[str]]:
    """
    Update wiki links in a single file.

    Returns:
        Tuple of (number of links updated, list of changes)
    """
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    links = parse_wiki_links(content)

    updates = 0
    changes = []

    for link in links:
        if should_update_link(link, old_path, vault_root, is_folder_move):
            new_target = calculate_new_link_target(link, old_path, new_path, vault_root, file_path, is_folder_move)

            # Reconstruct the link
            embed_prefix = '!' if link.is_embed else ''
            alias_suffix = f'|{link.alias}' if link.alias else ''
            new_link = f'{embed_prefix}[[{new_target}{alias_suffix}]]'

            # Replace in content
            content = content.replace(link.original, new_link)
            updates += 1
            changes.append(f"  {link.original} → {new_link}")

    if updates > 0 and not dry_run:
        file_path.write_text(content, encoding='utf-8')

    return updates, changes


def find_files_with_links(vault_root: Path, exclude_path: Optional[Path] = None) -> List[Path]:
    """
    Find all markdown files in the vault (excluding a specific path).
    """
    files = []
    for md_file in vault_root.rglob('*.md'):
        if exclude_path and md_file.is_relative_to(exclude_path):
            continue
        files.append(md_file)
    return files


def move_file(
    source: Path,
    destination: Path,
    vault_root: Path,
    dry_run: bool = False,
    verbose: bool = False
) -> dict:
    """
    Move a file and update all wiki links.

    Returns:
        Dictionary with move results
    """
    if not source.exists():
        raise FileNotFoundError(f"Source does not exist: {source}")

    is_folder = source.is_dir()

    # Resolve destination
    if destination.is_dir():
        # Moving into a directory
        dest_path = destination / source.name
    else:
        dest_path = destination

    # Ensure destination parent exists
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if dest_path.exists():
        raise FileExistsError(f"Destination already exists: {dest_path}")

    # Find all markdown files in vault (excluding source if it's a folder)
    exclude = source if is_folder else None
    all_files = find_files_with_links(vault_root, exclude)

    results = {
        'source': str(source),
        'destination': str(dest_path),
        'is_folder': is_folder,
        'dry_run': dry_run,
        'files_updated': 0,
        'total_links_updated': 0,
        'updates': []
    }

    # Update links in all files
    for file_path in all_files:
        updates, changes = update_links_in_file(
            file_path,
            source,
            dest_path,
            vault_root,
            is_folder_move=is_folder,
            dry_run=dry_run
        )

        if updates > 0:
            results['files_updated'] += 1
            results['total_links_updated'] += updates
            results['updates'].append({
                'file': str(file_path.relative_to(vault_root)),
                'links_updated': updates,
                'changes': changes if verbose else []
            })

    # Move the file/folder
    if not dry_run:
        if is_folder:
            shutil.move(str(source), str(dest_path))
        else:
            shutil.move(str(source), str(dest_path))

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Move files/folders in Obsidian vault while updating wiki links'
    )
    parser.add_argument('source', type=Path, help='Source file or folder to move')
    parser.add_argument('destination', type=Path, help='Destination path')
    parser.add_argument(
        '--vault-root',
        type=Path,
        help='Root directory of Obsidian vault (default: auto-detect from source)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without making changes'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed changes for each file'
    )

    args = parser.parse_args()

    # Resolve paths
    source = args.source.resolve()
    destination = args.destination.resolve()

    # Auto-detect vault root if not provided
    if args.vault_root:
        vault_root = args.vault_root.resolve()
    else:
        # Walk up from source to find .obsidian directory
        current = source if source.is_dir() else source.parent
        while current != current.parent:
            if (current / '.obsidian').exists():
                vault_root = current
                break
            current = current.parent
        else:
            # Fallback: use parent of source
            vault_root = source.parent if source.is_file() else source.parent.parent

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Moving in vault: {vault_root}")
    print(f"Source: {source.relative_to(vault_root)}")
    print(f"Destination: {destination.relative_to(vault_root) if destination.is_relative_to(vault_root) else destination}")
    print()

    # Perform the move
    try:
        results = move_file(source, destination, vault_root, args.dry_run, args.verbose)

        print(f"✓ {'Would move' if args.dry_run else 'Moved'}: {results['source']} → {results['destination']}")
        print(f"✓ Files with updated links: {results['files_updated']}")
        print(f"✓ Total links updated: {results['total_links_updated']}")

        if args.verbose and results['updates']:
            print("\nDetailed changes:")
            for update in results['updates']:
                print(f"\n{update['file']} ({update['links_updated']} links):")
                for change in update['changes']:
                    print(change)
        elif results['updates']:
            print("\nFiles updated:")
            for update in results['updates']:
                print(f"  - {update['file']} ({update['links_updated']} links)")

    except Exception as e:
        print(f"✗ Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
