#!/usr/bin/env bash
set -e
export DOTFILES_DIR="$HOME/.local/share/dotfiles"

if [ ! -d "$DOTFILES_DIR" ]; then
    mkdir -p "$HOME/.local/share"
    git clone https://github.com/voidfiles/dotfiles.git "$DOTFILES_DIR"
fi

cd $DOTFILES_DIR

bash scripts/init.sh
