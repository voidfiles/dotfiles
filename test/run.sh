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
