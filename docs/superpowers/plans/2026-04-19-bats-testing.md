# Bats Testing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a two-tier bats testing system (fast unit + full-fidelity integration) to this dotfiles repo. Unit tests run in seconds on the host using stubs and scratch `$HOME`. Integration tests run the real scripts against real package managers and real network inside Lima (Linux) and tart (macOS) VMs locally, and directly on GHA runners in CI. The same `.bats` files execute in every envelope.

**Architecture:** Vendor `bats-core` and its assertion libraries as git submodules under `test/bats/`. A single `test/run.sh` entry point runs either tier and is invoked identically from the host shell, from inside Lima, from a tart SSH session, and from GitHub Actions. Unit tests prepend `test/stubs/` to `PATH` to neutralize external commands; integration tests execute the real scripts and assert post-install state. An `integration-matrix.sh` orchestrator runs the 8-cell matrix (`USE_1_PASSWORD × SHELL_TO_USE × {fresh, rerun}`) per platform.

**Tech Stack:** bash, bats-core (1.11+), bats-support, bats-assert, bats-file, Lima (vz backend, Apple Virtualization framework), tart (macOS VMs on Apple Silicon), GitHub Actions (`ubuntu-latest`, `macos-latest`), `just` for task wiring.

**Spec:** See `docs/superpowers/specs/2026-04-19-bats-testing-design.md` for the full design and rationale. This plan implements it exactly.

---

## Conventions used throughout this plan

- **Working directory:** all relative paths are from the repo root `/Users/alex/.local/share/dotfiles`.
- **Commit style:** one conceptual change per commit. Commit messages follow `<area>: <summary>` (e.g. `test: add scratch home helper`).
- **Verification before commit:** every task ends with running the relevant tests and asserting they pass. Never commit red tests.
- **Shebangs:** all scripts start with `#!/usr/bin/env bash` and `set -euo pipefail` unless they are sourced (helper libs use `set -uo pipefail` only if safe).
- **chmod:** every new executable script gets `chmod +x` staged with it.
- **No `any` / `-u` sloppiness:** helpers avoid unset-var hazards by initializing defaults.

---

## Task 1: Bootstrap the test directory and vendor bats

**Files:**
- Create: `test/bats/` (empty dir, will hold submodules)
- Create: `test/helpers/`, `test/stubs/`, `test/fixtures/`, `test/unit/`, `test/integration/`, `test/lima/`, `test/tart/` (empty dirs with `.gitkeep` where needed)
- Create: `.gitmodules`
- Create: `test/bats/.gitkeep` (optional, not needed because submodules populate it)

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p test/{helpers,stubs,fixtures/{git,local_config},unit,integration,lima,tart}
touch test/helpers/.gitkeep test/stubs/.gitkeep test/fixtures/git/.gitkeep test/fixtures/local_config/.gitkeep test/unit/.gitkeep test/integration/.gitkeep test/lima/.gitkeep test/tart/.gitkeep
```

- [ ] **Step 2: Add bats-core as a submodule pinned to v1.11.0**

```bash
git submodule add -b master https://github.com/bats-core/bats-core.git test/bats/bats-core
cd test/bats/bats-core && git checkout v1.11.0 && cd -
```

- [ ] **Step 3: Add bats-support, bats-assert, bats-file submodules**

```bash
git submodule add https://github.com/bats-core/bats-support.git test/bats/bats-support
cd test/bats/bats-support && git checkout v0.3.0 && cd -

git submodule add https://github.com/bats-core/bats-assert.git test/bats/bats-assert
cd test/bats/bats-assert && git checkout v2.1.0 && cd -

git submodule add https://github.com/bats-core/bats-file.git test/bats/bats-file
cd test/bats/bats-file && git checkout v0.4.0 && cd -
```

- [ ] **Step 4: Verify bats runs**

Run: `test/bats/bats-core/bin/bats --version`
Expected: prints `Bats 1.11.0` (or exact pinned version).

- [ ] **Step 5: Remove the `test/bats/.gitkeep` placeholders that submodules made redundant**

```bash
# Only remove if it exists; submodules already populate the dir
rm -f test/bats/.gitkeep
```

- [ ] **Step 6: Commit**

```bash
git add .gitmodules test/bats test/helpers test/stubs test/fixtures test/unit test/integration test/lima test/tart
git commit -m "test: bootstrap test directory and vendor bats submodules"
```

---

## Task 2: Write the common test helper

**Files:**
- Create: `test/helpers/common.bash`

This is the helper loaded by every `.bats` file. It loads the bats assertion libraries and exports `DOTFILES_REPO_ROOT`.

- [ ] **Step 1: Write the helper**

```bash
# test/helpers/common.bash
# shellcheck shell=bash

load '../bats/bats-support/load'
load '../bats/bats-assert/load'
load '../bats/bats-file/load'

DOTFILES_REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
export DOTFILES_REPO_ROOT
```

- [ ] **Step 2: Write a smoke test that loads the helper and asserts nothing (just exercises the load path)**

Create `test/unit/_smoke.bats`:

```bash
#!/usr/bin/env bats

load '../helpers/common'

@test "helper loads and DOTFILES_REPO_ROOT resolves" {
  assert [ -n "$DOTFILES_REPO_ROOT" ]
  assert_file_exists "$DOTFILES_REPO_ROOT/justfile"
}
```

- [ ] **Step 3: Run the smoke test**

Run: `test/bats/bats-core/bin/bats test/unit/_smoke.bats`
Expected: 1 test passes.

- [ ] **Step 4: Commit**

```bash
git add test/helpers/common.bash test/unit/_smoke.bats
git commit -m "test: add common bats helper and smoke test"
```

---

## Task 3: Write the scratch-home helper

**Files:**
- Create: `test/helpers/scratch.bash`

Creates a disposable `$HOME` under `$BATS_TEST_TMPDIR` for each test. Symlinks the repo into `$HOME/.local/share/dotfiles` so `DOTFILES_DIR` resolves correctly without copying.

- [ ] **Step 1: Write the helper**

```bash
# test/helpers/scratch.bash
# shellcheck shell=bash

make_scratch_home() {
  local home_dir="$BATS_TEST_TMPDIR/home"
  mkdir -p "$home_dir/.local/share"
  ln -snf "$DOTFILES_REPO_ROOT" "$home_dir/.local/share/dotfiles"
  export HOME="$home_dir"
  export DOTFILES_DIR="$home_dir/.local/share/dotfiles"
}

teardown_scratch_home() {
  # BATS_TEST_TMPDIR is auto-cleaned by bats; this is a no-op today but
  # gives future tests a place to hook cleanup.
  :
}
```

- [ ] **Step 2: Load scratch.bash from common.bash**

Edit `test/helpers/common.bash` to append `load './scratch'` after the assert loads.

```bash
# test/helpers/common.bash (final form)
load '../bats/bats-support/load'
load '../bats/bats-assert/load'
load '../bats/bats-file/load'
load './scratch'

DOTFILES_REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
export DOTFILES_REPO_ROOT
```

- [ ] **Step 3: Write a test that proves scratch-home works**

Add to `test/unit/_smoke.bats`:

```bash
@test "scratch home isolates HOME to BATS_TEST_TMPDIR" {
  make_scratch_home
  assert_equal "$HOME" "$BATS_TEST_TMPDIR/home"
  assert_dir_exists "$HOME/.local/share/dotfiles"
  assert_equal "$(readlink "$HOME/.local/share/dotfiles")" "$DOTFILES_REPO_ROOT"
}
```

- [ ] **Step 4: Run tests**

Run: `test/bats/bats-core/bin/bats test/unit/_smoke.bats`
Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add test/helpers/scratch.bash test/helpers/common.bash test/unit/_smoke.bats
git commit -m "test: add scratch home helper"
```

---

## Task 4: Write the stubs helper and first stubs

**Files:**
- Create: `test/helpers/stubs.bash`
- Create: `test/stubs/bork`
- Create: `test/stubs/brew`
- Create: `test/stubs/apt-get`
- Create: `test/stubs/chsh`

Stubs prepend to `PATH` and each one appends its invocation to `$STUB_LOG`.

- [ ] **Step 1: Write `stubs.bash`**

```bash
# test/helpers/stubs.bash
# shellcheck shell=bash

install_stubs() {
  export STUB_LOG="$BATS_TEST_TMPDIR/stub.log"
  : > "$STUB_LOG"
  export PATH="$DOTFILES_REPO_ROOT/test/stubs:$PATH"
}

stub_assert_called() {
  local cmd="$1"
  shift
  local expected="$cmd $*"
  if ! grep -Fxq "$expected" "$STUB_LOG"; then
    echo "expected stub log to contain: $expected" >&2
    echo "actual stub log:" >&2
    cat "$STUB_LOG" >&2
    return 1
  fi
}

stub_assert_not_called() {
  local cmd="$1"
  if grep -E "^${cmd}( |$)" "$STUB_LOG" >/dev/null; then
    echo "did not expect stub log to contain calls to: $cmd" >&2
    cat "$STUB_LOG" >&2
    return 1
  fi
}

# Arrange a stub to write a specific response to stdout on a given arg match.
# Usage: stub_respond <cmd> <match-regex> <fixture-file>
stub_respond() {
  local cmd="$1" match="$2" fixture="$3"
  export "STUB_RESPOND_${cmd//[^A-Za-z0-9]/_}=${match}::${fixture}"
}
```

- [ ] **Step 2: Load stubs.bash from common.bash**

Edit `test/helpers/common.bash` to append `load './stubs'`.

```bash
# test/helpers/common.bash (final form)
load '../bats/bats-support/load'
load '../bats/bats-assert/load'
load '../bats/bats-file/load'
load './scratch'
load './stubs'

DOTFILES_REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
export DOTFILES_REPO_ROOT
```

- [ ] **Step 3: Write the record-and-exit-0 stubs**

Each stub is a small bash script that logs its invocation and exits 0.

```bash
# test/stubs/bork
#!/usr/bin/env bash
printf 'bork %s\n' "$*" >>"$STUB_LOG"
exit 0
```

```bash
# test/stubs/brew
#!/usr/bin/env bash
printf 'brew %s\n' "$*" >>"$STUB_LOG"
exit 0
```

```bash
# test/stubs/apt-get
#!/usr/bin/env bash
printf 'apt-get %s\n' "$*" >>"$STUB_LOG"
exit 0
```

```bash
# test/stubs/chsh
#!/usr/bin/env bash
printf 'chsh %s\n' "$*" >>"$STUB_LOG"
exit 0
```

Make them executable:

```bash
chmod +x test/stubs/bork test/stubs/brew test/stubs/apt-get test/stubs/chsh
```

- [ ] **Step 4: Write a test that exercises a stub**

Add to `test/unit/_smoke.bats`:

```bash
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
```

- [ ] **Step 5: Run tests**

Run: `test/bats/bats-core/bin/bats test/unit/_smoke.bats`
Expected: 4 tests pass.

- [ ] **Step 6: Commit**

```bash
git add test/helpers/stubs.bash test/helpers/common.bash test/stubs/{bork,brew,apt-get,chsh}
git commit -m "test: add stubs helper and record-and-exit-0 stubs"
```

---

## Task 5: Add curl and git stubs with fixture support

**Files:**
- Create: `test/stubs/curl`
- Create: `test/stubs/git`
- Create: `test/stubs/sudo`
- Create: `test/fixtures/git/thinking-partner/` (minimal fake skill repo)
- Create: `test/fixtures/git/hegelian-dialectic-skill/` (minimal fake skill repo)

The `curl` stub optionally responds with a fixture file when a stub_respond rule matches. The `git` stub, on `clone <url> <dst>`, copies from `test/fixtures/git/<basename-minus-.git>/` into `<dst>`.

- [ ] **Step 1: Write the `curl` stub**

```bash
# test/stubs/curl
#!/usr/bin/env bash
set -uo pipefail
args="$*"
printf 'curl %s\n' "$args" >>"$STUB_LOG"

# Look through env for STUB_RESPOND_curl_* rules; they take the form "match::fixture-path".
for var in $(compgen -v | grep '^STUB_RESPOND_curl_' || true); do
  rule="${!var}"
  match="${rule%%::*}"
  fixture="${rule##*::}"
  if [[ "$args" =~ $match ]]; then
    cat "$fixture"
    exit 0
  fi
done
exit 0
```

- [ ] **Step 2: Write the `git` stub**

```bash
# test/stubs/git
#!/usr/bin/env bash
set -uo pipefail
printf 'git %s\n' "$*" >>"$STUB_LOG"

sub="${1:-}"
case "$sub" in
  clone)
    # Parse: git clone [--depth=N] [--quiet] [--branch X] <url> <dst>
    # Accept any leading flags, then url and dst.
    shift
    while [[ "${1:-}" == --* ]] || [[ "${1:-}" == -b ]] || [[ "${1:-}" == --branch ]]; do
      if [[ "${1:-}" == -b || "${1:-}" == --branch ]]; then
        shift 2
      else
        shift 1
      fi
    done
    url="${1:-}"
    dst="${2:-}"
    if [[ -z "$url" || -z "$dst" ]]; then
      echo "stub git: could not parse url/dst from: $*" >&2
      exit 2
    fi
    name="$(basename "$url" .git)"
    src="${DOTFILES_REPO_ROOT}/test/fixtures/git/${name}"
    if [[ ! -d "$src" ]]; then
      echo "stub git: no fixture for $name at $src" >&2
      exit 1
    fi
    mkdir -p "$(dirname "$dst")"
    cp -R "$src" "$dst"
    exit 0
    ;;
  *)
    # Let other subcommands (rev-parse, etc.) fall through to real git if ever needed.
    # For now, just log and exit 0.
    exit 0
    ;;
esac
```

- [ ] **Step 3: Write the `sudo` stub**

```bash
# test/stubs/sudo
#!/usr/bin/env bash
printf 'sudo %s\n' "$*" >>"$STUB_LOG"
# Execute the command without sudo so side effects still happen inside $BATS_TEST_TMPDIR.
exec "$@"
```

- [ ] **Step 4: Make them executable**

```bash
chmod +x test/stubs/{curl,git,sudo}
```

- [ ] **Step 5: Build minimal skill fixtures**

```bash
mkdir -p test/fixtures/git/thinking-partner test/fixtures/git/hegelian-dialectic-skill
```

Create `test/fixtures/git/thinking-partner/skills/thinking-partner/SKILL.md`:

```markdown
---
name: thinking-partner
description: Fixture thinking partner skill
---

Fixture content.
```

Create `test/fixtures/git/hegelian-dialectic-skill/SKILL.md`:

```markdown
---
name: hegelian-dialectic-skill
description: Fixture hegelian skill
---

Fixture content.
```

- [ ] **Step 6: Write tests for the new stubs**

Add to `test/unit/_smoke.bats`:

```bash
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
```

- [ ] **Step 7: Run tests**

Run: `test/bats/bats-core/bin/bats test/unit/_smoke.bats`
Expected: 7 tests pass.

- [ ] **Step 8: Commit**

```bash
git add test/stubs/{curl,git,sudo} test/fixtures/git test/unit/_smoke.bats
git commit -m "test: add curl/git/sudo stubs and skill fixtures"
```

---

## Task 6: Write `test/run.sh` entry point (unit tier only, for now)

**Files:**
- Create: `test/run.sh`

Single entry point. For unit tier it just runs bats on `test/unit`. The integration branch will be filled in later and is stubbed out to fail loudly for now.

- [ ] **Step 1: Write `test/run.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BATS="$ROOT/test/bats/bats-core/bin/bats"

tier="${1:?usage: run.sh unit|integration}"

case "$tier" in
  unit)
    exec "$BATS" "$ROOT/test/unit"
    ;;
  integration)
    exec "$ROOT/test/helpers/integration-matrix.sh"
    ;;
  *)
    echo "run.sh: unknown tier: $tier" >&2
    exit 2
    ;;
esac
```

- [ ] **Step 2: Make executable**

```bash
chmod +x test/run.sh
```

- [ ] **Step 3: Verify it runs the existing smoke tests**

Run: `test/run.sh unit`
Expected: the 7 smoke tests all pass.

- [ ] **Step 4: Delete the smoke test file — it was scaffolding, not a real test**

```bash
rm test/unit/_smoke.bats
```

The next tasks add real tests; the smoke file served its purpose of proving the harness works.

- [ ] **Step 5: Commit**

```bash
git add test/run.sh
git rm test/unit/_smoke.bats
git commit -m "test: add run.sh entry point and drop smoke scaffolding"
```

---

## Task 7: Unit test `config/config.sh` — platform and shell flags

**Files:**
- Create: `test/unit/config.bats`

- [ ] **Step 1: Write the failing test file**

```bash
#!/usr/bin/env bats

load '../helpers/common'

setup() {
  make_scratch_home
}

# Helper: run config.sh in a subshell with a specific uname stub and shell env,
# print the flag the test cares about.
_read_flag() {
  local flag="$1"; shift
  bash -c "$*; source '$DOTFILES_REPO_ROOT/config/config.sh' >/dev/null 2>&1; printf '%s' \"\${$flag}\""
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
  # We can't easily change `uname` output from a subshell without a stub on PATH,
  # so we test the real environment's detection.
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
```

- [ ] **Step 2: Run the tests, verify they pass**

Run: `test/run.sh unit`
Expected: 7 tests pass.

If any fail, the failure is a real bug in `config/config.sh`. Fix it; the spec says `config.sh` should already behave this way.

- [ ] **Step 3: Commit**

```bash
git add test/unit/config.bats
git commit -m "test: unit tests for config.sh flags and defaults"
```

---

## Task 8: Unit test `scripts/util.sh::ensure_package`

**Files:**
- Create: `test/unit/util_ensure_package.bats`

- [ ] **Step 1: Write the test file**

```bash
#!/usr/bin/env bats

load '../helpers/common'

setup() {
  make_scratch_home
  install_stubs
}

# Override uname in a bash-function sense: we provide a stub named `uname` on PATH.
# But we don't want to keep that stub for every test, so we write it per-test.
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
}

@test "ensure_package dispatches to bork brew on Darwin" {
  _stub_uname "Darwin"
  # shellcheck disable=SC1091
  source "$DOTFILES_REPO_ROOT/scripts/util.sh"
  run ensure_package direnv
  assert_success
  stub_assert_called bork 'do' ok brew direnv
}

@test "ensure_package dispatches to bork apt on Linux with apt-get" {
  _stub_uname "Linux"
  # shellcheck disable=SC1091
  source "$DOTFILES_REPO_ROOT/scripts/util.sh"
  run ensure_package direnv
  assert_success
  stub_assert_called bork 'do' ok apt direnv
}

@test "ensure_package errors on unsupported OS" {
  _stub_uname "Plan9"
  # Remove apt-get stub for this test so the "neither" branch fires.
  rm "$DOTFILES_REPO_ROOT/test/stubs/apt-get"
  # shellcheck disable=SC1091
  source "$DOTFILES_REPO_ROOT/scripts/util.sh"
  run ensure_package direnv
  assert_failure
  assert_output --partial 'Unsupported OS'
  # Restore the stub for other tests (it's owned by task 4, not this test).
  cat >"$DOTFILES_REPO_ROOT/test/stubs/apt-get" <<'EOF'
#!/usr/bin/env bash
printf 'apt-get %s\n' "$*" >>"$STUB_LOG"
exit 0
EOF
  chmod +x "$DOTFILES_REPO_ROOT/test/stubs/apt-get"
}
```

- [ ] **Step 2: Run the tests**

Run: `test/run.sh unit`
Expected: 10 tests total pass (3 new + 7 from task 7).

- [ ] **Step 3: Commit**

```bash
git add test/unit/util_ensure_package.bats
git commit -m "test: unit tests for ensure_package dispatch"
```

---

## Task 9: Unit test `templates/dot_gitconfig.tmpl` rendering

**Files:**
- Create: `test/unit/templates.bats`
- Create: `test/fixtures/gitconfig_golden.txt`

- [ ] **Step 1: Generate the golden fixture by running the template once**

```bash
GIT_EMAIL=test@example.com GIT_NAME=tester envsubst < templates/dot_gitconfig.tmpl > test/fixtures/gitconfig_golden.txt
```

Inspect it; confirm it looks right. If `dot_gitconfig.tmpl` expects additional vars, set them too.

- [ ] **Step 2: Write the test file**

```bash
#!/usr/bin/env bats

load '../helpers/common'

@test "gitconfig template renders against golden fixture" {
  out="$BATS_TEST_TMPDIR/rendered"
  GIT_EMAIL=test@example.com GIT_NAME=tester envsubst \
    <"$DOTFILES_REPO_ROOT/templates/dot_gitconfig.tmpl" \
    >"$out"
  assert_files_equal "$out" "$DOTFILES_REPO_ROOT/test/fixtures/gitconfig_golden.txt"
}

@test "gitconfig template does not leave literal \${VAR} when vars are empty" {
  out="$BATS_TEST_TMPDIR/rendered"
  GIT_EMAIL= GIT_NAME= envsubst \
    <"$DOTFILES_REPO_ROOT/templates/dot_gitconfig.tmpl" \
    >"$out"
  refute_file_contains "$out" '${GIT_EMAIL}'
  refute_file_contains "$out" '${GIT_NAME}'
}
```

Note: `bats-file` provides `assert_files_equal` and `refute_file_contains` — confirm they exist in the pinned version; if not, substitute with `diff` / `grep -v`.

- [ ] **Step 3: Run the tests**

Run: `test/run.sh unit`
Expected: 12 tests total pass (2 new).

- [ ] **Step 4: Commit**

```bash
git add test/unit/templates.bats test/fixtures/gitconfig_golden.txt
git commit -m "test: unit tests for gitconfig template rendering"
```

---

## Task 10: Unit test `scripts/refresh-skills.sh`

**Files:**
- Create: `test/unit/refresh_skills.bats`
- Create: `test/fixtures/git/claude-scientific-skills/scientific-skills/bgpt-paper-search/SKILL.md`
- Create: `test/fixtures/git/claude-scientific-skills/scientific-skills/literature-review/SKILL.md`
- Create: `test/fixtures/git/claude-scientific-skills/scientific-skills/paper-lookup/SKILL.md`
- Create: `test/fixtures/git/thinking-partner/skills/thinking-partner/SKILL.md` (likely already exists from task 5; verify)

The `refresh-skills.sh` script iterates `SKILL_SOURCES`, clones each repo, copies skill subdirs to `$SKILLS_DIR`, optionally renames them and rewrites `name:` in the frontmatter. Tests exercise each branch.

- [ ] **Step 1: Extend fixtures so every SKILL_SOURCES entry has something to copy**

Look at `scripts/refresh-skills.sh` — the actual `SKILL_SOURCES` entries are:

```
https://github.com/K-Dense-AI/claude-scientific-skills.git|scientific-skills|bgpt-paper-search literature-review paper-lookup
https://github.com/mattnowdev/thinking-partner.git|skills|thinking-partner:model-based-thinking
https://github.com/KyleAMathews/hegelian-dialectic-skill.git|
```

Create the fixture tree to match:

```bash
mkdir -p test/fixtures/git/claude-scientific-skills/scientific-skills/{bgpt-paper-search,literature-review,paper-lookup}
for s in bgpt-paper-search literature-review paper-lookup; do
  cat >"test/fixtures/git/claude-scientific-skills/scientific-skills/$s/SKILL.md" <<EOF
---
name: $s
description: Fixture for $s
---
Fixture content.
EOF
done

mkdir -p test/fixtures/git/thinking-partner/skills/thinking-partner
cat >test/fixtures/git/thinking-partner/skills/thinking-partner/SKILL.md <<'EOF'
---
name: thinking-partner
description: Fixture thinking-partner
---
Fixture content.
EOF

# hegelian-dialectic-skill is the bare-repo case; its fixture from task 5 is enough.
```

- [ ] **Step 2: Write the test file**

```bash
#!/usr/bin/env bats

load '../helpers/common'

setup() {
  make_scratch_home
  install_stubs
  export TEST_SKILLS_DIR="$BATS_TEST_TMPDIR/skills"
  mkdir -p "$TEST_SKILLS_DIR"
}

# refresh-skills.sh hardcodes SKILLS_DIR="$REPO_ROOT/skills", so we redirect by
# running the script from a temp copy of the repo root whose `skills` subdir is
# our scratch dir.
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

@test "rename syntax remote:local copies and rewrites frontmatter" {
  run _run_refresh_in_scratch_repo
  assert_success
  assert_dir_exists "$TEST_SKILLS_DIR/model-based-thinking"
  assert_file_not_exists "$TEST_SKILLS_DIR/thinking-partner"
  run grep -l '^name: model-based-thinking$' "$TEST_SKILLS_DIR/model-based-thinking/SKILL.md"
  assert_success
}

@test "bare repo url copies repo root as skill named after repo" {
  run _run_refresh_in_scratch_repo
  assert_success
  assert_dir_exists "$TEST_SKILLS_DIR/hegelian-dialectic-skill"
  assert_file_exists "$TEST_SKILLS_DIR/hegelian-dialectic-skill/SKILL.md"
}

@test ".external-skills manifest rebuilt with all copied names" {
  run _run_refresh_in_scratch_repo
  assert_success
  manifest="$BATS_TEST_TMPDIR/repo/scripts/.external-skills"
  assert_file_exists "$manifest"
  run grep -c . "$manifest"
  # 3 scientific + 1 rename + 1 bare = 5 entries
  assert_output "5"
}

@test "failed clone surfaces as non-zero exit" {
  # Point the git stub at a non-existent fixture by deleting one.
  rm -rf "$DOTFILES_REPO_ROOT/test/fixtures/git/hegelian-dialectic-skill"
  run _run_refresh_in_scratch_repo
  assert_failure
  # Restore fixture for downstream tests.
  mkdir -p "$DOTFILES_REPO_ROOT/test/fixtures/git/hegelian-dialectic-skill"
  cat >"$DOTFILES_REPO_ROOT/test/fixtures/git/hegelian-dialectic-skill/SKILL.md" <<'EOF'
---
name: hegelian-dialectic-skill
description: Fixture hegelian skill
---

Fixture content.
EOF
}
```

- [ ] **Step 3: Run the tests**

Run: `test/run.sh unit`
Expected: 17 total (5 new).

Note: the `refresh-skills.sh` script uses `sed -i ''` (BSD syntax) which works on Mac but breaks on Linux. If the test fails on Linux due to this, flag it as a real bug to the user rather than silently patching — it's a portability issue the spec implies exists in production code.

- [ ] **Step 4: Commit**

```bash
git add test/unit/refresh_skills.bats test/fixtures/git/claude-scientific-skills test/fixtures/git/thinking-partner
git commit -m "test: unit tests for refresh-skills.sh"
```

---

## Task 11: Unit test `config/router.sh` loading

**Files:**
- Create: `test/unit/router.bats`

- [ ] **Step 1: Write the test file**

`router.sh` sources `config.sh` then every `config/shell/*.sh`. We assert a few side effects of those shell files are present in the environment after sourcing.

```bash
#!/usr/bin/env bats

load '../helpers/common'

setup() {
  make_scratch_home
}

@test "router sources config.sh and exports platform flags" {
  # shellcheck disable=SC1091
  run bash -c "source '$DOTFILES_REPO_ROOT/config/router.sh'; printf '%s' \"\$IS_DARWIN\""
  assert_success
  # On either platform, IS_DARWIN is set to 0 or 1 (not unset).
  assert_output --regexp '^[01]$'
}

@test "router sources every config/shell/*.sh in name order" {
  # Make each shell/*.sh log its name to a marker file, then assert the order.
  marker="$BATS_TEST_TMPDIR/marker.log"
  export MARKER_LOG="$marker"

  # Create a scratch overlay: copy shell scripts, prepend a marker echo.
  tmp_shell="$BATS_TEST_TMPDIR/shell"
  mkdir -p "$tmp_shell"
  for src in "$DOTFILES_REPO_ROOT"/config/shell/*.sh; do
    name="$(basename "$src")"
    {
      echo "echo $name >> \"$MARKER_LOG\""
      cat "$src"
    } >"$tmp_shell/$name"
  done

  # Build a router that sources the overlay instead of the real shell dir.
  tmp_router="$BATS_TEST_TMPDIR/router.sh"
  cat >"$tmp_router" <<EOF
source "$DOTFILES_REPO_ROOT/config/config.sh"
for f in "$tmp_shell/"*.sh; do [ -r "\$f" ] && . "\$f"; done
EOF

  run bash -c "source '$tmp_router'; cat \"$marker\""
  assert_success
  # Order should be sorted: 00-omz.sh, 01-ssh.sh, 10-paths.sh, 20-tools.sh, 90-aliases.sh
  assert_line --index 0 '00-omz.sh'
  assert_line --index 1 '01-ssh.sh'
  assert_line --index 2 '10-paths.sh'
  assert_line --index 3 '20-tools.sh'
  assert_line --index 4 '90-aliases.sh'
}
```

- [ ] **Step 2: Run the tests**

Run: `test/run.sh unit`
Expected: 19 total (2 new).

- [ ] **Step 3: Commit**

```bash
git add test/unit/router.bats
git commit -m "test: unit tests for router.sh load order"
```

---

## Task 12: Unit test `scripts/init.sh` idempotency

**Files:**
- Create: `test/unit/idempotency.bats`

This is the high-value one. Run `init.sh` twice with all external commands stubbed and assert nothing drifts.

- [ ] **Step 1: Write the test file**

```bash
#!/usr/bin/env bats

load '../helpers/common'

setup() {
  make_scratch_home
  install_stubs
  # stub `uname` for deterministic platform selection
  cat >"$DOTFILES_REPO_ROOT/test/stubs/uname" <<'EOF'
#!/usr/bin/env bash
echo 'Linux'
EOF
  chmod +x "$DOTFILES_REPO_ROOT/test/stubs/uname"

  # stub `dpkg` used by the 1Password path
  cat >"$DOTFILES_REPO_ROOT/test/stubs/dpkg" <<'EOF'
#!/usr/bin/env bash
printf 'dpkg %s\n' "$*" >>"$STUB_LOG"
[[ "$*" == "--print-architecture" ]] && echo "amd64"
exit 0
EOF
  chmod +x "$DOTFILES_REPO_ROOT/test/stubs/dpkg"

  # stub `gpg` for the keyring step
  cat >"$DOTFILES_REPO_ROOT/test/stubs/gpg" <<'EOF'
#!/usr/bin/env bash
printf 'gpg %s\n' "$*" >>"$STUB_LOG"
exit 0
EOF
  chmod +x "$DOTFILES_REPO_ROOT/test/stubs/gpg"

  # stub `tee`, `command`, and `sh` are standard; leave them real

  # Redirect privileged paths the script writes to into $BATS_TEST_TMPDIR
  # by setting a KEYRING_DIR / APT_LIST_DIR that the script respects? No —
  # init.sh hardcodes those paths. So use a sudo stub that rewrites the
  # target path under $BATS_TEST_TMPDIR. Simplest: stub sudo to exec without
  # sudo (task 5 stub), and rely on the paths being writable because we're
  # inside a scratch where we mkdir them.
  mkdir -p "$BATS_TEST_TMPDIR/usr/share/keyrings" "$BATS_TEST_TMPDIR/etc/apt/sources.list.d"
}

_run_init() {
  HOME="$HOME" DOTFILES_DIR="$DOTFILES_DIR" bash "$DOTFILES_DIR/scripts/init.sh"
}

@test "init.sh is idempotent: router line added exactly once after two runs" {
  SHELL_TO_USE=zsh USE_1_PASSWORD=0 run _run_init
  assert_success
  SHELL_TO_USE=zsh USE_1_PASSWORD=0 run _run_init
  assert_success
  router_line='source "$HOME/.local/share/dotfiles/config/router.sh"'
  run grep -cF "$router_line" "$HOME/.zshrc"
  assert_output "1"
}

@test "init.sh renders gitconfig identically on two runs" {
  SHELL_TO_USE=zsh USE_1_PASSWORD=0 GIT_EMAIL=a@b.c GIT_NAME=ab run _run_init
  assert_success
  first="$(cat "$HOME/.gitconfig")"
  SHELL_TO_USE=zsh USE_1_PASSWORD=0 GIT_EMAIL=a@b.c GIT_NAME=ab run _run_init
  assert_success
  second="$(cat "$HOME/.gitconfig")"
  assert_equal "$first" "$second"
}

@test "init.sh copies Claude config files verbatim" {
  SHELL_TO_USE=zsh USE_1_PASSWORD=0 run _run_init
  assert_success
  assert_files_equal "$HOME/.claude/settings.json" "$DOTFILES_DIR/config/claude/settings.json"
  assert_files_equal "$HOME/.claude/CLAUDE.md" "$DOTFILES_DIR/config/claude/CLAUDE.md"
}

teardown() {
  rm -f "$DOTFILES_REPO_ROOT/test/stubs/uname"
  rm -f "$DOTFILES_REPO_ROOT/test/stubs/dpkg"
  rm -f "$DOTFILES_REPO_ROOT/test/stubs/gpg"
}
```

- [ ] **Step 2: Run the tests**

Run: `test/run.sh unit`
Expected: 22 total (3 new).

If tests fail because `init.sh` branches on something unexpected, investigate the real code path. Do not bandaid — fix `init.sh` if the test reveals a real bug, or fix the test if our understanding was wrong.

- [ ] **Step 3: Commit**

```bash
git add test/unit/idempotency.bats
git commit -m "test: unit tests for init.sh idempotency"
```

---

## Task 13: Wire unit tier into justfile

**Files:**
- Modify: `justfile`

- [ ] **Step 1: Add recipes**

Edit `justfile` so it reads (preserving existing recipes):

```make
set shell := ["bash", "scripts/just-shell.sh"]

export PATH := justfile_directory() / "vendor/bork/bin" + ":" + env_var("PATH")

# Show available recipes
default:
    @just --list

update:
    scripts/update.sh

test: test-unit

test-unit:
    test/run.sh unit
```

- [ ] **Step 2: Verify `just test` works**

Run: `just test`
Expected: 22 unit tests pass.

- [ ] **Step 3: Commit**

```bash
git add justfile
git commit -m "test: wire unit tier into justfile"
```

---

## Task 14: Add GitHub Actions workflow for unit tier

**Files:**
- Create: `.github/workflows/tests.yml`

Ship the unit tier in CI first. Integration comes in later tasks — this lets us validate the CI plumbing with fast tests before adding slow ones.

- [ ] **Step 1: Create the workflow**

```yaml
# .github/workflows/tests.yml
name: tests
on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

jobs:
  unit:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - run: test/run.sh unit
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/tests.yml
git commit -m "ci: run unit tier on ubuntu-latest and macos-latest"
```

- [ ] **Step 3: Push the branch (if the user asks) and watch the run**

This is a read-only check for the user to do. Do NOT push without explicit authorization from the user.

---

## Task 15: Write integration helpers

**Files:**
- Create: `test/helpers/integration.bash`

This helper is loaded by integration `.bats` files (not unit). It provides `assert_safe_home` (the destructive-ops guardrail) and the `reset_scratch_home` function called between matrix cells.

- [ ] **Step 1: Write the helper**

```bash
# test/helpers/integration.bash
# shellcheck shell=bash

assert_safe_home() {
  if [[ "${ALLOW_DESTRUCTIVE:-0}" == "1" ]]; then
    return 0
  fi
  case "$HOME" in
    /tmp/*|/private/tmp/*|/home/lima*|/Users/lima*|"$BATS_TEST_TMPDIR"*)
      return 0
      ;;
    *)
      echo "integration test refusing to run against HOME=$HOME" >&2
      echo "set ALLOW_DESTRUCTIVE=1 to override (CI does this)" >&2
      return 1
      ;;
  esac
}

# Wipe every file init.sh / update.sh touches in $HOME so the next cell starts clean.
# Also wipes the 1Password apt source on Linux.
reset_scratch_home() {
  assert_safe_home || return 1

  rm -rf \
    "$HOME/.local/share/dotfiles" \
    "$HOME/.gitconfig" \
    "$HOME/.zshrc" \
    "$HOME/.bashrc" \
    "$HOME/.claude" \
    "$HOME/.oh-my-zsh" \
    "$HOME/.local/bin/uv" \
    "$HOME/.local/bin/claude"

  if [[ "$(uname)" == "Linux" ]]; then
    sudo rm -rf \
      /usr/share/keyrings/1password-archive-keyring.gpg \
      /etc/apt/sources.list.d/1password.list
  else
    # macOS: if 1password-cli cask is installed from a previous cell, uninstall so
    # the next cell exercises the real install path.
    if command -v brew >/dev/null 2>&1 && brew list --cask 1password-cli >/dev/null 2>&1; then
      brew uninstall --cask 1password-cli
    fi
  fi

  # Copy the repo (mounted inside Lima at /workspace/dotfiles, checked out directly in GHA)
  # into $HOME/.local/share/dotfiles so init.sh finds it and skips the clone.
  local src="${REPO_SRC:-$DOTFILES_REPO_ROOT}"
  mkdir -p "$HOME/.local/share"
  cp -R "$src" "$HOME/.local/share/dotfiles"
}
```

- [ ] **Step 2: Commit (no test yet; it'll be covered by the integration suite in task 17)**

```bash
git add test/helpers/integration.bash
git commit -m "test: add integration helpers with safety guardrail"
```

---

## Task 16: Write the integration matrix orchestrator

**Files:**
- Create: `test/helpers/integration-matrix.sh`

Loops the 8 cells, sets env vars, invokes bats.

- [ ] **Step 1: Write the orchestrator**

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BATS="$ROOT/test/bats/bats-core/bin/bats"

fail=0
for use_1p in 0 1; do
  for shell_to_use in zsh bash; do
    for mode in fresh rerun; do
      echo "=== matrix cell: USE_1_PASSWORD=$use_1p SHELL_TO_USE=$shell_to_use RUN_MODE=$mode ==="
      if ! USE_1_PASSWORD=$use_1p SHELL_TO_USE=$shell_to_use RUN_MODE=$mode \
           timeout 300 "$BATS" "$ROOT/test/integration/install.bats"; then
        fail=1
      fi
    done
  done
done
exit "$fail"
```

- [ ] **Step 2: Make executable**

```bash
chmod +x test/helpers/integration-matrix.sh
```

- [ ] **Step 3: Commit**

```bash
git add test/helpers/integration-matrix.sh
git commit -m "test: add integration matrix orchestrator"
```

---

## Task 17: Write the parameterized integration test

**Files:**
- Create: `test/integration/install.bats`

This is the single test file that asserts every pass criterion from the spec, conditioned on env vars.

- [ ] **Step 1: Write the test file**

```bash
#!/usr/bin/env bats

load '../helpers/common'
load '../helpers/integration'

setup() {
  assert_safe_home
  # reset_scratch_home is called BETWEEN cells by the orchestrator, not per-test.
  # Each cell is a single bats invocation with one test that runs init.sh.
  # We use one test per assertion group via sharing setup via environment.
  :
}

@test "init.sh completes successfully" {
  run bash "$HOME/.local/share/dotfiles/scripts/init.sh"
  assert_success
}

@test "bork on PATH after init" {
  run command -v bork
  assert_success
}

@test "just on PATH after init" {
  run command -v just
  assert_success
}

@test "gitconfig rendered with no literal placeholders" {
  assert_file_exists "$HOME/.gitconfig"
  refute_file_contains "$HOME/.gitconfig" '${GIT_EMAIL}'
  refute_file_contains "$HOME/.gitconfig" '${GIT_NAME}'
}

@test "claude config copied from repo" {
  assert_files_equal "$HOME/.claude/settings.json" "$HOME/.local/share/dotfiles/config/claude/settings.json"
  assert_files_equal "$HOME/.claude/CLAUDE.md" "$HOME/.local/share/dotfiles/config/claude/CLAUDE.md"
}

@test "direnv installed" {
  run command -v direnv
  assert_success
}

@test "uv present on PATH or at ~/.local/bin" {
  if command -v uv >/dev/null 2>&1; then
    pass=1
  elif [[ -x "$HOME/.local/bin/uv" ]]; then
    pass=1
  else
    pass=0
  fi
  assert_equal "$pass" "1"
}

@test "claude cli present on PATH or at ~/.local/bin" {
  if command -v claude >/dev/null 2>&1; then
    pass=1
  elif [[ -x "$HOME/.local/bin/claude" ]]; then
    pass=1
  else
    pass=0
  fi
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

@test "rerun-mode: idempotent, no dupes, no crashes" {
  if [[ "${RUN_MODE:-fresh}" != "rerun" ]]; then
    skip "only runs in rerun mode"
  fi
  # Already ran once (the orchestrator didn't reset HOME between fresh/rerun — see note).
  # Run it again and assert success.
  run bash "$HOME/.local/share/dotfiles/scripts/init.sh"
  assert_success

  # router line still exactly once
  local rc_file
  if [[ "${SHELL_TO_USE:-zsh}" == "zsh" ]]; then
    rc_file="$HOME/.zshrc"
  else
    rc_file="$HOME/.bashrc"
  fi
  local line='source "$HOME/.local/share/dotfiles/config/router.sh"'
  run grep -cF "$line" "$rc_file"
  assert_output "1"

  # apt source list not duplicated
  if [[ "${USE_1_PASSWORD:-0}" == "1" && "$(uname)" == "Linux" ]]; then
    run grep -c '1password' /etc/apt/sources.list.d/1password.list
    assert_output "1"
  fi
}
```

**Note on rerun semantics:** the orchestrator calls `reset_scratch_home` before each cell. The `rerun` cell needs state from a prior `fresh` run to be meaningful. Update the orchestrator to handle this: do not reset between a `fresh` cell and the immediately-following `rerun` cell with the same `USE_1_PASSWORD` and `SHELL_TO_USE`.

- [ ] **Step 2: Fix the orchestrator to reset only before `fresh` cells**

Edit `test/helpers/integration-matrix.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BATS="$ROOT/test/bats/bats-core/bin/bats"

# shellcheck disable=SC1091
source "$ROOT/test/helpers/integration.bash"

# Seed $DOTFILES_REPO_ROOT for the helper in non-bats contexts.
DOTFILES_REPO_ROOT="$ROOT"
export DOTFILES_REPO_ROOT

fail=0
for use_1p in 0 1; do
  for shell_to_use in zsh bash; do
    for mode in fresh rerun; do
      if [[ "$mode" == "fresh" ]]; then
        reset_scratch_home
      fi
      echo "=== matrix cell: USE_1_PASSWORD=$use_1p SHELL_TO_USE=$shell_to_use RUN_MODE=$mode ==="
      if ! USE_1_PASSWORD=$use_1p SHELL_TO_USE=$shell_to_use RUN_MODE=$mode \
           timeout 300 "$BATS" "$ROOT/test/integration/install.bats"; then
        fail=1
      fi
    done
  done
done
exit "$fail"
```

- [ ] **Step 3: Commit**

```bash
git add test/integration/install.bats test/helpers/integration-matrix.sh
git commit -m "test: add parameterized integration test and update orchestrator"
```

---

## Task 18: Lima VM definition and startup script

**Files:**
- Create: `test/lima/linux-test.yaml`
- Create: `test/lima/up.sh`

- [ ] **Step 1: Write the Lima VM definition**

```yaml
# test/lima/linux-test.yaml
# Ubuntu 24.04 arm64 VM for integration testing.
images:
  - location: "https://cloud-images.ubuntu.com/releases/24.04/release/ubuntu-24.04-server-cloudimg-arm64.img"
    arch: "aarch64"

vmType: "vz"
cpus: 4
memory: "4GiB"
disk: "20GiB"

mounts:
  - location: "~"
    writable: false
  - location: "{{ .Dir }}/../../.."
    mountPoint: "/workspace/dotfiles"
    writable: true

networks:
  - mode: shared
```

- [ ] **Step 2: Write the startup script**

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VM_NAME="linux-test"

state=$(limactl list --format '{{.Name}} {{.Status}}' | awk -v n="$VM_NAME" '$1==n {print $2}')

case "$state" in
  "")
    limactl start --name "$VM_NAME" "$SCRIPT_DIR/linux-test.yaml"
    ;;
  Stopped)
    limactl start "$VM_NAME"
    ;;
  Running)
    ;;
  *)
    echo "unexpected Lima state: $state" >&2
    exit 1
    ;;
esac
```

- [ ] **Step 3: Make executable**

```bash
chmod +x test/lima/up.sh
```

- [ ] **Step 4: Commit**

```bash
git add test/lima/linux-test.yaml test/lima/up.sh
git commit -m "test: Lima VM definition and startup script"
```

---

## Task 19: tart VM setup scripts

**Files:**
- Create: `test/tart/prepare.sh`
- Create: `test/tart/run.sh`
- Create: `test/tart/reset.sh`

- [ ] **Step 1: Write `prepare.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail

BASE_IMAGE="ghcr.io/cirruslabs/macos-sequoia-base:latest"
INSTANCE="dotfiles-test"

if ! tart list | awk '{print $2}' | grep -qx "$INSTANCE"; then
  tart pull "$BASE_IMAGE"
  tart clone "$BASE_IMAGE" "$INSTANCE"
fi
```

- [ ] **Step 2: Write `run.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail

INSTANCE="dotfiles-test"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

tier="${1:?usage: run.sh unit|integration}"

# Start VM if not already running
if ! tart list --format json | python3 -c "
import sys, json
for vm in json.load(sys.stdin):
    if vm['Name'] == '$INSTANCE' and vm['State'] == 'running':
        sys.exit(0)
sys.exit(1)
"; then
  tart run --no-graphics "$INSTANCE" &
  sleep 20  # give it time to boot; improve with a wait-for-ssh loop later
fi

IP="$(tart ip "$INSTANCE")"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"

# rsync the repo in
rsync -az --delete -e "ssh $SSH_OPTS" "$REPO_ROOT/" "admin@$IP:/tmp/dotfiles/"

# run the test
ssh $SSH_OPTS "admin@$IP" "REPO_SRC=/tmp/dotfiles ALLOW_DESTRUCTIVE=1 /tmp/dotfiles/test/run.sh $tier"
```

- [ ] **Step 3: Write `reset.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail

BASE_IMAGE="ghcr.io/cirruslabs/macos-sequoia-base:latest"
INSTANCE="dotfiles-test"

tart stop "$INSTANCE" 2>/dev/null || true
tart delete "$INSTANCE" 2>/dev/null || true
tart clone "$BASE_IMAGE" "$INSTANCE"
```

- [ ] **Step 4: Make executable**

```bash
chmod +x test/tart/prepare.sh test/tart/run.sh test/tart/reset.sh
```

- [ ] **Step 5: Commit**

```bash
git add test/tart/prepare.sh test/tart/run.sh test/tart/reset.sh
git commit -m "test: tart VM setup scripts for macOS integration"
```

---

## Task 20: Wire integration tier into justfile

**Files:**
- Modify: `justfile`

- [ ] **Step 1: Add recipes**

Final `justfile`:

```make
set shell := ["bash", "scripts/just-shell.sh"]

export PATH := justfile_directory() / "vendor/bork/bin" + ":" + env_var("PATH")

# Show available recipes
default:
    @just --list

update:
    scripts/update.sh

test: test-unit

test-unit:
    test/run.sh unit

test-linux:
    test/lima/up.sh
    limactl shell linux-test -- bash -c "cd /workspace/dotfiles && ALLOW_DESTRUCTIVE=1 REPO_SRC=/workspace/dotfiles test/run.sh integration"

test-macos:
    test/tart/prepare.sh
    test/tart/run.sh integration

test-linux-clean:
    -limactl delete -f linux-test
    just test-linux

test-macos-clean:
    test/tart/reset.sh
    just test-macos

test-all: test-unit test-linux test-macos
```

- [ ] **Step 2: Verify `just` sees the new recipes**

Run: `just --list`
Expected: lists all test recipes.

- [ ] **Step 3: Commit**

```bash
git add justfile
git commit -m "test: wire integration tier into justfile"
```

---

## Task 21: Add integration job to GHA workflow

**Files:**
- Modify: `.github/workflows/tests.yml`

- [ ] **Step 1: Add the integration job**

Final workflow:

```yaml
# .github/workflows/tests.yml
name: tests
on:
  push:
    branches: [main]
  pull_request:
  workflow_dispatch:

jobs:
  unit:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - run: test/run.sh unit

  integration:
    needs: unit
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    timeout-minutes: 45
    env:
      ALLOW_DESTRUCTIVE: "1"
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - run: test/run.sh integration
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/tests.yml
git commit -m "ci: add integration job to tests workflow"
```

---

## Task 22: Update README with clone and test instructions

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Append the new sections**

Add to `README.md`:

```markdown
## Development

### Cloning

This repo vendors bats via git submodules. Clone with:

```
git clone --recurse-submodules https://github.com/voidfiles/dotfiles.git
```

Or if you already cloned without submodules:

```
git submodule update --init --recursive
```

### Running tests

```
just test           # fast unit tier
just test-linux     # integration tier in Lima VM
just test-macos     # integration tier in tart VM (Apple Silicon only)
just test-all       # everything
```

Paranoid full VM reset:

```
just test-linux-clean
just test-macos-clean
```

Tests also run on every PR and push to `main` via GitHub Actions.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add development section with test instructions"
```

---

## Self-Review Summary

**Spec coverage:**
- Two tiers (unit + integration): tasks 7–12 (unit), 15–17 (integration).
- Vendored bats via submodules: task 1.
- Helpers (common, scratch, stubs, integration, matrix orchestrator): tasks 2, 3, 4, 15, 16.
- All stubs named in spec (bork, brew, apt-get, curl, git, chsh, sudo, envsubst): tasks 4–5. **envsubst** is NOT stubbed — the spec lists it only "to pin order on PATH" and unit tests use the real one. Confirmed intentional.
- Fixtures (git, local_config): task 5 adds minimal, task 10 extends for refresh-skills, `local_config` fixtures are inlined per-test so no separate fixture task.
- 6 unit test files: tasks 7–12.
- Single parameterized integration.bats: task 17.
- Lima + tart setup: tasks 18, 19.
- Single `test/run.sh` entry point: task 6.
- Justfile additions: tasks 13 (unit), 20 (all).
- GHA workflow: tasks 14 (unit), 21 (integration).
- Guardrail against destructive ops: task 15 implements `assert_safe_home`; integration.bats calls it in setup.
- 8-cell matrix, reset-before-fresh-not-rerun: task 16 (updated in task 17).

**Placeholder scan:** no TBDs, no "handle edge cases" hand-waves, every step contains actual code.

**Type/name consistency:**
- `install_stubs`, `stub_assert_called`, `stub_respond`, `make_scratch_home`, `assert_safe_home`, `reset_scratch_home` — consistent across every reference.
- `DOTFILES_REPO_ROOT` (capital) used everywhere, never drifts to `DOTFILES_DIR` in helper code. `DOTFILES_DIR` is used only when it's the env var the production scripts read.
- Variable `STUB_LOG` used consistently.

**Known follow-ups called out in spec (not blocking):**
- Status badge in README — not in plan; trivial post-merge task.
- CI caching — not in plan; revisit later per spec.
- Per-cell `workflow_dispatch` input — not in plan; post-merge enhancement.

Plan complete and saved to `docs/superpowers/plans/2026-04-19-bats-testing.md`.
