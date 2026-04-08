#!/usr/bin/env bash
# Detect changes in ~/.claude/skills/ and migrate them back into the chezmoi
# skills/ directory. Skills managed by refresh-skills (listed in
# scripts/.external-skills) are intentionally ignored.
#
# Usage:
#   ./scripts/sync-skills-back.sh          # dry-run: show what would change
#   ./scripts/sync-skills-back.sh --apply  # actually copy changes back

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SRC="$HOME/.claude/skills"
SKILLS_DST="$REPO_ROOT/skills"
EXTERNAL_MANIFEST="$SCRIPT_DIR/.external-skills"

DRY_RUN=true
if [[ "${1:-}" == "--apply" ]]; then
    DRY_RUN=false
fi

# ---------------------------------------------------------------------------
# Load external skill names to skip
# ---------------------------------------------------------------------------
declare -A external_skills=()
if [[ -f "$EXTERNAL_MANIFEST" ]]; then
    while IFS= read -r line; do
        [[ -z "$line" || "$line" == "#"* ]] && continue
        external_skills["$line"]=1
    done < "$EXTERNAL_MANIFEST"
fi

if $DRY_RUN; then
    echo "==> Dry run — pass --apply to write changes"
    echo ""
fi

updated=0
added=0
skipped_external=0
skipped_unchanged=0

for skill_dir in "$SKILLS_SRC"/*/; do
    [[ -d "$skill_dir" ]] || continue
    skill_name="$(basename "$skill_dir")"

    if [[ -n "${external_skills[$skill_name]+_}" ]]; then
        (( skipped_external++ )) || true
        continue
    fi

    # Skills prefixed with stripe_ are managed by a separate repo
    if [[ "$skill_name" == stripe_* ]]; then
        (( skipped_external++ )) || true
        continue
    fi

    dst="$SKILLS_DST/$skill_name"

    if [[ ! -d "$dst" ]]; then
        echo "  NEW      $skill_name"
        if ! $DRY_RUN; then
            cp -R "$skill_dir" "$dst"
        fi
        (( added++ )) || true
        continue
    fi

    if diff -rq --exclude='*.pyc' "$skill_dir" "$dst" > /dev/null 2>&1; then
        (( skipped_unchanged++ )) || true
        continue
    fi

    echo "  CHANGED  $skill_name"
    if ! $DRY_RUN; then
        rm -rf "$dst"
        cp -R "$skill_dir" "$dst"
    fi
    (( updated++ )) || true
done

echo ""
if $DRY_RUN; then
    echo "$updated changed, $added new, $skipped_external external (ignored), $skipped_unchanged unchanged."
    if (( updated + added > 0 )); then
        echo "Run with --apply to copy them back."
    fi
else
    echo "Done. $updated updated, $added added, $skipped_external external (ignored), $skipped_unchanged unchanged."
fi
