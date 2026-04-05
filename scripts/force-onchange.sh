#!/usr/bin/env bash
# Force a chezmoi run_onchange_ script to re-run on the next `chezmoi apply`
# by deleting its entry from the scriptState bucket.
#
# Usage: ./force-onchange.sh <partial-script-name>
# Example: ./force-onchange.sh sync-skills

set -euo pipefail

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <partial-script-name>" >&2
    echo "" >&2
    echo "Known scripts:" >&2
    chezmoi state dump --format=json | \
        python3 -c "import json,sys; [print(' ', v['name']) for v in json.load(sys.stdin).get('scriptState', {}).values()]"
    exit 1
fi

SEARCH="$1"

matches=$(chezmoi state dump --format=json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for key, val in data.get('scriptState', {}).items():
    if '$SEARCH' in val['name']:
        print(key, val['name'])
")

if [[ -z "$matches" ]]; then
    echo "No script state found matching '$SEARCH'." >&2
    exit 1
fi

echo "$matches" | while read -r key name; do
    echo "Clearing state for: $name ($key)"
    chezmoi state delete --bucket=scriptState --key="$key"
done

echo "Done. Run 'chezmoi apply' to trigger the script."
