#!/usr/bin/env bash
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export IS_DARWIN=0
export IS_LINUX=0
case "$(uname)" in
  Darwin) IS_DARWIN=1 ;;
  Linux)  IS_LINUX=1  ;;
esac

# shellcheck source=/dev/null
source "$DOTFILES_DIR/scripts/util.sh"

eval "$1"
