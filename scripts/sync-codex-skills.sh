#!/usr/bin/env bash
# Symlink personal skills (and optionally work skills) into ~/.codex/skills/
# so Codex picks them up the same way Claude Code does via plugins.
#
# Run this whenever you add or rename a skill directory:
#   just sync-codex-skills
#
# Work skills source can be overridden via CODEX_WORK_SKILLS_DIR env var.
# Set it to "" to skip work skills entirely.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
CODEX_SKILLS_DIR="$CODEX_HOME/skills"

PERSONAL_SKILLS_DIR="$REPO_ROOT/skills"
WORK_SKILLS_DIR="${CODEX_WORK_SKILLS_DIR:-$HOME/.local/share/chezmoi-work/skills}"

linked=0
skipped=0
removed=0

_link_skills_from() {
    local src_dir="$1"
    local label="$2"

    if [[ ! -d "$src_dir" ]]; then
        echo "  Skipping $label — directory not found: $src_dir"
        return
    fi

    echo "  Source: $src_dir"
    for skill_dir in "$src_dir"/*/; do
        [[ -d "$skill_dir" ]] || continue
        local name
        name="$(basename "$skill_dir")"
        local target="$CODEX_SKILLS_DIR/$name"

        if [[ -L "$target" ]]; then
            local current_link
            current_link="$(readlink "$target")"
            if [[ "$current_link" == "$skill_dir" || "$current_link" == "${skill_dir%/}" ]]; then
                (( skipped++ )) || true
                continue
            fi
            # Points somewhere else — update it
            rm "$target"
        elif [[ -e "$target" ]]; then
            echo "    WARNING: $name exists as a real file/dir, skipping (remove manually to replace)"
            (( skipped++ )) || true
            continue
        fi

        ln -s "$skill_dir" "$target"
        echo "    Linked $name"
        (( linked++ )) || true
    done
}

_prune_stale_links() {
    # Remove symlinks that point into our source dirs but whose targets no longer exist
    for link in "$CODEX_SKILLS_DIR"/*/; do
        [[ -L "${link%/}" ]] || continue
        local dest
        dest="$(readlink "${link%/}")"
        if [[ ! -e "$dest" ]]; then
            local name
            name="$(basename "${link%/}")"
            rm "${link%/}"
            echo "  Removed stale link: $name"
            (( removed++ )) || true
        fi
    done
}

mkdir -p "$CODEX_SKILLS_DIR"

echo "==> Personal skills"
_link_skills_from "$PERSONAL_SKILLS_DIR" "personal skills"

if [[ -n "${CODEX_WORK_SKILLS_DIR+x}" && -z "$CODEX_WORK_SKILLS_DIR" ]]; then
    echo "==> Work skills (skipped — CODEX_WORK_SKILLS_DIR is empty)"
else
    echo "==> Work skills"
    _link_skills_from "$WORK_SKILLS_DIR" "work skills"
fi

echo "==> Pruning stale links"
_prune_stale_links

echo ""
echo "Done. $linked linked, $skipped already up-to-date, $removed stale removed."
