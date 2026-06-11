#!/usr/bin/env python3
"""
Grade one eval run against its assertions.

Usage:
    python grade.py <output_file.md> <eval_id> [--config evals.json]

Writes grading.json to the same directory as output_file.
"""

import json
import re
import sys
from pathlib import Path


def load_evals(config_path: Path) -> dict:
    with open(config_path) as f:
        data = json.load(f)
    return {e["id"]: e for e in data["evals"]}


def parse_frontmatter(content: str) -> tuple[dict, str]:
    if not content.startswith("---"):
        return {}, content
    end = re.search(r"\n---\s*\n", content[3:])
    if not end:
        return {}, content
    fm_text = content[3:3 + end.start()]
    body = content[3 + end.end():]
    fm = {}
    for line in fm_text.split("\n"):
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            val = val.strip()
            if val.lower() == "true":
                fm[key.strip()] = True
            elif val.lower() == "false":
                fm[key.strip()] = False
            else:
                fm[key.strip()] = val
    return fm, body


def count_bold(body: str) -> int:
    """Count **bold** passages that are NOT inside ==**...**==."""
    # Remove highlight markers first to avoid double-counting
    stripped = re.sub(r"==\*\*.*?\*\*==", "", body, flags=re.DOTALL)
    return len(re.findall(r"\*\*[^*]+\*\*", stripped))


def count_highlight(body: str) -> int:
    return len(re.findall(r"==\*\*[^*]+\*\*==", body, re.DOTALL))


def bold_texts(body: str) -> list[str]:
    """Return list of all bolded text strings (including highlighted ones)."""
    results = re.findall(r"\*\*([^*]+)\*\*", body)
    return results


def check_assertion(assertion: dict, fm: dict, body: str, eval_id: int) -> dict:
    name = assertion["name"]
    passed = False
    evidence = ""

    if name == "frontmatter-highlighted-true":
        passed = fm.get("highlighted") is True
        evidence = f"highlighted = {fm.get('highlighted')}"

    elif name == "minimum-three-bold-passages":
        n = count_bold(body)
        passed = n >= 3
        evidence = f"found {n} bold passages"

    elif name == "minimum-five-bold-passages":
        n = count_bold(body)
        passed = n >= 5
        evidence = f"found {n} bold passages"

    elif name == "at-least-one-highlight":
        n = count_highlight(body)
        passed = n >= 1
        evidence = f"found {n} highlighted passages"

    elif name == "at-least-two-highlights":
        n = count_highlight(body)
        passed = n >= 2
        evidence = f"found {n} highlighted passages"

    elif name == "shame-withdrawal-claim-bolded":
        bolded = bold_texts(body)
        targets = [t for t in bolded if "shame" in t.lower() and any(
            w in t.lower() for w in ["withdrawal", "avoidance", "goal-inconsistent", "withdraws"]
        )]
        passed = len(targets) > 0
        evidence = f"{len(targets)} matching passage(s); first: {targets[0][:100] if targets else 'none'}"

    elif name == "specific-probability-or-effect-size-bolded":
        bolded = bold_texts(body)
        pattern = re.compile(r"(SMD|d\s*[=≈]|p\s*=|0\.\d{2}|\d+\.\d+\s*%)", re.IGNORECASE)
        targets = [t for t in bolded if pattern.search(t)]
        passed = len(targets) > 0
        evidence = f"{len(targets)} passage(s) with numeric evidence; first: {targets[0][:100] if targets else 'none'}"

    elif name == "environmental-vs-cognitive-claim-bolded":
        bolded = bold_texts(body)
        targets = [t for t in bolded if (
            ("environmental" in t.lower() or "substrate" in t.lower()) and
            ("cognitive" in t.lower() or "reframing" in t.lower() or "reappraisal" in t.lower())
        )]
        passed = len(targets) > 0
        evidence = f"{len(targets)} matching passage(s); first: {targets[0][:100] if targets else 'none'}"

    elif name == "smd-effect-size-bolded":
        bolded = bold_texts(body)
        pattern = re.compile(r"(SMD|effect size|d\s*[=≈]|-0\.\d+)", re.IGNORECASE)
        targets = [t for t in bolded if pattern.search(t)]
        passed = len(targets) > 0
        evidence = f"{len(targets)} passage(s) with SMD/effect size; first: {targets[0][:100] if targets else 'none'}"

    elif name == "implementation-intention-finding-bolded":
        bolded = bold_texts(body)
        pattern = re.compile(r"(implementation intention|if.then|d\s*[=≈]\s*0\.6)", re.IGNORECASE)
        targets = [t for t in bolded if pattern.search(t)]
        passed = len(targets) > 0
        evidence = f"{len(targets)} matching passage(s); first: {targets[0][:100] if targets else 'none'}"

    elif name == "sleep-finding-bolded":
        bolded = bold_texts(body)
        pattern = re.compile(r"(sleep loss|sleep deprivation|sleep.{0,30}SMD|SMD.{0,30}sleep)", re.IGNORECASE)
        targets = [t for t in bolded if pattern.search(t) or (
            "sleep" in t.lower() and ("SMD" in t or "positive affect" in t.lower() or "−0.9" in t or "-0.9" in t)
        )]
        passed = len(targets) > 0
        evidence = f"{len(targets)} sleep+effect passage(s); first: {targets[0][:100] if targets else 'none'}"

    elif name == "no-formatting-artifacts":
        has_quad_star = "****" in body
        has_quad_eq = "====" in body
        passed = not has_quad_star and not has_quad_eq
        if has_quad_star:
            evidence = "found **** artifacts"
        elif has_quad_eq:
            evidence = "found ==== artifacts"
        else:
            evidence = "no artifacts found"

    else:
        passed = False
        evidence = f"unknown assertion name: {name}"

    return {"text": assertion["name"], "passed": passed, "evidence": evidence}


def grade_file(output_path: Path, eval_id: int, config_path: Path) -> None:
    evals = load_evals(config_path)
    if eval_id not in evals:
        print(f"Eval ID {eval_id} not found in {config_path}", file=sys.stderr)
        sys.exit(1)

    eval_config = evals[eval_id]
    assertions = eval_config.get("assertions", [])

    content = output_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)

    results = [check_assertion(a, fm, body, eval_id) for a in assertions]

    passed = sum(1 for r in results if r["passed"])
    total = len(results)

    grading = {
        "eval_id": eval_id,
        "output_file": str(output_path),
        "pass_rate": passed / total if total > 0 else 0.0,
        "passed": passed,
        "total": total,
        "bold_count": count_bold(body),
        "highlight_count": count_highlight(body),
        "expectations": results,
    }

    out_path = output_path.parent / "grading.json"
    out_path.write_text(json.dumps(grading, indent=2), encoding="utf-8")
    print(f"Graded {output_path.name}: {passed}/{total} assertions passed ({grading['pass_rate']:.0%})")
    print(f"  Bold: {grading['bold_count']}, Highlighted: {grading['highlight_count']}")
    for r in results:
        status = "✓" if r["passed"] else "✗"
        print(f"  {status} {r['text']}: {r['evidence']}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: grade.py <output_file.md> <eval_id> [--config evals.json]", file=sys.stderr)
        sys.exit(1)

    output_file = Path(sys.argv[1])
    eval_id = int(sys.argv[2])

    config = Path(__file__).parent / "evals.json"
    if "--config" in sys.argv:
        idx = sys.argv.index("--config")
        config = Path(sys.argv[idx + 1])

    grade_file(output_file, eval_id, config)
