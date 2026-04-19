#!/usr/bin/env bash
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"


# shellcheck source=/dev/null
source "$DOTFILES_DIR/config/config.sh"
# shellcheck source=/dev/null
source "$DOTFILES_DIR/scripts/util.sh"

eval "$1"
