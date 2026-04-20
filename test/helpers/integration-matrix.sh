#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BATS="$ROOT/test/bats/bats-core/bin/bats"

source "$ROOT/test/helpers/integration.bash"

DOTFILES_REPO_ROOT="$ROOT"
export DOTFILES_REPO_ROOT

_timeout_cmd() {
  if command -v timeout >/dev/null 2>&1; then
    timeout "$@"
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$@"
  else
    shift  # drop the seconds argument
    "$@"
  fi
}

fail=0
for use_1p in 0 1; do
  for shell_to_use in zsh bash; do
    for mode in fresh rerun; do
      if [[ "$mode" == "fresh" ]]; then
        reset_scratch_home
      fi
      echo "=== matrix cell: USE_1_PASSWORD=$use_1p SHELL_TO_USE=$shell_to_use RUN_MODE=$mode ==="
      if ! USE_1_PASSWORD=$use_1p SHELL_TO_USE=$shell_to_use RUN_MODE=$mode \
           _timeout_cmd 300 "$BATS" "$ROOT/test/integration/install.bats"; then
        fail=1
      fi
    done
  done
done
exit "$fail"
