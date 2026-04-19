#!/bin/bash

LOADER='for f in ~/.config/shell/*.zsh(N); do source "$f"; done'
MARKER="# Load modular shell config"

# Read existing content
existing="$(cat ~/.zshrc)"

# Check if loader already present
if echo "$existing" | grep -qF "$MARKER"; then
    echo "$existing"
    exit 0
fi

# Append loader after existing content
echo "$existing"
echo ""
echo "$MARKER"
echo "$LOADER"
