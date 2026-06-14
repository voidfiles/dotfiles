#!/usr/bin/env bash
set -euo pipefail

DOTFILES_DIR="${DOTFILES_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
LOCAL_SKILLS_DIR="$DOTFILES_DIR/skills"
SOURCES_FILE="${SKILLS_SOURCES_FILE:-$DOTFILES_DIR/config/skills/sources.txt}"

install_args=(
  --skill '*'
  --global
  --agent claude-code
  --agent codex
  --yes
)

ensure_npx() {
  if command -v npx >/dev/null 2>&1; then
    return 0
  fi

  echo "npx is required to install skills. Install Node.js/npm, then rerun this script." >&2
  return 1
}

install_skill_source() {
  local source="$1"
  echo "==> Installing skills from $source"
  npx --yes skills add "$source" "${install_args[@]}"
}

append_configured_sources() {
  [[ -f "$SOURCES_FILE" ]] || return 0

  local line source
  while IFS= read -r line || [[ -n "$line" ]]; do
    source="${line%%#*}"
    source="${source#"${source%%[![:space:]]*}"}"
    source="${source%"${source##*[![:space:]]}"}"
    [[ -n "$source" ]] || continue
    sources+=("$source")
  done < "$SOURCES_FILE"
}

ensure_npx

if [[ ! -d "$LOCAL_SKILLS_DIR" ]]; then
  echo "Local skills directory not found: $LOCAL_SKILLS_DIR" >&2
  exit 1
fi

sources=("$LOCAL_SKILLS_DIR")
append_configured_sources

if [[ -n "${SKILL_SOURCES:-}" ]]; then
  # shellcheck disable=SC2206
  env_sources=($SKILL_SOURCES)
  sources+=("${env_sources[@]}")
fi

sources+=("$@")

for source in "${sources[@]}"; do
  install_skill_source "$source"
done
