---
name: note-area-suggester
description: Suggest where in your Obsidian vault a note belongs — existing folder or a new one to create. Scans the live PARA folder structure and recommends the best-fit locations with brief reasoning. Use whenever you're wondering "where does this go?", "what folder should I put this in?", "suggest a location for this note", "where should I file this?", "what area does this belong in?", or any variation of needing to know the right home for a note or idea in the vault. Also trigger when the user has just drafted content and asks where to save it.
argument-hint: [file-path or leave empty if content is in context]
---

# Note Area Suggester

Given a note or topic, scan the vault's live folder structure and suggest the right home for it. Existing folder if one fits well; new folder proposal if the vault is missing that category.

## Step 1: Get the content

- If `$ARGUMENTS` is a file path → read the file
- If `$ARGUMENTS` is empty → use content already in the conversation
- If it's a topic phrase or idea in words → work from that description directly (no file needed)

## Step 2: Scan the vault structure

```bash
find /Users/alex/Dropbox/obsidian/Alex3 -type d \
  -not -path '*/.obsidian*' \
  -not -path '*/.*' \
  -not -path '*/attachments*' \
  -not -path '*/assets*' \
  -not -path '*/trash*' \
  -not -path '*/Backup*' \
  -not -path '*/__pycache__*' \
  | sort
```

Read the full list. You're looking for folders across all four PARA buckets: `projects/`, `areas/`, `resources/`, `archive/`.

## Step 3: Determine the PARA bucket

Before picking a specific subfolder, commit to the right PARA category. This matters because it shapes how the content gets used later.

| Bucket | Use when... | Examples in this vault |
|--------|-------------|------------------------|
| `projects/` | Active work toward a specific outcome, has an implicit deadline | `allstate-nominations`, `account-status-domain-trailhead` |
| `areas/` | Ongoing domain of responsibility or sustained interest — no "done" state | `leadership`, `coaching`, `physical-training`, `writing` |
| `resources/` | Reference material on a topic you might draw on in the future | `agent-engineering`, `software-development`, `career` |
| `archive/` | Inactive, completed, or deprecated | — |

**The areas vs. resources heuristic**: areas are things you *are or do* (roles, ongoing practices), resources are things you *know about* (topics you consult). A note about your leadership practice → `areas/leadership`. A research summary on leadership theories → `resources/engineering-leadership`.

**Usage signals override form factor**: If the content includes phrases like "I use this daily", "core to how I work", "I do this regularly", or "I've been iterating on this", treat that as a strong push toward `areas/` even if the content looks like a reference collection. The deciding question is: is this an active practice or passive knowledge?

## Step 4: Match to existing folders

Look at the folders in the chosen bucket. Find the best semantic match — the folder whose theme most closely overlaps with the note's content. Consider:

- **Specificity**: A note about swimming technique should go in `areas/physical-training` or `resources/swimming`, not `resources/training` if a more specific folder exists
- **Depth**: Prefer the most specific existing folder that still feels right; don't go so deep you're forcing it
- **Don't stuff**: If the match is weak (you'd be putting it somewhere because it's closest, not because it fits), propose a new folder instead

## Step 5: Output the suggestions

Keep it short and decisive. Format:

---

**PARA bucket**: `areas/` *(or whichever applies, with one-sentence rationale)*

**Existing folders** (best matches, ranked):
1. `areas/leadership` — *ongoing leadership practice; use this if you actively work on this*
2. `resources/engineering-leadership` — *reference material on leading engineering teams; better fit if this is more "useful someday" than active practice*

**New folder** *(only if no existing folder fits well)*:
- `areas/team-dynamics` — *ongoing interest in how teams form and perform; doesn't fit any current folder cleanly*

**Note** *(optional, only if the choice is genuinely ambiguous)*:
> This sits between areas and resources. If you're actively working on this as a responsibility, file it under areas. If it's reference knowledge you might draw on, use resources.

---

Rules for the output:
- Max 3 existing folder suggestions. Usually 1-2 is better than 3.
- Max 2 new folder proposals. One is usually right.
- New folder names must follow the existing convention: `kebab-case`, no special characters.
- Skip the "Note" block if the choice is obvious.
- Use full relative vault paths (e.g. `areas/leadership`, not just `leadership`).
