# Update Project Index

This skill performs a weekly review of all projects, writes updates for each, and refreshes the project index.

## Overview

The project index lives at `projects/index.md`. This skill:

1. Analyzes recent activity for each project (files changed/created in last 7 days)
2. Writes a weekly update for each project's index.md
3. Updates the master project index with embedded summaries

## Execution Strategy

**Use concurrent Task agents** to maximize efficiency. Projects can be analyzed in parallel since they're independent.

## Phase 1: Discover Projects

List all project folders in `projects/` that have an `index.md` file.

```bash
find projects -maxdepth 2 -name "index.md" -type f
```

## Phase 2: Analyze & Update Each Project (CONCURRENT)

**Launch Task agents in parallel** - one for each project. Each agent should:

### 2a. Find Recent Activity

For each project folder, identify:

**Files modified in last 7 days:**
```bash
find projects/{project-name} -type f -mtime -7 -name "*.md"
```

**Files created in last 7 days:**
```bash
find projects/{project-name} -type f -ctime -7 -name "*.md"
```

Also check for related activity in:
- `daily/` - Daily notes that link to this project
- `meetings/` - Meeting notes that reference this project

### 2b. Analyze Changes

For each changed/created file:
- Read the file content
- Identify what changed (new sections, completed items, new notes)
- Look for patterns: completed TODOs, new blockers, decisions made

### 2c. Write Weekly Update

Add or update the `## Weekly Updates` section in the project's `index.md`:

```markdown
### Week of {YYYY-MM-DD}

**Progress:**

- {List concrete accomplishments based on file changes}
- {Completed TODOs, new documents created, decisions made}

**Challenges:**

- {Any blockers or difficulties identified}
- {Open questions discovered}

**Next Week:**

- {Upcoming work based on remaining TODOs}
- {Follow-ups needed}
```

**Guidelines for writing updates:**
- Be specific and concrete (reference actual files/changes)
- Focus on outcomes, not activity
- Keep each bullet to 1-2 lines
- If no activity found, note "No significant activity this week"

### Task Agent Prompt Template

```
Analyze project "{project-name}" and write a weekly update.

1. Find files modified in last 7 days in projects/{project-name}/
2. Find files created in last 7 days in projects/{project-name}/
3. Search daily/ and meetings/ for references to this project from the last week
4. Read the current projects/{project-name}/index.md
5. Based on the activity found, write a weekly update following this format:

### Week of {current week date}

**Progress:**
- {specific accomplishments}

**Challenges:**
- {blockers or issues}

**Next Week:**
- {upcoming work}

6. Edit projects/{project-name}/index.md to add or update the weekly update section
```

## Phase 3: Update Project Index

After all project updates complete, regenerate `projects/index.md`.

### Obsidian Embed Syntax

Embed specific headings from project index files:
```
![[projects/{project-name}/index#Executive Summary]]
![[projects/{project-name}/index#ToDos]]
```

### Index Template

```markdown
# Projects

## {Human Readable Project Name}

![[projects/{project-folder}/index#Executive Summary]]

![[projects/{project-folder}/index#ToDos]]

---

## {Human Readable Project Name}

![[projects/{project-folder}/index#Executive Summary]]

![[projects/{project-folder}/index#ToDos]]

---
```

### Naming Convention

Convert folder names to human-readable titles:
- `v2_account_specifications` → `V2 Account Specifications`
- `blog-post-fear-shame-arena` → `Blog Post: Fear, Shame, and the Arena`
- `stripe_beyond_payments` → `Stripe Beyond Payments`

## Execution Summary

```
┌─────────────────────────────────────────────────────────┐
│ Phase 1: Discover Projects                              │
│ - List all projects with index.md                       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ Phase 2: Update Each Project (PARALLEL)                 │
│                                                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │Project 1│ │Project 2│ │Project 3│ │Project N│       │
│  │  Task   │ │  Task   │ │  Task   │ │  Task   │       │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘       │
│       │           │           │           │             │
│       ▼           ▼           ▼           ▼             │
│  [Analyze]   [Analyze]   [Analyze]   [Analyze]         │
│  [Write]     [Write]     [Write]     [Write]           │
│  [Update]    [Update]    [Update]    [Update]          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼ (wait for all)
┌─────────────────────────────────────────────────────────┐
│ Phase 3: Update Project Index                           │
│ - Generate projects/index.md with embeds                │
└─────────────────────────────────────────────────────────┘
```

## Notes

- Skip archived projects (in `archives/` or marked archived in frontmatter)
- If a project has no activity, still include it in the index but note "No activity this week" in the update
- Preserve existing weekly updates in the Archive section when adding new ones
- Use `general-purpose` subagent type for the Task agents
