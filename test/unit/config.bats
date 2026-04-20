#!/usr/bin/env bats

load '../helpers/common'

setup() {
  make_scratch_home
}

_read_flag() {
  local flag="$1"; shift
  local extra="${*:-true}"
  bash -c "HOME='$HOME'; $extra; source '$DOTFILES_REPO_ROOT/config/config.sh' >/dev/null 2>&1; printf '%s' \"\${$flag}\""
}

@test "IS_ZSH=1 and IS_BASH=0 when SHELL_TO_USE is unset" {
  unset SHELL_TO_USE
  run _read_flag IS_ZSH 'unset SHELL_TO_USE'
  assert_output "1"
  run _read_flag IS_BASH 'unset SHELL_TO_USE'
  assert_output "0"
}

@test "IS_BASH=1 when SHELL_TO_USE=bash" {
  run _read_flag IS_BASH 'export SHELL_TO_USE=bash'
  assert_output "1"
  run _read_flag IS_ZSH 'export SHELL_TO_USE=bash'
  assert_output "0"
}

@test "IS_DARWIN and IS_LINUX reflect uname" {
  run _read_flag IS_DARWIN ''
  if [[ "$(uname)" == "Darwin" ]]; then
    assert_output "1"
  else
    assert_output "0"
  fi
}

@test "USE_1_PASSWORD defaults to 1" {
  run _read_flag USE_1_PASSWORD 'unset USE_1_PASSWORD'
  assert_output "1"
}

@test "USE_1_PASSWORD honors local_config override" {
  local_conf="$HOME/.local_config.sh"
  printf 'export USE_1_PASSWORD=0\n' >"$local_conf"
  run _read_flag USE_1_PASSWORD ''
  assert_output "0"
}

@test "GIT_EMAIL default applies when unset" {
  run _read_flag GIT_EMAIL 'unset GIT_EMAIL'
  assert_output "voidfiles@gmail.com"
}

@test "GIT_EMAIL honors user-provided value" {
  run _read_flag GIT_EMAIL 'export GIT_EMAIL=test@example.com'
  assert_output "test@example.com"
}
