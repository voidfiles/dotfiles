# Bats Testing Design

**Status:** Draft, awaiting review
**Date:** 2026-04-19
**Owner:** voidfiles

## Goal

Add automated tests for this dotfiles repo using [bats-core](https://github.com/bats-core/bats-core). Tests run locally in fast VMs (Lima for Linux, tart for macOS) and the identical `.bats` files run in GitHub Actions. Two tiers: fast hermetic unit tests and full-fidelity integration tests that actually install everything against real network and real package managers.

## Non-Goals

- No containers (Docker/Podman). Linux tests use real VMs via Lima.
- No bats retries. Flakes fail loudly and get re-run manually.
- No caching in CI on the first pass. Revisit if matrix grows.
- No nightly runs. Integration runs on PR and push to `main` is enough.
- No testing of `bork` itself. That's upstream.

## Architecture

Two tiers, one set of bats files, a single entry point (`test/run.sh`) invoked the same way from every execution envelope.

### Execution matrix

| Tier | Local (Mac dev) | GitHub Actions |
|------|-----------------|----------------|
| Unit | `bats test/unit` directly on host, stubs on PATH | `bats test/unit` on `ubuntu-latest` and `macos-latest` |
| Integration — Linux | Lima Ubuntu 24.04 VM, `limactl shell linux-test test/run.sh integration` | `ubuntu-latest` runner runs `test/run.sh integration` directly |
| Integration — macOS | tart VM cloned from cached base image, `test/tart/run.sh integration` | `macos-latest` runner runs `test/run.sh integration` directly |

The `.bats` files are byte-identical across all envelopes. Only the launcher wrapping them differs. On Apple Silicon, both Lima (using Apple's Virtualization framework) and tart boot cached images in 10–20s; in CI, the runner IS the VM, so no nesting.

### Integration-tier parameter matrix

Per platform, 8 cells:

```
{USE_1_PASSWORD=0, USE_1_PASSWORD=1}
  × {SHELL_TO_USE=zsh, SHELL_TO_USE=bash}
  × {RUN_MODE=fresh, RUN_MODE=rerun}
```

Total across platforms: 16 integration runs per full test execution. Every config axis in `config/config.sh` is exercised; idempotency (`rerun`) is exercised for each config.

## Directory Layout

```
test/
├── bats/                          # vendored via git submodules, pinned to release tags
│   ├── bats-core/
│   ├── bats-support/
│   ├── bats-assert/
│   └── bats-file/
├── helpers/
│   ├── common.bash                # load bats-* libs, define DOTFILES_REPO_ROOT
│   ├── scratch.bash               # make_scratch_home / teardown_scratch_home
│   ├── stubs.bash                 # install_stubs, stub_assert_called, stub_respond
│   ├── integration.bash           # helpers loaded by integration .bats files
│   └── integration-matrix.sh      # orchestrator: loops 8 cells, invokes bats per cell
├── stubs/
│   ├── bork                       # record invocations, exit 0
│   ├── brew                       # record, exit 0
│   ├── apt-get                    # record, exit 0
│   ├── curl                       # record URL; respond from fixture if configured
│   ├── git                        # record args; on clone, copy from test/fixtures/git/<name>
│   ├── chsh                       # record args, exit 0
│   ├── sudo                       # forward to real command (sudo-less path)
│   └── envsubst                   # real envsubst, listed only to pin order on PATH
├── fixtures/
│   ├── git/                       # fake skill repos served by the git stub
│   │   ├── thinking-partner/
│   │   └── hegelian-dialectic-skill/
│   └── local_config/
│       ├── default.sh             # empty
│       ├── no-1password.sh        # USE_1_PASSWORD=0
│       └── bash-shell.sh          # SHELL_TO_USE=bash
├── unit/
│   ├── config.bats
│   ├── util_ensure_package.bats
│   ├── templates.bats
│   ├── refresh_skills.bats
│   ├── router.bats
│   └── idempotency.bats
├── integration/
│   └── install.bats               # single parameterized suite, re-run per matrix cell
├── lima/
│   ├── linux-test.yaml            # VM definition
│   └── up.sh                      # idempotent VM start
├── tart/
│   ├── prepare.sh                 # fetch + clone base image, one-time
│   ├── run.sh                     # run a command inside the VM via ssh
│   └── reset.sh                   # delete + re-clone from base
└── run.sh                         # single entry point: test/run.sh {unit|integration}
```

### Helpers

**`test/helpers/common.bash`** — loaded by every test file:

```bash
load '../bats/bats-support/load'
load '../bats/bats-assert/load'
load '../bats/bats-file/load'
load './scratch'
load './stubs'

DOTFILES_REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
```

**`scratch.bash`** — `make_scratch_home` creates `$BATS_TEST_TMPDIR/home`, exports `HOME` to it, creates `.local/share/`, and symlinks `$DOTFILES_REPO_ROOT` to `$HOME/.local/share/dotfiles` so `DOTFILES_DIR` resolves correctly without copying. `bats` auto-cleans `BATS_TEST_TMPDIR` between tests.

**`stubs.bash`** — `install_stubs` prepends `test/stubs/` to `PATH` and exports `STUB_LOG=$BATS_TEST_TMPDIR/stub.log`. Stubs append one line per invocation (e.g., `bork do ok brew direnv`). `stub_assert_called <cmd> <args...>` greps the log. `stub_respond <cmd> <match> <fixture-path>` lets a test arrange a specific response (used mainly for the `curl https://api.github.com/repos/borksh/bork/releases/latest` call).

### Single entry point

`test/run.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
tier="${1:?usage: run.sh unit|integration}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="$ROOT/test/bats/bats-core/bin:$PATH"

case "$tier" in
  unit)
    bats "$ROOT/test/unit"
    ;;
  integration)
    "$ROOT/test/helpers/integration-matrix.sh"
    ;;
  *) echo "unknown tier: $tier" >&2; exit 2 ;;
esac
```

`integration-matrix.sh` loops the 8 cells, resetting `$HOME` state between each and invoking bats with `USE_1_PASSWORD`, `SHELL_TO_USE`, `RUN_MODE` set.

### Justfile additions

```make
test: test-unit

test-unit:
    test/run.sh unit

test-linux:
    test/lima/up.sh && limactl shell linux-test test/run.sh integration

test-macos:
    test/tart/prepare.sh && test/tart/run.sh integration

test-linux-clean:
    limactl delete -f linux-test; just test-linux

test-macos-clean:
    test/tart/reset.sh; just test-macos

test-all: test-unit test-linux test-macos
```

## Unit Tier

Target runtime: under 2s total. Six test files.

### `config.bats`
Sources `config/config.sh` in a subshell with controlled env, asserts exported flags.
- `SHELL_TO_USE` unset → `IS_ZSH=1`, `IS_BASH=0`
- `SHELL_TO_USE=bash` → inverted
- Stub `uname` returning `Darwin` → `IS_DARWIN=1`, `IS_LINUX=0`
- Stub `uname` returning `Linux` → inverted
- `~/.local_config.sh` with `USE_1_PASSWORD=0` overrides default of 1
- `GIT_EMAIL` / `GIT_NAME` defaults apply when unset; user values win

### `util_ensure_package.bats`
Sources `util.sh`, calls `ensure_package foo` under each platform.
- Darwin → stub log contains `bork do ok brew foo` exactly once
- Linux with `apt-get` on PATH → stub log contains `bork do ok apt foo`
- Neither → non-zero exit, stderr contains "Unsupported OS"

### `templates.bats`
Renders `templates/dot_gitconfig.tmpl` via `envsubst`, asserts output matches a golden fixture. Also: empty vars produce empty fields, no literal `${GIT_EMAIL}` remains.

### `refresh_skills.bats`
Runs `scripts/refresh-skills.sh` with a stub `git` that, on `clone <url> <dst>`, copies from `test/fixtures/git/<repo-name>/` instead.
- Skills listed in `SKILL_SOURCES` get copied to `SKILLS_DIR`
- Bare URL form ("url|") copies repo root as a skill named after the repo
- Rename syntax `remote:local` renames the dir AND rewrites `name:` in every `*.md` up to depth 2
- `.external-skills` manifest contains the local names, rebuilt from scratch each run
- Failed clone increments error counter, script exits non-zero

### `router.bats`
Sources `config/router.sh` with a scratch `$HOME`, asserts `config.sh` was sourced and every `config/shell/*.sh` ran (detected via side-effect env vars or PATH additions those scripts make).

### `idempotency.bats`
The high-value unit test. Runs `scripts/init.sh` twice in a scratch `$HOME` with all network-y stubs in place.
- `.zshrc` contains the router source line exactly once after second run
- `.gitconfig` content byte-identical between runs
- `~/.claude/settings.json` matches `config/claude/settings.json` byte-for-byte
- No duplicate apt source lines for 1Password (when that path is taken)
- Second-run stub log shows no destructive ops

### Unit-tier exclusions
- No real network, no real installs
- oh-my-zsh/uv/claude installer script contents not asserted — unit just verifies the scripts attempt to invoke them

## Integration Tier

Real scripts, real packages, real network, real VMs.

### VM lifecycle

**Linux (Lima).** `test/lima/linux-test.yaml` declares an Ubuntu 24.04 arm64 VM with `vz` virtualization, 4 CPU, 4 GB RAM, 20 GB disk, and a writable mount of the repo at `/workspace/dotfiles`. The mount is deliberately NOT at `~/.local/share/dotfiles` — the scripts write there, and we want that on the VM's own disk so the clone/reuse logic is faithfully exercised.

`test/lima/up.sh`:
1. VM doesn't exist → `limactl start --name linux-test ./linux-test.yaml` (30–60s first time)
2. Stopped → `limactl start linux-test` (~10s)
3. Already up → skip

**macOS (tart).** `test/tart/prepare.sh` pulls a pinned base image (`ghcr.io/cirruslabs/macos-sequoia-base` or equivalent, pinned by digest), then `tart clone` creates a `dotfiles-test` instance. `test/tart/run.sh` starts the VM in the background and SSHes in to exec the test script. `test/tart/reset.sh` does `tart delete` + re-clone from base.

### Between-cell reset

**Keep the VM, reset `$HOME`.** Between matrix cells:

```bash
reset_scratch_home() {
  # Linux
  sudo rm -rf /usr/share/keyrings/1password-archive-keyring.gpg \
              /etc/apt/sources.list.d/1password.list
  rm -rf "$HOME"/{.local/share/dotfiles,.gitconfig,.zshrc,.bashrc,.claude,.oh-my-zsh,.local/bin/uv,.local/bin/claude}
  cp -R /workspace/dotfiles "$HOME/.local/share/dotfiles"

  # macOS adds: brew uninstall --cask 1password-cli (if present), rm -rf the same dotfiles
  # and $HOME cruft; no apt keyring on Darwin
}
```

**Why not reset the whole VM per cell:** 8 cells × full VM boot ≈ 10+ minutes of VM startup alone. The value of a fresh VM is "works on a clean machine," which is validated on cell 1. Cells 2–8 validate "works from a clean `$HOME` on a mostly-clean machine," which matches the common real-world case of re-running `update.sh` on an existing workstation.

`just test-linux-clean` and `just test-macos-clean` exist for paranoid full-reset runs.

### Matrix orchestration

`test/helpers/integration-matrix.sh`:

```bash
for use_1p in 0 1; do
  for shell in zsh bash; do
    for mode in fresh rerun; do
      reset_scratch_home
      USE_1_PASSWORD=$use_1p SHELL_TO_USE=$shell RUN_MODE=$mode \
        bats "$ROOT/test/integration/install.bats"
    done
  done
done
```

`install.bats` reads the env vars and conditions its assertions.

### Pass criteria

After `init.sh` completes, every cell asserts:

**Always:**
- Exit status 0
- `bork` on `PATH`, reports a version
- `just` on `PATH`
- `~/.gitconfig` contains expected email + name, no literal `${...}` left
- `~/.claude/settings.json` and `~/.claude/CLAUDE.md` match repo source byte-for-byte
- `uv` on `PATH` or at `~/.local/bin/uv`
- `direnv` on `PATH`
- `claude` binary present on `PATH` or at `~/.local/bin/claude`

**If `SHELL_TO_USE=zsh`:**
- `~/.zshrc` contains `source "$HOME/.local/share/dotfiles/config/router.sh"` exactly once
- On macOS: `~/.oh-my-zsh/` directory exists
- On Linux (when real zsh is installed in the VM): either login shell in `/etc/passwd` is zsh OR a `chsh` attempt is observable in the script log

**If `SHELL_TO_USE=bash`:**
- `~/.bashrc` contains the router source line exactly once
- `~/.oh-my-zsh` does NOT exist
- No `chsh` invocation

**If `USE_1_PASSWORD=1`:**
- macOS: `op` binary present (from `1password-cli` cask)
- Linux: `/usr/share/keyrings/1password-archive-keyring.gpg` exists, `/etc/apt/sources.list.d/1password.list` contains the expected deb line, `op` binary present

**If `USE_1_PASSWORD=0`:** none of the 1Password artifacts exist (no keyring file, no source list, no `op` binary)

**If `RUN_MODE=rerun`:** every assertion above PLUS:
- `.zshrc` / `.bashrc` router line appears exactly once (idempotent append)
- `~/.gitconfig` content identical between runs
- No crash from re-running `cp` / `envsubst` / the oh-my-zsh installer
- `apt sources.list.d/1password.list` not duplicated

### Flake handling

- **No bats-level retries.** Real failures should fail, not hide.
- **Install-level retries** already exist through idempotency: a transient `apt-get update` failure gets a second shot in the `rerun` cell.
- **Per-cell timeout:** 5 min. A hung `apt-get` won't block the whole matrix.
- **Sequential cells.** Parallelism across VMs isn't worth the complexity at this scale. Budget: ~2 min/cell × 8 cells ≈ 16 min per platform, ~32 min for a full local run.

### Destructive-ops guardrail

`test/helpers/integration.bash` exports an `assert_safe_home` function called in `setup()` for every integration test. It refuses to proceed unless one of:

- `$HOME` is under `/tmp`, `/private/tmp`, `/home/lima`, `/Users/lima`, or `$BATS_TEST_TMPDIR`
- `$ALLOW_DESTRUCTIVE=1` is set

CI sets `ALLOW_DESTRUCTIVE=1` explicitly (runners are disposable). This prevents an accidental `just test-macos` on the developer's actual machine from nuking their real `~/.gitconfig`.

## CI Wiring

Single workflow file: `.github/workflows/tests.yml`.

```yaml
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

**Design notes:**

- Unit gates integration. Broken config parsing shouldn't waste 20 min of integration time.
- `fail-fast: false` so a flake on one OS doesn't mask the other.
- No caching yet. `apt-get install direnv gettext just` and `brew install just direnv` are ~60s each; caching adds complexity for small wins at this scale.
- Submodules (`test/bats/*`) require `submodules: recursive` on checkout. README will note the same for local clones.
- No Lima or tart in CI. GHA runners are already the VMs; `test/run.sh` runs directly on them.

## Open Follow-ups

- Status badge in README after the first green run.
- Revisit CI caching if the matrix grows past 30 min per platform.
- Consider a `workflow_dispatch` input to run only a specific matrix cell for faster debugging of integration failures.
