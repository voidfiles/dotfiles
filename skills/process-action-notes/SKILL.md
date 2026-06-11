---
name: process-action-notes
description: Sweep an Obsidian vault for notes tagged in the #action/ namespace and run the action each one declares — #action/atomic-note (extract atomic notes into an area), #action/move-area (move into areas/), #action/move-resources (move into resources/), #action/suggest-area (suggest a best-fit area and explain why, without moving). Use whenever the user says "process my action notes", "run my #action tags", "do my action-tagged notes", "sweep the action notes", "clear my #action queue", "process #action/atomic-note and move-area", or any variation of batch-processing the action tags they've left around the vault. This is the batch orchestrator — prefer it over calling atomic-note-suggestor, note-area-suggester, or move-file one note at a time when there are several tagged notes to clear. Always create atomic notes before moving any file so wiki links resolve correctly.
argument-hint: [optional vault-root override]
---

# Process Action Notes

You leave `#action/...` tags on notes as a to-do queue: "this one should be atomized," "this one belongs in an area," "this one is reference, move it to resources." This skill clears that queue. It finds every tagged note, walks them with you one at a time, generates any atomic notes, and then moves files — in that order, on purpose.

## The one rule that shapes everything: atomics before moves

A note can carry more than one action. `Blog Post Ideas.md` might be both `#action/atomic-note` and `#action/move-area`: extract its ideas as atomic notes, then file the source under an area.

The atomic notes you write link back to their source with `[[source]]`. If you move the source *first* and write the atomic notes *after*, those links point at a path that no longer exists. So the order is non-negotiable:

1. **Create all atomic notes first**, while every source still sits at its current path.
2. **Then run every move.** `move-file` rescans the whole vault and rewrites wiki links — including the back-links in the atomic notes you just wrote — to the new locations.

That is why this skill writes atomic notes immediately as you confirm each note, but *queues* moves and runs them in a single final phase. Don't move a file the moment you confirm it; let the moves batch.

## Action verbs

| Tag | What it does | Destination bucket |
|-----|--------------|--------------------|
| `#action/atomic-note` | Extract atomic notes from the source. Source note stays put. | atomic notes go into `areas/` |
| `#action/move-area` | Move the source note into an ongoing area of responsibility. | `areas/` |
| `#action/move-resources` | Move the source note into reference material. | `resources/` |
| `#action/suggest-area` | Suggest the best-fit area for the source and explain why. Does **not** move anything. | advisory only (suggestion lands in the report) |

Atomic notes always land in an **area** — they're knowledge you actively work with, not passive reference.

## Step 1: Sweep the vault

Run the finder. It parses real Obsidian tags (inline `#action/verb` at a word boundary, plus genuine frontmatter `tags:` entries), whitelists the three verbs above, skips archives, and reports any unknown verbs separately. Do not hand-roll a `grep action/` — the substring shows up inside ordinary prose ("satisf**action/state**") and you'll act on garbage.

```bash
uv run --no-project skills/process-action-notes/scripts/find_action_notes.py
```

Add `--vault-root PATH` if `$ARGUMENTS` overrides the default vault.

The JSON gives you `notes` (each with `path`, `rel`, `title`, `actions[]`) and `unknown` (notes with `#action/` verbs this skill doesn't handle, e.g. `bridge`). Show the user a compact summary of the worklist before doing anything:

- How many notes, broken down by action.
- The unknown ones, listed plainly: "These have `#action/` tags I don't handle (`bridge`); I'll leave them alone. Want to deal with them separately?"

If `notes` is empty, say so and stop. Nothing to do is a fine outcome.

## Step 2: Scan the folder structure once

Both the atomic-note destination and the move destinations need to match against the live PARA folders. Scan once, reuse for every note — don't re-run this per note. Use the same vault root the finder reported (`vault_root` in its JSON), not a hardcoded path, so this works against an override too.

```bash
find "<vault_root>" -type d \
  -not -path '*/.obsidian*' -not -path '*/.*' \
  -not -path '*/attachments*' -not -path '*/assets*' \
  -not -path '*/trash*' -not -path '*/Backup*' \
  -not -path '*/__pycache__*' | sort
```

Keep the `areas/` and `resources/` subtrees handy. You'll match against them following the `note-area-suggester` logic: pick the best-fit existing folder, or propose a new one only when nothing fits.

## Step 3: Walk each note, one at a time

Process notes in worklist order. For each note, read the source, then handle its actions. Confirm before committing anything for that note.

Within a single note, the local order mirrors the global rule: **atomic generation first, then de-tag, then queue the move.**

### If the note has `#action/atomic-note`

1. Read the source fully.
2. Follow the **atomic-note-suggestor** process to draft atomic notes: one focused idea each, concept-oriented title, self-contained body, `#atomic/{idea}` tag plus domain tags, and a `*From: [[source-title]]*` back-link. Aim for the 3–7 range; quality over quantity. (See `skills/atomic-note-suggestor/SKILL.md` for the full bar on what earns a note.)
3. **Link each new note to related atomic notes.** Run atomic-note-suggestor's Step 4 (Link each note to related atomic notes): use the Obsidian CLI (`obsidian search query="tag:#atomic/<domain>"`, `obsidian search:context query="<concept>"`) to find genuine neighbors already in the vault, confirm fit, and add a `## Related` block with `[[Title]] — one-line reason`. Forward links only; skip the block when nothing genuinely relates.
4. Pick the destination **area** for these notes following **note-area-suggester**, constrained to the `areas/` bucket. Usually one area fits the whole set; split only if the ideas genuinely belong to different areas.
5. Show the user: the source, the atomic-note titles you'll create (with their `## Related` links), and the target area. This is the confirm point.
6. On confirm, **write the atomic note files now** with Zettelkasten naming `YYYYMMDDHHMM [Title].md` (get the real datetime; stagger the minute so filenames don't collide) into the chosen area. Each file links `[[source-title]]` so context is recoverable, and carries its `## Related` block.

The source note itself stays where it is for the atomic action. (If it *also* has a move action, that's handled below — and because the atomic notes already exist, the upcoming move will fix their back-links.)

### If the note has `#action/move-area` or `#action/move-resources`

1. Pick the destination following **note-area-suggester**, constrained to `areas/` (for move-area) or `resources/` (for move-resources). Prefer the most specific existing folder that genuinely fits; propose a new folder only when nothing does.
2. **Suggest atomic-note links, if it makes sense.** A note landing in an area usually has neighbors there. Run atomic-note-suggestor's Step 4 discovery against the destination's subject (`obsidian search query="tag:#atomic/<domain>"`, `obsidian search:context query="<concept>"`), confirm genuine fit, and propose a `## Related` block of `[[Title]] — one-line reason` forward links for the note being filed. This is a suggestion, not a requirement: if the note has no real atomic neighbors, skip it silently. Don't link a note that isn't itself about ideas (a raw clipping, a logistics doc) just to have links.
3. Show the user: the source path, the proposed destination with one line of reasoning, and any `## Related` links you'd add. This is the confirm point. If they redirect the destination or drop a link, use their choice.
4. On confirm, **add the suggested `## Related` block to the source in place** (so it travels with the file), then **add the move to a queue** — `(source_abs, destination_abs)`. Do not run the move yet.

### If the note has `#action/suggest-area`

This verb is advisory: it tells you where the note *would* belong without touching the file. Use it when you've left a note that you want a recommendation on but aren't ready to commit to a move.

1. Read the source.
2. Follow **note-area-suggester**, constrained to the `areas/` bucket, to pick the best-fit area. Surface the top 1–2 candidates ranked, each with **one line of reasoning** — what in the note's content maps to that area. The explanation is the whole point of this verb; never hand back a bare folder name.
3. **Surface related atomic notes, if any.** Run atomic-note-suggestor's Step 4 discovery (`obsidian search query="tag:#atomic/<domain>"`, `obsidian search:context query="<concept>"`) to name the existing atomic notes this one would connect to. These strengthen the area recommendation ("belongs in `areas/writing` near `[[...]]`, `[[...]]`") and become the `## Related` block if the user promotes to a move. Skip if nothing genuinely relates.
4. Show the user: the source, the suggested area(s) with reasoning, and the related atomic notes you found. This is the confirm point, and it offers two paths:
   - **Promote to a move** — the user likes the suggestion and wants it filed now. Treat it exactly like `#action/move-area`, including adding the `## Related` block before queuing: queue `(source_abs, destination_abs)` for the chosen area. (They can pick a candidate other than your top one, or redirect entirely.)
   - **Keep advisory only** — record the suggestion in the run report and leave the file where it is.
5. Either way, de-tag (see below) so the queue clears and a future run doesn't re-suggest. The suggestion itself survives in the Step 5 report.

`suggest-area` never adds anything to the move queue on its own — only the explicit "promote to a move" path does. A note that stays advisory makes no filesystem change beyond de-tagging.

### De-tag the note

Once you've handled a note's actions (atomic notes written, move queued, and/or area suggested), remove its `#action/...` tags from the source content so a future run doesn't reprocess it. Use Edit to strip the inline `#action/verb` token (and the frontmatter `tags:` entry if it lives there). Do this in place before the file moves, so the file arrives at its destination already clean.

Leave the atomic-note's own `#atomic/...` tags alone — those are real, keep them.

## Step 4: Run the queued moves

After every note is walked and all atomic notes are written, drain the move queue. For each queued move:

```bash
uv run skills/move-file/scripts/move_file.py "<source_abs>" "<destination_abs>"
```

Run each move; `move-file` updates every wiki link in the vault that pointed at the source, including the back-links in the atomic notes from this run. If a destination folder doesn't exist yet, `move-file` creates the path. If a destination filename already exists, it errors — pick a different name with the user rather than clobbering.

Do a dry run first (`--dry-run --verbose`) only if the user wants to preview, or if a move looks risky (e.g. a common title that might collide).

## Step 5: Report

Summarize what happened, with paths:

- Atomic notes created: count and where (link each).
- Files moved: `source → destination`, plus the link-update counts `move-file` reported.
- Area suggestions: for each `suggest-area` note left advisory, the suggested area and the one-line reasoning, so the recommendation isn't lost when the tag is gone.
- `## Related` links added: which notes got atomic-note links, and to what. Call out where you deliberately added none because nothing fit.
- Notes de-tagged.
- Unknown `#action/` notes left untouched, and any moves the user redirected or skipped.

Call out anything that needs a human eye: collisions you renamed around, notes where no folder fit well and you created a new one, atomic sets you weren't confident about.

## Failure modes to avoid

- **Moving before atomics exist.** The cardinal sin. If you ever find yourself running `move-file` on a source whose atomic notes haven't been written yet, stop — you'll strand the back-links.
- **Acting on unknown verbs.** `#action/bridge` and friends are not your job. Report them, leave them.
- **Substring matching.** Always use the finder script. "action/" inside a word is not a tag.
- **Over-atomizing.** Five sharp notes beat twelve fragments. The unit is the idea, not the sentence.
- **Silent new folders.** If nothing fits and you make a new area/resource folder, say so explicitly in the report — a new folder is a structural decision the user should see.
