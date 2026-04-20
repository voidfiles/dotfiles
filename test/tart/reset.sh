#!/usr/bin/env bash
set -euo pipefail

BASE_IMAGE="ghcr.io/cirruslabs/macos-sequoia-base:latest"
INSTANCE="dotfiles-test"

tart stop "$INSTANCE" 2>/dev/null || true
tart delete "$INSTANCE" 2>/dev/null || true
tart clone "$BASE_IMAGE" "$INSTANCE"
echo "VM $INSTANCE reset from base image"
