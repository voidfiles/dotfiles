#!/usr/bin/env bats

load '../helpers/common'

setup() {
  make_scratch_home
}

_read_obsidian_var() {
  local var="$1"; shift
  local setup="$*"

  bash --norc --noprofile -c "
    export HOME='$HOME'
    export USE_1_PASSWORD=0
    unset OBSIDIAN_ROOT OBSIDIAN_ROOT_CANDIDATES
    $setup
    source '$DOTFILES_REPO_ROOT/config/router.sh' >/dev/null 2>&1
    printf '%s' \"\${$var}\"
  "
}

_read_claude_render_alias() {
  local setup="$*"

  bash --norc --noprofile -c "
    shopt -s expand_aliases
    export HOME='$HOME'
    export USE_1_PASSWORD=0
    unset OBSIDIAN_ROOT OBSIDIAN_ROOT_CANDIDATES
    $setup
    source '$DOTFILES_REPO_ROOT/config/router.sh' >/dev/null 2>&1
    alias claude-render
  "
}

@test "OBSIDIAN_ROOT honors explicit local override" {
  mkdir -p "$HOME/Documents/Alex3/.obsidian"
  mkdir -p "$HOME/custom-vault/.obsidian"

  run _read_obsidian_var OBSIDIAN_ROOT 'export OBSIDIAN_ROOT="$HOME/custom-vault"'

  assert_success
  assert_output "$HOME/custom-vault"
}

@test "OBSIDIAN_ROOT defaults to Documents vault before Dropbox vault" {
  mkdir -p "$HOME/Documents/Alex3/.obsidian"
  mkdir -p "$HOME/Dropbox/obsidian/Alex3/.obsidian"

  run _read_obsidian_var OBSIDIAN_ROOT ''

  assert_success
  assert_output "$HOME/Documents/Alex3"
}

@test "OBSIDIAN_ROOT_CANDIDATES controls auto-detection order" {
  mkdir -p "$HOME/Documents/Alex3/.obsidian"
  mkdir -p "$HOME/Dropbox/obsidian/Alex3/.obsidian"

  run _read_obsidian_var OBSIDIAN_ROOT 'export OBSIDIAN_ROOT_CANDIDATES="$HOME/Dropbox/obsidian/Alex3:$HOME/Documents/Alex3"'

  assert_success
  assert_output "$HOME/Dropbox/obsidian/Alex3"
}

@test "claude-render alias uses resolved OBSIDIAN_ROOT" {
  mkdir -p "$HOME/custom-vault/.obsidian"

  run _read_claude_render_alias 'export OBSIDIAN_ROOT="$HOME/custom-vault"'

  assert_success
  [[ "$output" == *'${OBSIDIAN_ROOT:-$HOME/Documents/Alex3}/.claude/scripts/render.py'* ]]
}
