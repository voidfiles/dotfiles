#! /usr/bin/env bash
set -e
DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BORK_DIR="$DOTFILES_DIR/vendor/bork"

if [[ ! -x "$BORK_DIR/bin/bork" ]]; then
  bork_version=$(curl -sf https://api.github.com/repos/borksh/bork/releases/latest \
    | grep '"tag_name"' | sed 's/.*"tag_name": "\(.*\)".*/\1/')
  mkdir -p "$BORK_DIR"
  curl -sL "https://github.com/borksh/bork/archive/refs/tags/${bork_version}.tar.gz" \
    | tar -xz --strip-components=1 -C "$BORK_DIR"
  chmod +x "$BORK_DIR/bin/bork"
fi

export PATH="$BORK_DIR/bin:$PATH"

# shellcheck source=/dev/null
source "$DOTFILES_DIR/scripts/util.sh"

ensure_package just

just update

