#!/usr/bin/env bats

load '../helpers/common'

setup() {
  make_scratch_home
  install_stubs
}

_stub_uname() {
  local output="$1"
  cat >"$DOTFILES_REPO_ROOT/test/stubs/uname" <<EOF
#!/usr/bin/env bash
echo '$output'
EOF
  chmod +x "$DOTFILES_REPO_ROOT/test/stubs/uname"
}

teardown() {
  rm -f "$DOTFILES_REPO_ROOT/test/stubs/uname"
  # Restore apt-get stub if it was deleted in a test
  if [[ ! -f "$DOTFILES_REPO_ROOT/test/stubs/apt-get" ]]; then
    cat >"$DOTFILES_REPO_ROOT/test/stubs/apt-get" <<'EOF'
#!/usr/bin/env bash
printf 'apt-get %s\n' "$*" >>"$STUB_LOG"
exit 0
EOF
    chmod +x "$DOTFILES_REPO_ROOT/test/stubs/apt-get"
  fi
}

@test "ensure_package dispatches to bork brew on Darwin" {
  _stub_uname "Darwin"
  source "$DOTFILES_REPO_ROOT/scripts/util.sh"
  run ensure_package direnv
  assert_success
  stub_assert_called bork 'do' ok brew direnv
}

@test "ensure_package dispatches to bork apt on Linux with apt-get" {
  _stub_uname "Linux"
  source "$DOTFILES_REPO_ROOT/scripts/util.sh"
  run ensure_package direnv
  assert_success
  stub_assert_called bork 'do' ok apt direnv
}

@test "ensure_package errors on unsupported OS" {
  _stub_uname "Plan9"
  rm -f "$DOTFILES_REPO_ROOT/test/stubs/apt-get"
  source "$DOTFILES_REPO_ROOT/scripts/util.sh"
  run ensure_package direnv
  assert_failure
  assert_output --partial 'Unsupported OS'
}
