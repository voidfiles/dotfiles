#!/usr/bin/env python3
"""
Grade a finished process-action-notes run against the fixture's expected end
state. Reads the run's vault, checks each assertion programmatically, and writes
grading.json in the run dir (fields: text, passed, evidence — the viewer needs
exactly these).

Usage: grade.py <run_dir>   where <run_dir>/vault is the mutated vault.
"""

import json
import re
import sys
from pathlib import Path

WIKILINK = re.compile(r"(?<!\!)\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
EMBED = re.compile(r"!\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")


def md_files(vault: Path):
    return [p for p in vault.rglob("*.md")]


def find_by_basename(vault: Path, name: str):
    name = name.strip()
    if name.endswith(".md"):
        name = name[:-3]
    base = name.split("/")[-1]
    hits = []
    for p in md_files(vault):
        if p.stem == base:
            hits.append(p)
        # also allow path-style targets
    # path-style match
    for p in md_files(vault):
        rel = str(p.relative_to(vault))[:-3]
        if rel == name or rel.endswith("/" + name):
            hits.append(p)
    return hits


def notes_referencing(vault: Path, title: str):
    """Atomic notes that link back to a given source title and carry an
    #atomic/ tag (inline or frontmatter)."""
    out = []
    for p in md_files(vault):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        links = WIKILINK.findall(txt) + EMBED.findall(txt)
        link_bases = {l.strip().split("/")[-1].removesuffix(".md") for l in links}
        if title in link_bases and re.search(r"(?<![\w/])#?atomic/", txt):
            out.append(p)
    return out


def rel_paths(vault: Path):
    return {str(p.relative_to(vault)) for p in md_files(vault)}


def under(vault: Path, title: str, top: str):
    """Is there a file named <title> somewhere under <top>/ ?"""
    for p in md_files(vault):
        rel = str(p.relative_to(vault))
        if p.stem == title and rel.startswith(top + "/"):
            return rel
    return None


def in_inbox(vault: Path, title: str):
    for p in md_files(vault):
        rel = str(p.relative_to(vault))
        if p.stem == title and rel.startswith("inbox/"):
            return rel
    return None


def grade(run_dir: Path):
    vault = run_dir / "vault"
    results = []

    def add(text, passed, evidence):
        results.append({"text": text, "passed": bool(passed), "evidence": evidence})

    # 1 atomic notes for Blog Post Ideas
    blog_atomics = notes_referencing(vault, "Blog Post Ideas")
    add("At least one atomic note derived from 'Blog Post Ideas' exists under areas/ with #atomic/ tag and back-link.",
        any(str(p.relative_to(vault)).startswith("areas/") for p in blog_atomics),
        f"atomic notes linking Blog Post Ideas under areas/: {[str(p.relative_to(vault)) for p in blog_atomics if str(p.relative_to(vault)).startswith('areas/')]}")

    # 2 atomic notes for RSS
    rss_atomics = notes_referencing(vault, "Why support RSS")
    add("At least one atomic note derived from 'Why support RSS' exists under areas/.",
        any(str(p.relative_to(vault)).startswith("areas/") for p in rss_atomics),
        f"atomic notes linking Why support RSS under areas/: {[str(p.relative_to(vault)) for p in rss_atomics if str(p.relative_to(vault)).startswith('areas/')]}")

    # 3 no atomic for non-atomic sources
    bad = (notes_referencing(vault, "Markup is the new Cursive")
           + notes_referencing(vault, "Old Postgres Tuning Notes")
           + notes_referencing(vault, "The art of action"))
    add("No atomic notes generated from Markup / Old Postgres / The art of action.",
        len(bad) == 0,
        f"unexpected atomic notes: {[str(p.relative_to(vault)) for p in bad]}")

    # 4 blog moved to area
    add("'Blog Post Ideas.md' left inbox/ and now lives under areas/.",
        in_inbox(vault, "Blog Post Ideas") is None and under(vault, "Blog Post Ideas", "areas"),
        f"inbox={in_inbox(vault,'Blog Post Ideas')} areas={under(vault,'Blog Post Ideas','areas')}")

    # 5 rss moved to area
    add("'Why support RSS.md' left inbox/ into areas/.",
        in_inbox(vault, "Why support RSS") is None and under(vault, "Why support RSS", "areas"),
        f"inbox={in_inbox(vault,'Why support RSS')} areas={under(vault,'Why support RSS','areas')}")

    # 6 markup moved to area
    add("'Markup is the new Cursive.md' left inbox/ into areas/.",
        in_inbox(vault, "Markup is the new Cursive") is None and under(vault, "Markup is the new Cursive", "areas"),
        f"inbox={in_inbox(vault,'Markup is the new Cursive')} areas={under(vault,'Markup is the new Cursive','areas')}")

    # 7 postgres moved to resources
    add("'Old Postgres Tuning Notes.md' left inbox/ into resources/.",
        in_inbox(vault, "Old Postgres Tuning Notes") is None and under(vault, "Old Postgres Tuning Notes", "resources"),
        f"inbox={in_inbox(vault,'Old Postgres Tuning Notes')} resources={under(vault,'Old Postgres Tuning Notes','resources')}")

    # 8 bridge untouched
    bridge = in_inbox(vault, "The art of action")
    bridge_tagged = False
    if bridge:
        bridge_tagged = "action/bridge" in (vault / bridge).read_text(encoding="utf-8", errors="ignore")
    add("'The art of action.md' (unknown #action/bridge) still in inbox/ with its tag.",
        bool(bridge) and bridge_tagged,
        f"inbox={bridge} still_tagged={bridge_tagged}")

    # 9 sources de-tagged
    still_tagged = []
    for title in ["Blog Post Ideas", "Why support RSS", "Markup is the new Cursive", "Old Postgres Tuning Notes"]:
        for p in md_files(vault):
            if p.stem == title and re.search(r"(?<![\w/])#?action/(atomic-note|move-area|move-resources)", p.read_text(encoding="utf-8", errors="ignore")):
                still_tagged.append(str(p.relative_to(vault)))
    add("Processed/moved notes no longer carry any #action/ verb tag.",
        len(still_tagged) == 0,
        f"still tagged: {still_tagged}")

    # 10 no broken wiki links
    broken = []
    for p in md_files(vault):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        for target in set(WIKILINK.findall(txt) + EMBED.findall(txt)):
            if not find_by_basename(vault, target):
                broken.append(f"{p.relative_to(vault)} -> [[{target}]]")
    add("Every wiki link in the final vault resolves to an existing markdown file.",
        len(broken) == 0,
        f"broken links: {broken}" if broken else "all links resolve")

    passed = sum(r["passed"] for r in results)
    total = len(results)
    out = {"run_dir": str(run_dir), "expectations": results,
           "summary": {
               "pass_rate": round(passed / total, 4) if total else 0.0,
               "passed": passed, "failed": total - passed, "total": total,
           },
           "passed": passed, "total": total}
    (run_dir / "grading.json").write_text(json.dumps(out, indent=2))
    print(f"{run_dir.name}: {out['passed']}/{out['total']}")
    for r in results:
        mark = "PASS" if r["passed"] else "FAIL"
        print(f"  [{mark}] {r['text']}")
        if not r["passed"]:
            print(f"         {r['evidence']}")
    return out


def main():
    base = Path(sys.argv[1])
    runs = []
    for eval_dir in sorted(base.iterdir()):
        if not eval_dir.is_dir():
            continue
        for arm in ("with_skill", "without_skill", "old_skill"):
            rd = eval_dir / arm
            if (rd / "vault").is_dir():
                runs.append(rd)
    for rd in runs:
        grade(rd)
        print()


if __name__ == "__main__":
    main()
