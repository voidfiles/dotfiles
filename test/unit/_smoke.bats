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

@test "curl stub records and exits 0" {
  make_scratch_home
  install_stubs
  curl -sfL https://example.com
  stub_assert_called curl -sfL https://example.com
}

@test "curl stub responds with fixture when rule matches" {
  make_scratch_home
  install_stubs
  fixture="$BATS_TEST_TMPDIR/body.json"
  printf '{"tag_name":"v9.9.9"}\n' >"$fixture"
  stub_respond curl 'releases/latest' "$fixture"
  run curl -sf https://api.github.com/repos/borksh/bork/releases/latest
  assert_success
  assert_output --partial '"tag_name":"v9.9.9"'
}

@test "git clone stub copies fixture into destination" {
  make_scratch_home
  install_stubs
  dst="$BATS_TEST_TMPDIR/cloned"
  git clone --depth=1 --quiet https://github.com/x/hegelian-dialectic-skill.git "$dst"
  assert_file_exists "$dst/SKILL.md"
}
