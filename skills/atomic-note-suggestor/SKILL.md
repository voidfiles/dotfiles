---
name: atomic-note-suggestor
description: Suggest atomic notes from any content — a file, research report, article, or pasted text. Each suggestion has a focused concept-oriented title, self-contained body, a #atomic/{idea} tag, and additional helpful tags. Use whenever the user says "atomic notes", "atomize this", "what notes could I make from this?", "extract atomic ideas", "break this into zettelkasten notes", or when working with any research or article they want to distill into reusable, linkable knowledge units. Prefer this over extract-permanent-notes when the content hasn't been through the Obsidian triage/highlight workflow.
argument-hint: [file-path or leave empty if content is in context]
---

# Atomic Note Suggestor

Pull the worth-keeping ideas out of content and draft them as atomic notes — self-contained, concept-oriented, and ready to link.

## What makes a good atomic note

- **One idea**: not a summary, not a list. One claim, one principle, one tension. If the note would need a "Part 1" and "Part 2," it's not atomic yet.
- **Concept title**: phrases like "Atomicity trades off cohesion for reusability" or "RAG chunking is atomic-note granularity, machine-scale" — titles that function like API names (Matuschak's framing). Avoid vague gerunds ("Understanding atomicity") and source-bound titles ("From X: the atomicity principle"). Questions work: "Why do too-short notes fail?"
- **Self-contained body**: your future self should understand the note cold, without the source. If the note starts with "as mentioned above…" it's not done.
- **Source anchor**: a link back so context is always recoverable — this is the partial resolution to the atomicity/context tension.
- **Linked out**: an atomic note that connects to nothing is an orphan, and an orphan is dead weight. A good note names the *other* atomic notes it relates to, so the graph actually forms. Titles-as-APIs only pay off if something calls them.
- **Right size**: atomicity is about *focus*, not word count. Some ideas take two paragraphs; some take eight. Hydrogen and plutonium are both atoms.

## Process

### Step 1: Read the content

If `$ARGUMENTS` is a file path, read the file. If the content is already in the conversation, work from that directly.

### Step 2: Identify ideas worth keeping

Scan for candidates. Not everything earns a note — look for:
- Claims that would shift how you think about something
- Principles that generalize beyond this source
- Non-obvious tensions or tradeoffs
- Reframings that do real conceptual work
- Cross-domain connections most people miss

Skip: background scaffolding, obvious restatements, boilerplate context, anything that only makes sense inside the original document.

Aim for 3–7 notes per typical article or report. More than 8 usually means granularity is too fine. Ask: "Would this matter to someone five years from now who never read the source?"

### Step 3: Draft each note

For each idea, produce:

**Title** — a complete thought, specific enough to link to. Not "Atomicity" but "Atomicity is about focus, not word count."

**Body** — 2–4 paragraphs. Write declaratively ("Atomicity is a dial…") not bibliographically ("The author argues…"). Be concrete. Include the failure mode if there is one. Include a useful analogy if one exists.

**Tags**:
- Primary: `#atomic/{idea}` where `{idea}` is kebab-case (e.g. `#atomic/note-granularity`, `#atomic/rag-chunking`, `#atomic/separation-of-concerns`)
- Domain: 2–5 additional tags from the relevant topic space

**Source**: path or URL back to the original.

Output each suggestion in this format:

```markdown
---
title: [Note title]
type: atomic-note
created: YYYY-MM-DD
source: [[path/to/source]]
tags:
  - atomic/{idea}
  - domain-tag
  - domain-tag
---

# [Note title]

[Body — 2-4 paragraphs]

## Related

- [[Existing atomic note title]] — why it relates, in one line
- [[Another atomic note title]] — the connection, in one line

*From: [[source]]*
```

The `## Related` block is filled in by Step 4. Omit it entirely for a note that genuinely has no neighbors yet — an empty heading is noise.

### Step 4: Link each note to related atomic notes

This is the step that keeps the graph from filling up with orphans. For each drafted note, find the *existing* atomic notes it should connect to and write them into its `## Related` block. This is the canonical procedure — other skills (`process-action-notes`, `extract-permanent-notes`, `article-notes`) reference this step rather than reinventing it.

Discovery runs through the **Obsidian CLI** (Obsidian must be open). Never hand-roll a vault grep, and never invent a `[[target]]` — you may only link to a note the CLI actually returned.

1. **Pull candidates by tag.** Each drafted note has domain tags. Search the `#atomic/` namespace for overlapping ones:
   ```bash
   obsidian search query="tag:#atomic/<domain>" limit=20
   obsidian tags | grep atomic     # to see the live #atomic/* namespace
   ```
2. **Pull candidates by concept.** Search the note's key terms for thematic neighbors the tags miss:
   ```bash
   obsidian search:context query="<concept phrase>" limit=10
   ```
3. **Confirm genuine fit.** `obsidian read path="<candidate>"` on the promising hits. Link only on a *real* conceptual relationship — shared subject, a tension, one extends the other. A coincidental tag overlap is not a connection. If nothing genuinely relates, the note ships with no `## Related` block; do not force links to hit a quota.
4. **Write forward links only.** Add each confirmed neighbor to this note's `## Related` block as `[[Exact Note Title]] — one-line reason`. Use the candidate's real title (its filename without `.md`) so the wikilink resolves. Do **not** edit the other note to add a backlink — linking is forward-only here; Obsidian surfaces the reverse direction through `obsidian backlinks` on its own.

Aim for 1–4 related links when they exist. More than that usually means the note isn't atomic enough, or you're linking on theme rather than substance.

### Step 5: Ask about writing to files

After presenting all suggestions (bodies plus their `## Related` links):

> "Want me to write any of these to your vault? Tell me which ones, and where to save them (default: `resources/permanent-notes/`)."

If the user wants files written:
1. Use naming: `[Title].md` — the concept title only, no timestamp or date prefix/suffix in the filename
2. Write each file to the target path, `## Related` block included
3. List the files created

## Failure modes to avoid

**Context-stripping**: A note about "the tradeoff" without naming the tradeoff is useless. Make it specific enough to stand alone.

**Empty universals**: "Atomicity has benefits and tradeoffs" says nothing. Drill into which tradeoffs and why they matter.

**Duplicate ideas**: If two candidates say essentially the same thing, merge them or pick the stronger one.

**Over-atomizing**: Splitting until every note is one sentence produces a fragmented graph where nothing connects meaningfully. The unit is the *idea*, not the clause.

**Orphaning**: Writing a note with no `## Related` links when real neighbors exist in the vault. Step 4 is not optional decoration — an atomic note that connects to nothing rarely gets found again. Run the searches before deciding a note has no neighbors.

**Forced or invented links**: The opposite failure. Padding `## Related` with weak tag-coincidence matches, or worse, a `[[link]]` to a note that doesn't exist. Only link to notes the CLI returned, and only on a genuine relationship.

## Tag conventions

Some good `#atomic/{idea}` slugs:
- `#atomic/note-granularity` — the atomicity dial tradeoff
- `#atomic/zettelkasten` — Luhmann's method / the slip-box
- `#atomic/rag-chunking` — LLM retrieval chunk sizing
- `#atomic/separation-of-concerns` — the SRP applied to thought
- `#atomic/evergreen-notes` — Matuschak's framing
- `#atomic/note-titles-as-apis` — titles as stable reference interfaces

Additional domain tags: `#pkm`, `#zettelkasten`, `#note-taking`, `#rag`, `#llm`, `#learning`, `#knowledge-management`, `#writing`, `#productivity`, `#cognitive-tools`

## Example (from an atomic notes research report)

Given a research report on atomic notes, good candidates include:

**"Atomicity is a dial, not a binary target"**
`#atomic/note-granularity`, `#pkm`, `#zettelkasten`
> The failure modes sit at both extremes: notes too coarse bury ideas and muddy links; notes too fine fragment the graph, lose context, and generate maintenance friction. "One idea" has no objective definition — experienced practitioners treat granularity as something to tune per idea, not a rule to hit.

**"Note titles function like API names"**
`#atomic/note-titles-as-apis`, `#pkm`, `#software-engineering`
> Matuschak's insight: a well-formed evergreen note title is a stable interface that lets other notes "call" the idea by reference. Vague titles ("Atomicity") are ambiguous imports; specific titles ("Atomicity trades off cohesion for reusability") are typed, descriptive exports. The discipline of titling forces the clarification that makes linking precise.

**"RAG proposition-chunking rediscovers atomic notes"**
`#atomic/rag-chunking`, `#rag`, `#llm`, `#pkm`
> Retrieval-augmented generation systems that extract one-claim-at-a-time propositions for embedding hit the same tradeoff as Zettelkasten atomicity: too-short chunks lose context, too-long chunks add noise. The finding is that fixed-length splitting "splits concepts or adds noise" — nearly word for word the case against bad note granularity. Atomicity, conceived in the 1950s as an index-card constraint, turns out to describe a near-optimal unit for 2025-era semantic retrieval.
