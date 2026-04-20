#!/usr/bin/env bats

load '../helpers/common'

setup() {
  make_scratch_home
  install_stubs
  export TEST_SKILLS_DIR="$BATS_TEST_TMPDIR/skills"
  mkdir -p "$TEST_SKILLS_DIR"
}

# Build a scratch repo with the script and a symlinked skills dir, then run it.
# REPO_ROOT in the script is derived as SCRIPT_DIR/.., so we mirror that layout.
_run_refresh_in_scratch_repo() {
  local scratch_root="$BATS_TEST_TMPDIR/repo"
  mkdir -p "$scratch_root/scripts"
  cp "$DOTFILES_REPO_ROOT/scripts/refresh-skills.sh" "$scratch_root/scripts/"
  chmod +x "$scratch_root/scripts/refresh-skills.sh"
  ln -s "$TEST_SKILLS_DIR" "$scratch_root/skills"
  "$scratch_root/scripts/refresh-skills.sh"
}

@test "copies listed skills from cloned repo" {
  run _run_refresh_in_scratch_repo
  assert_success
  assert_dir_exists "$TEST_SKILLS_DIR/bgpt-paper-search"
  assert_dir_exists "$TEST_SKILLS_DIR/literature-review"
  assert_dir_exists "$TEST_SKILLS_DIR/paper-lookup"
}

@test "each copied scientific skill contains a SKILL.md" {
  run _run_refresh_in_scratch_repo
  assert_success
  assert_file_exists "$TEST_SKILLS_DIR/bgpt-paper-search/SKILL.md"
  assert_file_exists "$TEST_SKILLS_DIR/literature-review/SKILL.md"
  assert_file_exists "$TEST_SKILLS_DIR/paper-lookup/SKILL.md"
}

@test "rename syntax remote:local copies skill under local name" {
  run _run_refresh_in_scratch_repo
  assert_success
  assert_dir_exists "$TEST_SKILLS_DIR/model-based-thinking"
  assert_file_not_exists "$TEST_SKILLS_DIR/thinking-partner"
}

@test "rename syntax rewrites frontmatter name field" {
  run _run_refresh_in_scratch_repo
  assert_success
  run grep 'name: model-based-thinking' "$TEST_SKILLS_DIR/model-based-thinking/SKILL.md"
  assert_success
}

@test "rename syntax does not leave old frontmatter name" {
  run _run_refresh_in_scratch_repo
  assert_success
  run grep 'name: thinking-partner' "$TEST_SKILLS_DIR/model-based-thinking/SKILL.md"
  assert_failure
}

@test "bare repo url copies repo root as skill named after repo" {
  run _run_refresh_in_scratch_repo
  assert_success
  assert_dir_exists "$TEST_SKILLS_DIR/hegelian-dialectic-skill"
  assert_file_exists "$TEST_SKILLS_DIR/hegelian-dialectic-skill/SKILL.md"
}

@test ".external-skills manifest rebuilt with all copied skill names" {
  run _run_refresh_in_scratch_repo
  assert_success
  manifest="$BATS_TEST_TMPDIR/repo/scripts/.external-skills"
  assert_file_exists "$manifest"
  # 3 scientific-skills + 1 renamed (model-based-thinking) + 1 bare (hegelian-dialectic-skill) = 5
  run grep -c . "$manifest"
  assert_output "5"
}

@test ".external-skills manifest contains renamed local skill name not remote name" {
  run _run_refresh_in_scratch_repo
  assert_success
  manifest="$BATS_TEST_TMPDIR/repo/scripts/.external-skills"
  run grep -x 'model-based-thinking' "$manifest"
  assert_success
  run grep -x 'thinking-partner' "$manifest"
  assert_failure
}

@test "failed clone surfaces as non-zero exit" {
  # Remove the fixture so the git stub returns an error for this repo
  local fixture="$DOTFILES_REPO_ROOT/test/fixtures/git/hegelian-dialectic-skill"
  local backup="$BATS_TEST_TMPDIR/hegelian-dialectic-skill.bak"
  cp -R "$fixture" "$backup"
  rm -rf "$fixture"

  run _run_refresh_in_scratch_repo
  assert_failure

  # Restore fixture so we don't corrupt other tests
  cp -R "$backup" "$fixture"
}
