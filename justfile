set shell := ["bash", "scripts/just-shell.sh"]

export PATH := justfile_directory() / "vendor/bork/bin" + ":" + env_var("PATH")

# Show available recipes
default:
    @just --list

update:
    scripts/update.sh

test: test-unit

test-unit:
    test/run.sh unit

test-linux:
    test/lima/up.sh
    limactl shell linux-test -- bash -c "ALLOW_DESTRUCTIVE=1 REPO_SRC=/workspace/dotfiles DOTFILES_REPO_ROOT=/workspace/dotfiles /workspace/dotfiles/test/run.sh integration"

test-macos:
    test/tart/prepare.sh
    test/tart/run.sh integration

test-linux-clean:
    -limactl delete -f linux-test
    just test-linux

test-macos-clean:
    test/tart/reset.sh
    just test-macos

test-all: test-unit test-linux test-macos