load '../bats/bats-support/load'
load '../bats/bats-assert/load'
load '../bats/bats-file/load'

# Load local helpers using source pattern
source "$(dirname "${BASH_SOURCE[0]}")/scratch.bash"
source "$(dirname "${BASH_SOURCE[0]}")/stubs.bash"

DOTFILES_REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
export DOTFILES_REPO_ROOT
