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
