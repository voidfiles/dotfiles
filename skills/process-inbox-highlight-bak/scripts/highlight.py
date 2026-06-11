#!/usr/bin/env python3
"""
Process Inbox - Highlight

Apply Layer 1-2 Progressive Summarization to inbox items:
- Layer 1: Bold 10-20% of key passages
- Layer 2: Highlight 10-20% of bolded essence

For meetings and daily notes, also extract action items and decisions.

Usage:
    python highlight.py [file_path_or_folder]
    python highlight.py Clippings/
    python highlight.py Clippings/Article.md
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import subprocess


@dataclass
class ProcessingResult:
    """Result from processing a file."""
    file_path: Path
    success: bool
    bolded_count: int = 0
    highlighted_count: int = 0
    action_items_count: int = 0
    decisions_count: int = 0
    message: str = ""
    error: Optional[str] = None


def get_vault_root() -> Path:
    """Get the vault root directory."""
    # From: /Users/alex/Dropbox/obsidian/Alex3/.claude/skills/process-inbox-highlight/scripts/highlight.py
    # To: /Users/alex/Dropbox/obsidian/Alex3
    script_file = Path(__file__)
    # Go up: scripts -> process-inbox-highlight -> skills -> .claude -> Alex3
    vault_root = script_file.parent.parent.parent.parent.parent
    return vault_root


def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """Extract frontmatter from markdown content.

    Returns:
        Tuple of (frontmatter_dict, content_without_frontmatter)
    """
    if not content.startswith('---'):
        return {}, content

    # Find the closing ---
    end_match = re.search(r'\n---\s*\n', content[3:])
    if not end_match:
        return {}, content

    fm_text = content[3:3 + end_match.start()]
    remaining_content = content[3 + end_match.end():]

    # Parse YAML-like frontmatter
    fm_dict = {}
    lines = fm_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        if ':' in line and not line.startswith(' '):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            # Parse values
            if value.lower() == 'true':
                fm_dict[key] = True
            elif value.lower() == 'false':
                fm_dict[key] = False
            elif value == '[]':
                fm_dict[key] = []
            elif value == 'null':
                fm_dict[key] = None
            elif value == '':
                # This is a key with list items on following lines
                list_items = []
                i += 1
                while i < len(lines) and lines[i].startswith('  - '):
                    item = lines[i].strip()
                    if item.startswith('- '):
                        list_items.append(item[2:])
                    i += 1
                i -= 1  # Back up one since the loop will increment
                fm_dict[key] = list_items
            else:
                fm_dict[key] = value
        i += 1

    return fm_dict, remaining_content


def build_frontmatter(fm_dict: Dict) -> str:
    """Build frontmatter string from dictionary.

    Preserves a sensible key order: known pipeline keys first, then
    remaining keys alphabetically.
    """
    KNOWN_KEY_ORDER = [
        'type', 'tags', 'highlighted', 'extracted', 'processed',
        'highlighted_date', 'extracted_date', 'processed_date',
    ]

    ordered_keys: List[str] = []
    for k in KNOWN_KEY_ORDER:
        if k in fm_dict:
            ordered_keys.append(k)
    for k in sorted(fm_dict.keys()):
        if k not in ordered_keys:
            ordered_keys.append(k)

    lines = ['---']
    for key in ordered_keys:
        value = fm_dict[key]
        if isinstance(value, bool):
            lines.append(f"{key}: {str(value).lower()}")
        elif isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            else:
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
        elif value is None:
            lines.append(f"{key}: null")
        else:
            lines.append(f"{key}: {value}")
    lines.append('---')
    return '\n'.join(lines)


def detect_content_type(file_path: Path) -> str:
    """Detect content type from file path."""
    path_str = str(file_path)
    if 'Clippings' in path_str:
        return 'article'
    elif 'daily' in path_str:
        return 'daily'
    elif 'Meetings' in path_str:
        return 'meeting'
    elif 'assets' in path_str:
        return 'asset'
    return 'unknown'


def call_claude_api(prompt: str) -> Optional[str]:
    """Call Claude API using the Anthropic SDK."""
    try:
        import anthropic
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    except ImportError:
        print("Error: anthropic package not found. Install with: pip install anthropic", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error calling Claude API: {e}", file=sys.stderr)
        return None


def extract_json_from_response(response: str) -> Optional[Dict]:
    """Extract JSON from Claude response."""
    if not response:
        return None

    # Try to find JSON object in response
    json_match = re.search(r'\{[\s\S]*\}', response)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Try to find JSON array in response
    json_match = re.search(r'\[[\s\S]*\]', response)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    return None


CONTENT_TYPE_GUIDANCE = {
    'article': 'Focus on: novel claims, evidence-backed arguments, actionable frameworks, surprising data points.',
    'meeting': 'Focus on: decisions made, commitments given, open questions, strategic directions, ownership assignments.',
    'daily': 'Focus on: patterns noticed, reflections, commitments to self, mood/energy shifts, recurring themes.',
    'asset': 'Focus on: core thesis, key frameworks, memorable examples, actionable takeaways, definitions of new concepts.',
}


def identify_key_passages(content: str, content_type: str) -> List[str]:
    """Use Claude to identify key passages for bolding (Layer 1)."""
    if not content or len(content.strip()) == 0:
        return []

    type_hint = CONTENT_TYPE_GUIDANCE.get(content_type, '')

    prompt = f"""You are helping with progressive summarization (Layer 1).

Read this content and identify the 10-20% most important passages that represent key insights, core arguments, surprising ideas, or practical takeaways.

Content Type: {content_type}
{f"Content-type guidance: {type_hint}" if type_hint else ""}

Content:
{content}

Return ONLY a JSON array of passages to bold:
{{
  "passages": [
    "exact text passage 1",
    "exact text passage 2",
    ...
  ]
}}

Guidelines:
- Select passages that someone would want to remember in 5 years
- Prioritize: core arguments > evidence > examples
- Each passage should be at least 1-3 sentences, but can be longer if needed
- Multiple paragraphs are okay if they form a coherent thought
- Total bolded content should be ~10-20% of the content
- Return EXACT text matches (for reliable replacement)
- Do NOT include any text that is already bold (**text**) or highlighted (==text==)"""

    response = call_claude_api(prompt)
    if not response:
        return []

    result = extract_json_from_response(response)
    if result and 'passages' in result:
        return result['passages']

    return []


def identify_essence_passages(bolded_passages: List[str]) -> List[str]:
    """Use Claude to identify essence from bolded passages (Layer 2)."""
    if not bolded_passages:
        return []

    passages_str = '\n'.join([f"- {p}" for p in bolded_passages])

    prompt = f"""You are helping with progressive summarization (Layer 2 - essence).

From these bolded key passages, identify the 10-20% that represent the absolute core essence - the most important insights you'd want to remember.

Bolded Passages:
{passages_str}

Return ONLY a JSON array of essence passages to highlight:
{{
  "essence": [
    "exact bolded passage 1",
    "exact bolded passage 2",
    ...
  ]
}}

Guidelines:
- These are the insights that matter most
- If you could only remember 2-3 things from this content, what would they be?
- Total highlighted should be ~10-20% of bolded content
- Return EXACT text matches from the bolded passages"""

    response = call_claude_api(prompt)
    if not response:
        return []

    result = extract_json_from_response(response)
    if result and 'essence' in result:
        return result['essence']

    return []


def extract_action_items(content: str, content_type: str) -> Tuple[List[str], List[str], List[str]]:
    """Extract action items, decisions, and questions for meetings/daily."""
    # Only process meetings and daily notes
    if content_type not in ('meeting', 'daily'):
        return [], [], []

    if not content or len(content.strip()) == 0:
        return [], [], []

    prompt = f"""Extract action items, decisions, and open questions from this content:

Content:
{content}

Return JSON:
{{
  "action_items": [
    "Task 1 description",
    "Task 2 description"
  ],
  "decisions": [
    "Decision 1 with context",
    "Decision 2 with context"
  ],
  "open_questions": [
    "Question 1",
    "Question 2"
  ]
}}

Guidelines:
- Be specific and actionable
- Include owners if mentioned (e.g., "Task - Owner: Person Name")
- Preserve important context
- Return empty arrays if none found"""

    response = call_claude_api(prompt)
    if not response:
        return [], [], []

    result = extract_json_from_response(response)
    if result:
        action_items = result.get('action_items', [])
        decisions = result.get('decisions', [])
        questions = result.get('open_questions', [])
        return action_items, decisions, questions

    return [], [], []


def apply_formatting(content: str, bold_passages: List[str], essence_passages: List[str]) -> Tuple[str, int, int]:
    """Apply bold and highlight formatting to content.

    Returns:
        Tuple of (modified_content, bold_count, highlight_count)
    """
    modified = content
    bold_count = 0
    highlight_count = 0

    # Apply bolding first
    for passage in bold_passages:
        # Skip if already bolded or highlighted
        if f"**{passage}**" in modified or f"=={passage}==" in modified or f"==**{passage}**==" in modified:
            continue

        # Try to find exact match and bold it
        if passage in modified:
            modified = modified.replace(passage, f"**{passage}**", 1)
            bold_count += 1

    # Apply highlighting to bolded passages
    for passage in essence_passages:
        bolded = f"**{passage}**"
        if bolded in modified:
            modified = modified.replace(bolded, f"==**{passage}**==", 1)
            highlight_count += 1

    return modified, bold_count, highlight_count


def process_file(file_path: Path, vault_root: Path, force: bool = False) -> ProcessingResult:
    """Process a single file."""
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse frontmatter
        fm_dict, content_body = parse_frontmatter(content)

        # Check if already highlighted
        if fm_dict.get('highlighted') and not force:
            return ProcessingResult(
                file_path=file_path,
                success=True,
                message=f"Skipping {file_path.name} - already highlighted"
            )

        # Detect content type
        content_type = fm_dict.get('type') or detect_content_type(file_path)

        # For assets, process summary.md
        if content_type == 'asset':
            summary_path = file_path.parent / 'summary.md'
            if summary_path.exists():
                file_path = summary_path
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                fm_dict, content_body = parse_frontmatter(content)
            else:
                return ProcessingResult(
                    file_path=file_path,
                    success=False,
                    error=f"Asset folder has no summary.md"
                )

        # Identify key passages (Layer 1)
        bold_passages = identify_key_passages(content_body, content_type)

        # Identify essence (Layer 2)
        essence_passages = identify_essence_passages(bold_passages)

        # Apply formatting
        modified_content, bold_count, highlight_count = apply_formatting(
            content_body, bold_passages, essence_passages
        )

        # Extract action items and decisions (for meetings/daily)
        action_items, decisions, questions = extract_action_items(content_body, content_type)
        action_item_count = len(action_items)
        decision_count = len(decisions)

        # Update frontmatter
        fm_dict['type'] = content_type
        fm_dict['highlighted'] = True
        fm_dict['highlighted_date'] = datetime.now().strftime('%Y-%m-%d')
        if 'extracted' not in fm_dict:
            fm_dict['extracted'] = False
        if 'processed' not in fm_dict:
            fm_dict['processed'] = False

        # Add action items and decisions to frontmatter if present
        if action_items:
            fm_dict['action_items'] = action_items
        if decisions:
            fm_dict['decisions'] = decisions

        # Build new content
        new_frontmatter = build_frontmatter(fm_dict)

        # If there are action items, add summary section
        if action_items or decisions or questions:
            summary_section = "\n## Summary\n"
            if action_items:
                summary_section += "\n### Action Items\n"
                for item in action_items:
                    summary_section += f"- [ ] {item}\n"
            if decisions:
                summary_section += "\n### Decisions\n"
                for i, decision in enumerate(decisions, 1):
                    summary_section += f"{i}. {decision}\n"
            if questions:
                summary_section += "\n### Open Questions\n"
                for question in questions:
                    summary_section += f"- {question}\n"
            summary_section += "\n---\n"

            modified_content = summary_section + modified_content

        new_content = f"{new_frontmatter}\n{modified_content}"

        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return ProcessingResult(
            file_path=file_path,
            success=True,
            bolded_count=bold_count,
            highlighted_count=highlight_count,
            action_items_count=action_item_count,
            decisions_count=decision_count,
            message=f"Processed {file_path.name}: {bold_count} passages bolded, {highlight_count} highlighted"
        )

    except Exception as e:
        return ProcessingResult(
            file_path=file_path,
            success=False,
            error=str(e)
        )


def find_files(path_arg: str, vault_root: Path) -> List[Path]:
    """Find files to process."""
    path = Path(path_arg)

    # Make path absolute if relative
    if not path.is_absolute():
        path = vault_root / path

    files = []

    if path.is_file() and path.exists():
        # Single file
        if path.suffix == '.md':
            files.append(path)
    elif path.is_dir() and path.exists():
        # Directory - find all md files recursively
        files = sorted(path.glob('**/*.md'))
    elif not path.exists():
        # Try without strict checking
        path = vault_root / path_arg if not Path(path_arg).is_absolute() else Path(path_arg)
        if path.is_dir():
            files = sorted(path.glob('**/*.md'))
        elif path.is_file():
            if path.suffix == '.md':
                files.append(path)

    return files


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Apply progressive summarization to inbox items'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='Clippings/',
        help='File path or folder to process (default: Clippings/)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Re-highlight already highlighted files'
    )
    parser.add_argument(
        '--vault-root',
        type=Path,
        help='Vault root directory'
    )

    args = parser.parse_args()

    vault_root = args.vault_root or get_vault_root()

    # Find files
    files = find_files(args.path, vault_root)

    if not files:
        # Debug output
        path = Path(args.path)
        if not path.is_absolute():
            path = vault_root / path
        print(f"No markdown files found in {args.path}", file=sys.stderr)
        print(f"  Looked in: {path}", file=sys.stderr)
        print(f"  Path exists: {path.exists()}", file=sys.stderr)
        return 1

    print(f"Found {len(files)} file(s) to process")

    # Process files
    results = []
    for file_path in files:
        print(f"Processing: {file_path.name}...", end=' ', flush=True)
        result = process_file(file_path, vault_root, args.force)
        results.append(result)

        if result.success:
            if result.message:
                print(result.message)
            else:
                print("✓")
        else:
            print(f"✗ {result.error}")

    # Summary
    print(f"\n{len([r for r in results if r.success])} files processed successfully")

    success_count = sum(1 for r in results if r.success and r.bolded_count > 0)
    total_bolded = sum(r.bolded_count for r in results)
    total_highlighted = sum(r.highlighted_count for r in results)
    total_actions = sum(r.action_items_count for r in results)
    total_decisions = sum(r.decisions_count for r in results)

    if success_count > 0:
        print(f"  {total_bolded} passages bolded")
        print(f"  {total_highlighted} passages highlighted")
        if total_actions > 0 or total_decisions > 0:
            print(f"  {total_actions} action items extracted")
            print(f"  {total_decisions} decisions extracted")

    return 0 if all(r.success for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
