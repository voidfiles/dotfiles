#!/usr/bin/env bats

load '../helpers/common'

setup() {
  make_scratch_home
  install_stubs

  # Fake uv so update.sh skips the curl|sh install
  mkdir -p "$HOME/.local/bin"
  touch "$HOME/.local/bin/uv"
  chmod +x "$HOME/.local/bin/uv"

  # Fake claude so update.sh skips the curl|bash install
  touch "$HOME/.local/bin/claude"
  chmod +x "$HOME/.local/bin/claude"

  # Linux + zsh path would call chsh; force to a known state so the
  # "already the right shell" guard doesn't trip on whatever the host's
  # $SHELL is.  We just set IS_LINUX=0 (Darwin-like) to bypass that block.
  export USE_1_PASSWORD=0
  export IS_DARWIN=0
  export IS_LINUX=0
  export IS_ZSH=1
  export IS_BASH=0
  export GIT_EMAIL=test@example.com
  export GIT_NAME=tester
}

_run_update() {
  HOME="$HOME" \
  DOTFILES_DIR="$DOTFILES_DIR" \
  USE_1_PASSWORD=0 \
  IS_DARWIN=0 \
  IS_LINUX=0 \
  IS_ZSH=1 \
  IS_BASH=0 \
  GIT_EMAIL=test@example.com \
  GIT_NAME=tester \
  PATH="$PATH" \
  bash "$DOTFILES_DIR/scripts/update.sh"
}

@test "update.sh appends router line to .zshrc exactly once on first run" {
  run _run_update
  assert_success
  run grep -cF 'source "$HOME/.local/share/dotfiles/config/router.sh"' "$HOME/.zshrc"
  assert_output "1"
}

@test "update.sh does not duplicate router line on second run" {
  run _run_update
  assert_success
  run _run_update
  assert_success
  run grep -cF 'source "$HOME/.local/share/dotfiles/config/router.sh"' "$HOME/.zshrc"
  assert_output "1"
}

@test "update.sh renders gitconfig with no literal placeholders" {
  run _run_update
  assert_success
  assert_file_exists "$HOME/.gitconfig"
  run grep -F '${GIT_EMAIL}' "$HOME/.gitconfig"
  assert_failure
  run grep -F '${GIT_NAME}' "$HOME/.gitconfig"
  assert_failure
}

@test "update.sh gitconfig content is identical on second run" {
  run _run_update
  assert_success
  first="$(cat "$HOME/.gitconfig")"
  run _run_update
  assert_success
  second="$(cat "$HOME/.gitconfig")"
  assert_equal "$first" "$second"
}

@test "update.sh copies claude config files" {
  run _run_update
  assert_success
  assert_file_exists "$HOME/.claude/settings.json"
  assert_file_exists "$HOME/.claude/CLAUDE.md"
  run diff "$HOME/.claude/settings.json" "$DOTFILES_DIR/config/claude/settings.json"
  assert_success
  run diff "$HOME/.claude/CLAUDE.md" "$DOTFILES_DIR/config/claude/CLAUDE.md"
  assert_success
}

@test "update.sh installs local and configured skills for Claude Code and Codex" {
  run _run_update
  assert_success

  stub_assert_called npx --yes skills add "$DOTFILES_DIR/skills" --skill '*' --global --agent claude-code --agent codex --yes
  stub_assert_called npx --yes skills add shadcn/improve --skill '*' --global --agent claude-code --agent codex --yes
}

@test "update.sh removes old personal Claude marketplace cache entries" {
  mkdir -p "$HOME/.claude/plugins"
  printf '{"personal-marketplace":{"installLocation":"old"},"keep-marketplace":{"installLocation":"keep"}}\n' \
    > "$HOME/.claude/plugins/known_marketplaces.json"
  printf '{"version":2,"plugins":{"personal-skills@personal-marketplace":[{"installPath":"old"}],"keep@marketplace":[{"installPath":"keep"}]}}\n' \
    > "$HOME/.claude/plugins/installed_plugins.json"

  run _run_update
  assert_success

  run jq -e 'has("personal-marketplace") | not' "$HOME/.claude/plugins/known_marketplaces.json"
  assert_success
  run jq -e 'has("keep-marketplace")' "$HOME/.claude/plugins/known_marketplaces.json"
  assert_success
  run jq -e '.plugins | has("personal-skills@personal-marketplace") | not' "$HOME/.claude/plugins/installed_plugins.json"
  assert_success
  run jq -e '.plugins | has("keep@marketplace")' "$HOME/.claude/plugins/installed_plugins.json"
  assert_success
}
