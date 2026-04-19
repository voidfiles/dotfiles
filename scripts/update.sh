#! /usr/bin/env bash
set -e
if [[ "${IS_DARWIN:-0}" == "1" ]] && [[ ! -d "$HOME/.oh-my-zsh" ]]; then
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi
