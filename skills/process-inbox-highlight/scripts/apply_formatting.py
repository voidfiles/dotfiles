#!/usr/bin/env python3
"""
Apply bold and highlight formatting to a markdown file.

Reads a JSON list of passages from stdin (or --passages file),
applies Layer 1 bold and Layer 2 highlight formatting, updates frontmatter.

Usage:
    python3 apply_formatting.py <file.md> --layer1 p1 p2 ... --layer2 p1 ...
    python3 apply_formatting.py <file.md> --passages passages.json

passages.json format:
    {
      "layer1": ["exact passage text...", ...],
      "layer2": ["exact passage text...", ...]
    }
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    if not content.startswith("---"):
        return {}, content
    end = re.search(r"\n---\s*\n", content[3:])
    if not end:
        return {}, content
    fm_text = content[3:3 + end.start()]
    body = content[3 + end.end():]
    fm: Dict = {}
    for line in fm_text.split("\n"):
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            val = val.strip()
            fm[key.strip()] = True if val.lower() == "true" else (
                False if val.lower() == "false" else (
                    None if val == "null" else val
                )
            )
    return fm, body


def build_frontmatter(fm: Dict) -> str:
    KEY_ORDER = ["type", "tags", "highlighted", "extracted", "processed",
                 "highlighted_date", "extracted_date", "processed_date"]
    ordered = [k for k in KEY_ORDER if k in fm]
    ordered += sorted(k for k in fm if k not in ordered)
    lines = ["---"]
    for k in ordered:
        v = fm[k]
        if isinstance(v, bool):
            lines.append(f"{k}: {str(v).lower()}")
        elif v is None:
            lines.append(f"{k}: null")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


def find_passage_in_body(passage: str, body: str) -> Tuple[int, int]:
    """
    Find passage in body, tolerating minor whitespace differences.
    Returns (start, end) or (-1, -1) if not found.
    """
    # 1. Exact match
    idx = body.find(passage)
    if idx >= 0:
        return idx, idx + len(passage)

    # 2. Whitespace-normalised match
    def norm(s: str) -> str:
        return re.sub(r"\s+", " ", s).strip()

    norm_passage = norm(passage)
    # Slide a normalised window over body
    words_p = norm_passage.split()
    if not words_p:
        return -1, -1

    # Use regex with flexible whitespace
    escaped_words = [re.escape(w) for w in words_p]
    pattern = r"\s+".join(escaped_words)
    m = re.search(pattern, body)
    if m:
        return m.start(), m.end()

    # 3. Markdown-stripped match
    _strip = re.compile(r"\*\*|==|\*|_|`")
    clean_p = norm(_strip.sub("", passage))
    clean_words = [re.escape(w) for w in clean_p.split() if w]
    if clean_words:
        pattern2 = r"\s+".join(clean_words)
        m2 = re.search(pattern2, _strip.sub("", body))
        if m2:
            # Map stripped position back to original — approximate
            stripped_body = _strip.sub("", body)
            # Find original position by counting non-stripped chars
            orig_idx = 0
            stripped_idx = 0
            target_start = m2.start()
            for orig_char, stripped_char in zip(body, stripped_body):
                if stripped_idx == target_start:
                    break
                orig_idx += 1
                stripped_idx += 1
            # Extend to find end
            orig_end = orig_idx + (m2.end() - m2.start())
            return orig_idx, min(orig_end, len(body))

    return -1, -1


def apply_formatting(
    body: str,
    layer1_passages: List[str],
    layer2_passages: List[str],
) -> Tuple[str, int, int]:
    """
    Apply bold (Layer 1) then highlight (Layer 2).
    Returns (modified_body, bold_count, highlight_count).
    """
    modified = body
    bold_count = 0
    highlight_count = 0
    actually_bolded: List[str] = []

    # Sort longest first to avoid subset conflicts
    for passage in sorted(layer1_passages, key=len, reverse=True):
        # Skip if already formatted
        if f"**{passage}**" in modified or f"==**{passage}**==" in modified:
            actually_bolded.append(passage)  # count as bolded (pre-existing)
            continue

        start, end = find_passage_in_body(passage, modified)
        if start >= 0:
            matched_text = modified[start:end]
            modified = modified[:start] + f"**{matched_text}**" + modified[end:]
            bold_count += 1
            actually_bolded.append(passage)

    # Apply highlights only to passages we actually bolded (or found pre-bolded)
    for passage in layer2_passages:
        # Look for the bolded form in modified
        bolded = f"**{passage}**"
        if bolded in modified:
            modified = modified.replace(bolded, f"==**{passage}**==", 1)
            highlight_count += 1
        else:
            # Try whitespace-flexible search for the bolded version
            start, end = find_passage_in_body(f"**{passage}**", modified)
            if start >= 0:
                matched = modified[start:end]
                modified = modified[:start] + f"=={matched}==" + modified[end:]
                highlight_count += 1

    return modified, bold_count, highlight_count


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply bold/highlight formatting to markdown")
    parser.add_argument("file", help="Markdown file to format")
    parser.add_argument("--passages", help="JSON file with {layer1: [...], layer2: [...]}")
    parser.add_argument("--layer1", nargs="*", default=[], help="Layer 1 passages (bold)")
    parser.add_argument("--layer2", nargs="*", default=[], help="Layer 2 passages (highlight)")
    parser.add_argument("--content-type", default=None, help="Content type for frontmatter")
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: {file_path} not found", file=sys.stderr)
        return 1

    layer1 = args.layer1 or []
    layer2 = args.layer2 or []

    if args.passages:
        with open(args.passages) as f:
            data = json.load(f)
        layer1 = data.get("layer1", layer1)
        layer2 = data.get("layer2", layer2)

    content = file_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)

    modified_body, bold_count, highlight_count = apply_formatting(body, layer1, layer2)

    fm["highlighted"] = True
    fm["highlighted_date"] = datetime.now().strftime("%Y-%m-%d")
    if "extracted" not in fm:
        fm["extracted"] = False
    if "processed" not in fm:
        fm["processed"] = False
    if args.content_type and "type" not in fm:
        fm["type"] = args.content_type

    new_content = f"{build_frontmatter(fm)}\n{modified_body}"
    file_path.write_text(new_content, encoding="utf-8")

    print(json.dumps({
        "file": str(file_path),
        "bold_count": bold_count,
        "highlight_count": highlight_count,
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
