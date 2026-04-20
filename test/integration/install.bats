#!/usr/bin/env bats

load '../helpers/common'
load '../helpers/integration'

setup() {
  assert_safe_home
}

@test "update.sh completes successfully" {
  run bash "$HOME/.local/share/dotfiles/scripts/update.sh"
  assert_success
}

@test "bork on PATH after install" {
  run command -v bork
  assert_success
}

@test "just on PATH after install" {
  run command -v just
  assert_success
}

@test "gitconfig rendered with no literal placeholders" {
  assert_file_exists "$HOME/.gitconfig"
  run grep -F '${GIT_EMAIL}' "$HOME/.gitconfig"
  assert_failure
  run grep -F '${GIT_NAME}' "$HOME/.gitconfig"
  assert_failure
}

@test "claude config copied from repo" {
  run diff "$HOME/.claude/settings.json" "$HOME/.local/share/dotfiles/config/claude/settings.json"
  assert_success
  run diff "$HOME/.claude/CLAUDE.md" "$HOME/.local/share/dotfiles/config/claude/CLAUDE.md"
  assert_success
}

@test "direnv installed" {
  run command -v direnv
  assert_success
}

@test "uv present on PATH or at ~/.local/bin" {
  local pass=0
  command -v uv >/dev/null 2>&1 && pass=1
  [[ -x "$HOME/.local/bin/uv" ]] && pass=1
  assert_equal "$pass" "1"
}

@test "claude cli present on PATH or at ~/.local/bin" {
  local pass=0
  command -v claude >/dev/null 2>&1 && pass=1
  [[ -x "$HOME/.local/bin/claude" ]] && pass=1
  assert_equal "$pass" "1"
}

@test "router line in rc file appears exactly once" {
  local rc_file
  if [[ "${SHELL_TO_USE:-zsh}" == "zsh" ]]; then
    rc_file="$HOME/.zshrc"
  else
    rc_file="$HOME/.bashrc"
  fi
  local line='source "$HOME/.local/share/dotfiles/config/router.sh"'
  run grep -cF "$line" "$rc_file"
  assert_output "1"
}

@test "oh-my-zsh installed iff zsh on macOS" {
  if [[ "$(uname)" == "Darwin" && "${SHELL_TO_USE:-zsh}" == "zsh" ]]; then
    assert_dir_exists "$HOME/.oh-my-zsh"
  fi
  if [[ "${SHELL_TO_USE:-zsh}" == "bash" ]]; then
    assert_dir_not_exists "$HOME/.oh-my-zsh"
  fi
}

@test "1Password artifacts present iff USE_1_PASSWORD=1" {
  if [[ "${USE_1_PASSWORD:-0}" == "1" ]]; then
    if [[ "$(uname)" == "Linux" ]]; then
      assert_file_exists /usr/share/keyrings/1password-archive-keyring.gpg
      run grep -q '1password' /etc/apt/sources.list.d/1password.list
      assert_success
    fi
    run command -v op
    assert_success
  else
    if [[ "$(uname)" == "Linux" ]]; then
      assert_file_not_exists /usr/share/keyrings/1password-archive-keyring.gpg
      assert_file_not_exists /etc/apt/sources.list.d/1password.list
    fi
    run command -v op
    assert_failure
  fi
}

@test "rerun: idempotent, no duplicate router line" {
  if [[ "${RUN_MODE:-fresh}" != "rerun" ]]; then
    skip "only runs in rerun mode"
  fi
  run bash "$HOME/.local/share/dotfiles/scripts/update.sh"
  assert_success

  local rc_file
  if [[ "${SHELL_TO_USE:-zsh}" == "zsh" ]]; then
    rc_file="$HOME/.zshrc"
  else
    rc_file="$HOME/.bashrc"
  fi
  local line='source "$HOME/.local/share/dotfiles/config/router.sh"'
  run grep -cF "$line" "$rc_file"
  assert_output "1"

  if [[ "${USE_1_PASSWORD:-0}" == "1" && "$(uname)" == "Linux" ]]; then
    run grep -c '1password' /etc/apt/sources.list.d/1password.list
    assert_output "1"
  fi
}
