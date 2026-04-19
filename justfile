set shell := ["bash", "scripts/just-shell.sh"]

export PATH := justfile_directory() / "vendor/bork/bin" + ":" + env_var("PATH")

# Show available recipes
default:
    @just --list

update:
    scripts/update.sh