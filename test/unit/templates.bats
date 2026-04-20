#!/usr/bin/env bats

load '../helpers/common'

@test "gitconfig template renders identically to golden fixture" {
  out="$BATS_TEST_TMPDIR/rendered"
  GIT_EMAIL=test@example.com GIT_NAME=tester envsubst \
    <"$DOTFILES_REPO_ROOT/templates/dot_gitconfig.tmpl" \
    >"$out"
  run diff "$out" "$DOTFILES_REPO_ROOT/test/fixtures/gitconfig_golden.txt"
  assert_success
}

@test "gitconfig template does not leave literal placeholders when vars are empty" {
  out="$BATS_TEST_TMPDIR/rendered"
  GIT_EMAIL= GIT_NAME= envsubst \
    <"$DOTFILES_REPO_ROOT/templates/dot_gitconfig.tmpl" \
    >"$out"
  run grep -F '${GIT_EMAIL}' "$out"
  assert_failure
  run grep -F '${GIT_NAME}' "$out"
  assert_failure
}
