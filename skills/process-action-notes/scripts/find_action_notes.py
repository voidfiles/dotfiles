#!/usr/bin/env python3
"""
Find notes in an Obsidian vault tagged with the #action/ namespace.

Why a script and not a grep: a naive `grep action/` is wrong. The substring
"action/" shows up mid-word in ordinary prose ("satisfaction/state checking",
"call to action/forcing-functions"), which produces a pile of false positives.
Obsidian tags are real tokens: an inline tag must start with `#` at a word
boundary, and a frontmatter tag lives inside the YAML `tags:` list. This script
parses both forms properly, whitelists the action verbs we actually handle, and
reports anything else under #action/ so unknown verbs get surfaced, not silently
acted on.

A single note can carry more than one action (e.g. both atomic-note and
move-area). That is the whole reason ordering matters downstream: atomic notes
must be written while the source still sits at its current path, then the move
runs and the wiki-link updater rewrites the fresh notes' back-links.

Output: JSON to stdout.
{
  "vault_root": "...",
  "notes": [
    {"path": "<abs>", "rel": "<vault-relative>", "title": "<basename no ext>",
     "actions": ["atomic-note", "move-area"]}
  ],
  "unknown": [
    {"path": "<abs>", "rel": "...", "verbs": ["bridge"]}
  ]
}
"""

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_VAULT = "/Users/alex/Dropbox/obsidian/Alex3"

# The action verbs this skill knows how to execute. Anything else under
# #action/ is reported as "unknown" so the user can decide, never auto-run.
KNOWN_ACTIONS = {"atomic-note", "move-area", "move-resources", "suggest-area"}

# Folders to skip: Obsidian internals, binary/asset dirs, and anything already
# archived (archived notes that mention action/ are done, not a worklist).
SKIP_DIR_PARTS = {
    ".obsidian", ".trash", "trash", "attachments", "assets",
    "Backup", "__pycache__", "archive", "archives",
}

# Inline tag: `#action/<verb>`, must be at a word boundary so we don't match
# "...action/..." buried inside a longer word. Obsidian tag chars: letters,
# digits, _, -, /.
INLINE_TAG = re.compile(r"(?<![\w/#])#action/([A-Za-z0-9_-]+)")

# A frontmatter tags entry naming the action namespace, e.g. `- action/move-area`
# or `tags: [action/atomic-note, foo]`. We only look at this inside frontmatter.
FM_ACTION = re.compile(r"(?<![\w/])action/([A-Za-z0-9_-]+)")


def split_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter_text, body_text). Frontmatter is a leading
    `---\\n ... \\n---` block; if absent, frontmatter is empty."""
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            fm_end = end + len("\n---")
            return text[4:end], text[fm_end:]
    return "", text


def frontmatter_action_verbs(fm: str) -> set[str]:
    """Extract action verbs from the frontmatter `tags:` region only, so we
    don't pick up an unrelated `action:` field or prose. We scan lines that are
    part of a tags block (the `tags:` line and the indented list items beneath
    it, or an inline `tags: [...]`)."""
    verbs: set[str] = set()
    lines = fm.splitlines()
    in_tags = False
    for line in lines:
        stripped = line.strip()
        if re.match(r"^tags\s*:", stripped):
            in_tags = True
            # inline form: tags: [a, b]  or  tags: action/foo
            verbs.update(FM_ACTION.findall(line))
            # if the value is non-empty inline, the block ends on this line
            after = stripped.split(":", 1)[1].strip()
            if after and not after.startswith("["):
                in_tags = False
            continue
        if in_tags:
            # list items are indented "- foo"; a non-indented, non-dash line
            # ends the tags block
            if stripped.startswith("- ") or (line and line[0] in " \t"):
                verbs.update(FM_ACTION.findall(line))
            else:
                in_tags = False
    return verbs


def scan_file(path: Path) -> tuple[set[str], set[str]]:
    """Return (known_verbs, unknown_verbs) found as real tags in the file."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return set(), set()
    fm, body = split_frontmatter(text)
    verbs = set(INLINE_TAG.findall(body)) | frontmatter_action_verbs(fm)
    known = verbs & KNOWN_ACTIONS
    unknown = verbs - KNOWN_ACTIONS
    return known, unknown


def should_skip(path: Path, vault_root: Path) -> bool:
    parts = set(path.relative_to(vault_root).parts)
    return bool(parts & SKIP_DIR_PARTS)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--vault-root", default=DEFAULT_VAULT)
    args = ap.parse_args()

    vault_root = Path(args.vault_root).expanduser().resolve()
    if not vault_root.is_dir():
        print(f"vault root not found: {vault_root}", file=sys.stderr)
        return 1

    notes = []
    unknown = []
    for path in sorted(vault_root.rglob("*.md")):
        if should_skip(path, vault_root):
            continue
        known, unk = scan_file(path)
        rel = str(path.relative_to(vault_root))
        if known:
            notes.append({
                "path": str(path),
                "rel": rel,
                "title": path.stem,
                "actions": sorted(known),
            })
        if unk:
            unknown.append({"path": str(path), "rel": rel, "verbs": sorted(unk)})

    json.dump(
        {"vault_root": str(vault_root), "notes": notes, "unknown": unknown},
        sys.stdout,
        indent=2,
    )
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
