#!/usr/bin/env bash
set -euo pipefail

INSTANCE="dotfiles-test"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

tier="${1:?usage: run.sh unit|integration}"

# Ensure VM exists
"$SCRIPT_DIR/prepare.sh"

# Start VM if not already running (tart run is non-blocking with --no-graphics)
if ! tart list 2>/dev/null | awk 'NR>1 {print $1, $2}' | grep -q "^$INSTANCE running"; then
  tart run --no-graphics "$INSTANCE" &
  # Wait for SSH to become available
  IP=""
  for i in $(seq 1 30); do
    IP="$(tart ip "$INSTANCE" 2>/dev/null)" && break
    sleep 2
  done
  if [[ -z "$IP" ]]; then
    echo "tart: timed out waiting for VM IP" >&2
    exit 1
  fi
fi

IP="$(tart ip "$INSTANCE")"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"

# Sync repo
rsync -az --delete -e "ssh $SSH_OPTS" "$REPO_ROOT/" "admin@$IP:/tmp/dotfiles/"

# Run tests in VM
ssh $SSH_OPTS "admin@$IP" \
  "REPO_SRC=/tmp/dotfiles ALLOW_DESTRUCTIVE=1 DOTFILES_REPO_ROOT=/tmp/dotfiles /tmp/dotfiles/test/run.sh $tier"
