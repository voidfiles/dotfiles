#!/usr/bin/env bats

load '../helpers/common'

@test "helper loads and DOTFILES_REPO_ROOT resolves" {
  assert [ -n "$DOTFILES_REPO_ROOT" ]
  assert_file_exists "$DOTFILES_REPO_ROOT/justfile"
}

@test "scratch home isolates HOME to BATS_TEST_TMPDIR" {
  make_scratch_home
  assert_equal "$HOME" "$BATS_TEST_TMPDIR/home"
  assert_dir_exists "$HOME/.local/share/dotfiles"
  assert_equal "$(readlink "$HOME/.local/share/dotfiles")" "$DOTFILES_REPO_ROOT"
}

@test "stub records its invocation" {
  make_scratch_home
  install_stubs
  bork do ok brew foo
  stub_assert_called bork do ok brew foo
}

@test "stub_assert_not_called passes when cmd never ran" {
  make_scratch_home
  install_stubs
  bork foo
  stub_assert_not_called brew
}
