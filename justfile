set shell := ["bash", "-euo", "pipefail", "-c"]

# Show available recipes
default:
    @just --list

# Apply chezmoi source state to the home directory
apply:
    chezmoi apply

# Preview what chezmoi would change without applying
diff:
    chezmoi diff

# Show which managed files have drifted
status:
    chezmoi status

# Pull latest from git remote and apply
update:
    chezmoi update

# Pull manual edits from a managed file back into the source
re-add file:
    chezmoi re-add {{ file }}

# Fetch skills from external repos into skills/
refresh-skills:
    bash scripts/refresh-skills.sh

# Apply chezmoi, which syncs any new skills to ~/.claude/skills/
sync-skills: apply

# Force a run_onchange_ script to re-run on next `chezmoi apply`
# Usage: just force-onchange sync-skills
force-onchange script:
    bash scripts/force-onchange.sh {{ script }}

# Refresh skills from upstream, then sync them via chezmoi apply
upgrade-skills: refresh-skills sync-skills

# Show skills in ~/.claude/skills/ that differ from chezmoi (dry-run)
check-skills-back:
    bash scripts/sync-skills-back.sh

# Copy changed/new skills from ~/.claude/skills/ back into chezmoi skills/
sync-skills-back:
    bash scripts/sync-skills-back.sh --apply
