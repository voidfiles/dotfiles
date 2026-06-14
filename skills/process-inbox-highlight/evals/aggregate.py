#!/usr/bin/env python3
"""
Aggregate grading.json files from an iteration into a benchmark summary.

Usage:
    python aggregate.py <iteration-dir>

Prints a markdown table comparing with_skill vs without_skill (baseline) pass rates.
"""

import json
import sys
from pathlib import Path


def load_grading(path: Path) -> dict | None:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: aggregate.py <iteration-dir>", file=sys.stderr)
        sys.exit(1)

    iteration_dir = Path(sys.argv[1])
    if not iteration_dir.is_dir():
        print(f"Not a directory: {iteration_dir}", file=sys.stderr)
        sys.exit(1)

    rows = []
    for eval_dir in sorted(iteration_dir.iterdir()):
        if not eval_dir.is_dir():
            continue
        ws = load_grading(eval_dir / "with_skill" / "outputs" / "grading.json")
        bl = load_grading(eval_dir / "without_skill" / "outputs" / "grading.json")
        rows.append({
            "eval": eval_dir.name,
            "with_skill": ws,
            "baseline": bl,
        })

    if not rows:
        print("No grading.json files found.")
        return

    print(f"\n{'='*70}")
    print("BENCHMARK SUMMARY")
    print(f"{'='*70}\n")
    print(f"{'Eval':<45} {'v2':>8} {'baseline':>10} {'delta':>8}")
    print("-" * 73)

    total_ws_pass = total_ws_total = 0
    total_bl_pass = total_bl_total = 0

    for row in rows:
        ws, bl = row["with_skill"], row["baseline"]
        ws_str = f"{ws['passed']}/{ws['total']} ({ws['pass_rate']:.0%})" if ws else "N/A"
        bl_str = f"{bl['passed']}/{bl['total']} ({bl['pass_rate']:.0%})" if bl else "N/A"

        if ws and bl:
            delta = ws["pass_rate"] - bl["pass_rate"]
            delta_str = f"{delta:+.0%}"
        else:
            delta_str = "—"

        print(f"{row['eval']:<45} {ws_str:>8} {bl_str:>10} {delta_str:>8}")

        if ws:
            total_ws_pass += ws["passed"]
            total_ws_total += ws["total"]
        if bl:
            total_bl_pass += bl["passed"]
            total_bl_total += bl["total"]

    print("-" * 73)
    ws_overall = total_ws_pass / total_ws_total if total_ws_total else 0
    bl_overall = total_bl_pass / total_bl_total if total_bl_total else 0
    print(f"{'OVERALL':<45} {f'{total_ws_pass}/{total_ws_total} ({ws_overall:.0%})':>8} "
          f"{f'{total_bl_pass}/{total_bl_total} ({bl_overall:.0%})':>10} "
          f"{f'{ws_overall - bl_overall:+.0%}':>8}")

    print("\nPer-eval details:")
    for row in rows:
        ws = row["with_skill"]
        if not ws:
            continue
        print(f"\n  {row['eval']} (v2: {ws['bold_count']} bold, {ws['highlight_count']} highlighted)")
        for exp in ws.get("expectations", []):
            status = "✓" if exp["passed"] else "✗"
            print(f"    {status} {exp['text']}: {exp['evidence']}")


if __name__ == "__main__":
    main()
