#!/usr/bin/env bash
set -euo pipefail

BASE_IMAGE="ghcr.io/cirruslabs/macos-sequoia-base:latest"
INSTANCE="dotfiles-test"

if ! tart list 2>/dev/null | awk 'NR>1 {print $1}' | grep -qx "$INSTANCE"; then
  tart pull "$BASE_IMAGE"
  tart clone "$BASE_IMAGE" "$INSTANCE"
else
  echo "VM $INSTANCE already exists"
fi
