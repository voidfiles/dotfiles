#!/usr/bin/env bats

load '../helpers/common'

setup() {
  make_scratch_home
  install_stubs

  export TEST_REPO="$BATS_TEST_TMPDIR/repo"
  mkdir -p "$TEST_REPO/scripts" "$TEST_REPO/skills/example-skill" "$TEST_REPO/config/skills"
  cp "$DOTFILES_REPO_ROOT/scripts/install-skills.sh" "$TEST_REPO/scripts/install-skills.sh"
  chmod +x "$TEST_REPO/scripts/install-skills.sh"

  cat >"$TEST_REPO/skills/example-skill/SKILL.md" <<'EOF'
---
name: example-skill
description: Example skill fixture
---

# Example
EOF
}

_run_install_skills() {
  DOTFILES_DIR="$TEST_REPO" "$TEST_REPO/scripts/install-skills.sh" "$@"
}

@test "installs all local skills to Claude Code and Codex with npx skills" {
  run _run_install_skills
  assert_success

  stub_assert_called npx --yes skills add "$TEST_REPO/skills" --skill '*' --global --agent claude-code --agent codex --yes
}

@test "installs configured external skill sources" {
  printf '# useful UI audit skill\nshadcn/improve\n\n' >"$TEST_REPO/config/skills/sources.txt"

  run _run_install_skills
  assert_success

  stub_assert_called npx --yes skills add shadcn/improve --skill '*' --global --agent claude-code --agent codex --yes
}

@test "installs skill sources passed as arguments after configured sources" {
  printf 'shadcn/improve\n' >"$TEST_REPO/config/skills/sources.txt"

  run _run_install_skills vercel-labs/agent-skills
  assert_success

  stub_assert_called npx --yes skills add shadcn/improve --skill '*' --global --agent claude-code --agent codex --yes
  stub_assert_called npx --yes skills add vercel-labs/agent-skills --skill '*' --global --agent claude-code --agent codex --yes
}

@test "installs skill sources from SKILL_SOURCES env" {
  export SKILL_SOURCES='shadcn/improve vercel-labs/agent-skills'

  run _run_install_skills
  assert_success

  stub_assert_called npx --yes skills add shadcn/improve --skill '*' --global --agent claude-code --agent codex --yes
  stub_assert_called npx --yes skills add vercel-labs/agent-skills --skill '*' --global --agent claude-code --agent codex --yes
}
