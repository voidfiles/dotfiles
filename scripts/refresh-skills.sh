#!/usr/bin/env bash
# Fetch skills from external repos and copy them into the local skills/ folder.
# After running this, commit the changes and chezmoi will sync them to ~/.claude/skills/.
#
# To add a new source, append an entry to SKILL_SOURCES below:
#   "git@github.com:org/repo.git|src-subfolder|skill-a skill-b skill-c"
# Leave src-subfolder blank ("") to copy from the repo root.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
EXTERNAL_MANIFEST="$SCRIPT_DIR/.external-skills"

# ---------------------------------------------------------------------------
# SKILL_SOURCES: each entry is pipe-separated
#   <repo-url> | <subfolder-in-repo> | <space-separated skill names>[:<local skill name>]
# ---------------------------------------------------------------------------
SKILL_SOURCES=(
    "https://github.com/K-Dense-AI/claude-scientific-skills.git|scientific-skills|bgpt-paper-search literature-review paper-lookup"
    "https://github.com/mattnowdev/thinking-partner.git|skills|thinking-partner:model-based-thinking"
)

# ---------------------------------------------------------------------------

TMPDIR_BASE="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_BASE"' EXIT

# Rebuild the manifest from scratch on each run
: > "$EXTERNAL_MANIFEST"

updated=0
errors=0

for entry in "${SKILL_SOURCES[@]}"; do
    IFS='|' read -r repo subfolder skill_list <<< "$entry"

    repo_name="$(basename "$repo" .git)"
    clone_dir="$TMPDIR_BASE/$repo_name"

    echo "==> Cloning $repo_name ..."
    if ! git clone --depth=1 --quiet "$repo" "$clone_dir" 2>&1; then
        echo "    ERROR: failed to clone $repo" >&2
        (( errors++ )) || true
        continue
    fi

    src_base="$clone_dir"
    if [[ -n "$subfolder" ]]; then
        src_base="$clone_dir/$subfolder"
    fi

    if [[ ! -d "$src_base" ]]; then
        echo "    ERROR: subfolder '$subfolder' not found in $repo_name" >&2
        (( errors++ )) || true
        continue
    fi

    for skill_spec in $skill_list; do
        # Support "remote_name:local_name" rename syntax
        remote_name="${skill_spec%%:*}"
        local_name="${skill_spec##*:}"
        # If no colon, both are the same
        [[ "$remote_name" == "$local_name" ]] || true

        src="$src_base/$remote_name"
        dst="$SKILLS_DIR/$local_name"

        if [[ ! -d "$src" ]]; then
            echo "    WARNING: skill '$remote_name' not found in $repo_name/$subfolder" >&2
            (( errors++ )) || true
            continue
        fi

        if [[ "$remote_name" != "$local_name" ]]; then
            echo "    Copying $remote_name -> $local_name ..."
        else
            echo "    Copying $remote_name ..."
        fi
        rm -rf "$dst"
        cp -R "$src" "$dst"
        echo "$local_name" >> "$EXTERNAL_MANIFEST"
        (( updated++ )) || true
    done
done

echo ""
echo "Done. $updated skill(s) updated, $errors error(s)."
if (( errors > 0 )); then
    exit 1
fi
