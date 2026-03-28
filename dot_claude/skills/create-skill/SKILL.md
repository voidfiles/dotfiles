---
name: create-skill
description: Create a new Claude Code skill. Use when the user wants to add a custom slash command or extend Claude's capabilities.
argument-hint: [skill-name] [description of what it should do]
disable-model-invocation: true
---

# Create New Skill

Create a new Claude Code skill based on the user's requirements.

## Input

**Skill Request:** $ARGUMENTS

## Process

1. **Clarify Requirements**
   - What should the skill do?
   - Should Claude invoke it automatically, or only the user via `/skill-name`?
   - Does it need specific tools?
   - Should it run inline or in a subagent (`context: fork`)?

2. **Design the Skill**
   - Name: lowercase letters, numbers, and hyphens only (max 64 chars)
   - Description: explains what the skill does and when Claude should use it
   - Frontmatter options as needed
   - Clear instructions in markdown

3. **Create the Skill**
   - Location: `.claude/skills/[skill-name]/SKILL.md`
   - Include YAML frontmatter between `---` markers
   - Write clear, actionable instructions

## SKILL.md Template

```yaml
---
name: skill-name
description: What this skill does and when to use it. Claude uses this to decide when to apply the skill automatically.
# Optional fields:
# argument-hint: [arg1] [arg2]           # Shown during autocomplete
# disable-model-invocation: true         # Only user can invoke via /skill-name
# user-invocable: false                  # Only Claude can invoke (background knowledge)
# allowed-tools: Read, Grep, Glob        # Restrict available tools
# context: fork                          # Run in isolated subagent
# agent: Explore                         # Which agent type for context: fork
---

# Skill Title

Clear instructions for what Claude should do when this skill is invoked.

## Task

[What the skill accomplishes]

## Process

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Output

[Expected output format]
```

## Key Frontmatter Fields

| Field                      | Purpose                                                        |
| -------------------------- | -------------------------------------------------------------- |
| `name`                     | Display name and `/slash-command` (defaults to directory name) |
| `description`              | Tells Claude when to use this skill (recommended)              |
| `argument-hint`            | Shows expected arguments during autocomplete                   |
| `disable-model-invocation` | Set `true` to prevent Claude auto-invoking                     |
| `user-invocable`           | Set `false` to hide from `/` menu (Claude-only)                |
| `allowed-tools`            | Restrict which tools Claude can use                            |
| `context`                  | Set to `fork` for isolated subagent execution                  |
| `agent`                    | Agent type for forked context (Explore, Plan, general-purpose) |

## Skill Types

**Reference skills** - Add knowledge Claude applies to current work:

- Coding conventions, style guides, domain knowledge
- Usually auto-invoked by Claude when relevant

**Task skills** - Step-by-step instructions for specific actions:

- Deployments, commits, code generation workflows
- Often use `disable-model-invocation: true` for manual control

## Where to Store Skills

| Location | Path                               | Applies to        |
| -------- | ---------------------------------- | ----------------- |
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects |
| Project  | `.claude/skills/<name>/SKILL.md`   | This project only |

## Best Practices

- Write descriptions that match how users naturally ask for help
- Keep `SKILL.md` under 500 lines; use supporting files for detailed references
- Use `$ARGUMENTS` placeholder for user input
- Use `bang` command`` syntax for dynamic context injection
- Add `disable-model-invocation: true` for skills with side effects

Now I'll create your skill`!`
