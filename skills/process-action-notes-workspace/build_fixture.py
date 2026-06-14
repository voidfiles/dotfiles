#!/usr/bin/env python3
"""
Build a fresh synthetic Obsidian vault fixture for testing process-action-notes.

The skill mutates the vault (writes atomic notes, moves files, rewrites links),
so every test run needs its own throwaway copy. Call:

    uv run build_fixture.py /path/to/dest-vault

It wipes dest if it exists and writes a small but realistic PARA vault with:
- a .obsidian marker (so move-file detects the vault root)
- notes carrying #action/atomic-note, #action/move-area, #action/move-resources
- a multi-action note (atomic-note + move-area) — the link-ordering case
- an unknown verb (#action/bridge) plus prose containing "satisfaction/state"
  to confirm the finder ignores substrings and unknown verbs
- cross-links from other notes so wiki-link rewriting is observable
"""

import shutil
import sys
from pathlib import Path

FILES = {
    ".obsidian/app.json": "{}\n",

    "inbox/Blog Post Ideas.md": """---
tags:
  - action/atomic-note
  - action/move-area
---

# Blog Post Ideas

A running list of things worth writing about.

The strongest one: **writing in public compounds**. Every post is a cheap
option on a future conversation. You publish a half-formed idea, and months
later someone emails you the missing half. The cost is fixed and small; the
upside is unbounded and you only need a few to pay off. Most people never
publish because they price the embarrassment of being wrong higher than the
value of being found. That trade is almost always backwards.

Second idea: **a blog is a personal API**. Instead of re-explaining the same
opinion in every DM, you write it once and hand out the URL. The marginal cost
of the next explanation drops to zero. Your writing becomes a callable
interface to your own thinking.

Third: tools shape what we make. Worth its own piece someday.
""",

    "inbox/Why support RSS.md": """---
tags:
  - action/atomic-note
  - action/move-area
---

# Why support RSS

RSS is unfashionable and that is exactly why it is durable.

The core argument: **open syndication formats outlast the platforms that
ignore them**. Platforms optimize for engagement inside their walls, so they
starve any protocol that lets readers leave. But a format with no owner has no
incentive to die. RSS keeps working precisely because nobody can monetize
killing it.

There is a second point about **control of attention**. A feed reader puts the
reader in charge of the queue; an algorithmic timeline puts the platform in
charge. Supporting RSS is a small political act about who owns your attention.
""",

    "inbox/Markup is the new Cursive.md": """---
tags:
  - action/move-area
---

# Markup is the new Cursive

A short clipping I want to keep. Handwriting used to be a basic literacy;
now formatting plain text with markup is the equivalent baseline skill. Nothing
to atomize, just file it under writing somewhere.
""",

    "inbox/Old Postgres Tuning Notes.md": """---
tags:
  - action/move-resources
---

# Old Postgres Tuning Notes

Reference dump on connection pooling and vacuum settings. Not an active project,
not an area of responsibility — just something I'll look up later. Belongs in
resources.
""",

    "inbox/The art of action.md": """---
tags:
  - action/bridge
---

# The art of action

Notes on the book. There is a recurring theme of satisfaction/state checking in
how leaders close the gap between plans and results — the prose here contains
the literal substring "action/" mid-sentence, which a naive grep would wrongly
treat as a tag. This note's only real action tag is an unknown verb.
""",

    "areas/writing/writing-index.md": """# Writing Index

Stuff I'm working on around writing.

- [[Blog Post Ideas]] — the running list
- Some other thoughts
""",

    "daily/2026-06-01.md": """# 2026-06-01

Read [[Markup is the new Cursive]] this morning, good clipping.
""",

    "resources/.keep": "",
    "areas/.keep": "",
    "projects/.keep": "",
}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: build_fixture.py <dest-vault>", file=sys.stderr)
        return 1
    dest = Path(sys.argv[1]).expanduser().resolve()
    if dest.exists():
        shutil.rmtree(dest)
    for rel, content in FILES.items():
        p = dest / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    print(f"built fixture vault at {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
