#! /usr/bin/env bash
set -e

DOTFILES_DIR="${DOTFILES_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

source "$DOTFILES_DIR/config/config.sh"
source "$DOTFILES_DIR/scripts/util.sh"

if [[ "${IS_DARWIN:-0}" == "1" ]] && [[ ! -d "$HOME/.oh-my-zsh" ]]; then
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi

if [[ "${USE_1_PASSWORD:-0}" == "1" ]]; then
  if [[ "${IS_DARWIN:-0}" == "1" ]]; then
    bork 'do' ok cask 1password-cli
  else
    keyring=/usr/share/keyrings/1password-archive-keyring.gpg
    source_list=/etc/apt/sources.list.d/1password.list
    arch=$(dpkg --print-architecture)
    source_line="deb [arch=${arch} signed-by=${keyring}] https://downloads.1password.com/linux/debian/${arch} stable main"

    if [[ ! -s "$keyring" ]]; then
      curl -fsSL https://downloads.1password.com/linux/keys/1password.asc \
        | sudo gpg --dearmor --output "$keyring"
    fi

    if [[ ! -f "$source_list" ]] || ! grep -qxF "$source_line" "$source_list"; then
      echo "$source_line" | sudo tee "$source_list" >/dev/null
      sudo apt-get update
    fi

    bork 'do' ok apt 1password-cli
  fi
fi

ensure_package direnv

if ! command -v uv >/dev/null 2>&1 && ! [[ -x "$HOME/.local/bin/uv" ]]; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi


if [[ "${IS_LINUX:-0}" == "1" ]] && [[ "${IS_ZSH:-0}" == "1" ]] && command -v zsh >/dev/null 2>&1; then
  zsh_path="$(command -v zsh)"
  if [[ "${SHELL:-}" != "$zsh_path" ]]; then
    chsh -s "$zsh_path"
  fi
fi

if [[ "${IS_ZSH:-0}" == "1" ]]; then
  rc_file="$HOME/.zshrc"
else
  rc_file="$HOME/.bashrc"
fi

router_line='source "$HOME/.local/share/dotfiles/config/router.sh"'
touch "$rc_file"
if ! grep -qxF "$router_line" "$rc_file"; then
  printf '\n%s\n' "$router_line" >> "$rc_file"
fi



ensure_package gettext
ensure_package jq

envsubst < "$DOTFILES_DIR/templates/dot_gitconfig.tmpl" > "$HOME/.gitconfig"

mkdir -p "$HOME/.claude" "$HOME/.claude/plugins"

if [[ -f "$HOME/.local_claude.json" ]]; then
  jq -s '.[0] * .[1]' "$DOTFILES_DIR/config/claude/settings.json" "$HOME/.local_claude.json" > "$HOME/.claude/settings.json"
else
  cp "$DOTFILES_DIR/config/claude/settings.json" "$HOME/.claude/settings.json"
fi

cp "$DOTFILES_DIR/config/claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md"

if [[ -L "$HOME/.claude/workflows" ]]; then
  rm "$HOME/.claude/workflows"
elif [[ -d "$HOME/.claude/workflows" ]]; then
  rm -rf "$HOME/.claude/workflows"
fi
ln -s "$DOTFILES_DIR/config/claude/workflows" "$HOME/.claude/workflows"

# Register directory-based marketplaces in Claude Code's plugin cache so they
# are available immediately without waiting for Claude to resolve them on next
# startup. Reads extraKnownMarketplaces from the just-written settings.json and
# upserts any "directory" source entries into known_marketplaces.json.
_km="$HOME/.claude/plugins/known_marketplaces.json"
[[ -f "$_km" ]] || echo '{}' > "$_km"

_now="$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")"
_patch=$(jq -r --arg now "$_now" '
  .extraKnownMarketplaces // {} | to_entries
  | map(select(.value.source.source == "directory"))
  | map({
      key: .key,
      value: {
        source: { source: "directory", path: (.value.source.path | gsub("^~"; env.HOME) ) },
        installLocation: (.value.source.path | gsub("^~"; env.HOME) ),
        lastUpdated: $now
      }
    })
  | from_entries
' "$HOME/.claude/settings.json")

jq --argjson patch "$_patch" '. * $patch' "$_km" > "${_km}.tmp" && mv "${_km}.tmp" "$_km"

# Register enabled directory-based plugins in installed_plugins.json and set up
# cache symlinks so Claude Code sees them without a manual /plugins install.
_ip="$HOME/.claude/plugins/installed_plugins.json"
[[ -f "$_ip" ]] || echo '{"version":2,"plugins":{}}' > "$_ip"

jq -r '
  .extraKnownMarketplaces // {} | to_entries[]
  | select(.value.source.source == "directory")
  | [.key, (.value.source.path | gsub("^~"; env.HOME))] | @tsv
' "$HOME/.claude/settings.json" | while IFS=$'\t' read -r mk_name mk_path; do
  # Read the marketplace's plugin list and register each enabled one
  _mkt_file="$mk_path/.claude-plugin/marketplace.json"
  [[ -f "$_mkt_file" ]] || continue

  jq -r '.plugins[]? | .name' "$_mkt_file" | while read -r plugin_name; do
    _key="${plugin_name}@${mk_name}"

    # Skip if not enabled
    _enabled=$(jq -r --arg k "$_key" '.enabledPlugins[$k] // false' "$HOME/.claude/settings.json")
    [[ "$_enabled" == "true" ]] || continue

    # Read version from plugin.json
    _ver=$(jq -r '.version // "1.0.0"' "$mk_path/.claude-plugin/plugin.json")
    _cache_dir="$HOME/.claude/plugins/cache/${mk_name}/${plugin_name}/${_ver}"

    # Symlink the source dir into the cache so Claude reads skills from there
    mkdir -p "$(dirname "$_cache_dir")"
    if [[ -L "$_cache_dir" ]]; then
      rm "$_cache_dir"
    elif [[ -d "$_cache_dir" ]]; then
      rm -rf "$_cache_dir"
    fi
    ln -s "$mk_path" "$_cache_dir"

    # Upsert into installed_plugins.json
    jq --arg key "$_key" --arg path "$_cache_dir" --arg ver "$_ver" --arg now "$_now" '
      .plugins[$key] = [{
        scope: "user",
        installPath: $path,
        version: $ver,
        installedAt: ($now),
        lastUpdated: ($now)
      }]
    ' "$_ip" > "${_ip}.tmp" && mv "${_ip}.tmp" "$_ip"
  done
done

if ! command -v claude >/dev/null 2>&1 && ! [[ -x "$HOME/.local/bin/claude" ]]; then
  curl -fsSL https://claude.ai/install.sh | bash
fi




