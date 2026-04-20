#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VM_NAME="linux-test"

state=$(limactl list --format '{{.Name}} {{.Status}}' 2>/dev/null | awk -v n="$VM_NAME" '$1==n {print $2}')

case "$state" in
  "")
    limactl start --name "$VM_NAME" "$SCRIPT_DIR/linux-test.yaml"
    ;;
  Stopped)
    limactl start "$VM_NAME"
    ;;
  Running)
    echo "VM $VM_NAME already running"
    ;;
  *)
    echo "unexpected Lima state: $state" >&2
    exit 1
    ;;
esac
