#! /usr/bin/env bash
set -e

DOTFILES_DIR="${DOTFILES_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

if [[ "${IS_DARWIN:-0}" == "1" ]] && [[ ! -d "$HOME/.oh-my-zsh" ]]; then
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi

if [[ "${USE_1_PASSWORD:-0}" == "1" ]]; then
  if [[ "${IS_DARWIN:-0}" == "1" ]]; then
    bork 'do' ok cask 1password-cli
  else
    keyring=/usr/share/keyrings/1password-archive-keyring.gpg
    source_list=/etc/apt/sources.list.d/1password.list
    arch=$(dpkg --print-architecture)
    source_line="deb [arch=${arch} signed-by=${keyring}] https://downloads.1password.com/linux/debian/${arch} stable main"

    if [[ ! -s "$keyring" ]]; then
      curl -fsSL https://downloads.1password.com/linux/keys/1password.asc \
        | sudo gpg --dearmor --output "$keyring"
    fi

    if [[ ! -f "$source_list" ]] || ! grep -qxF "$source_line" "$source_list"; then
      echo "$source_line" | sudo tee "$source_list" >/dev/null
      sudo apt-get update
    fi

    bork 'do' ok apt 1password-cli
  fi
fi

ensure_package direnv

if ! command -v uv >/dev/null 2>&1 && ! [[ -x "$HOME/.local/bin/uv" ]]; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi


if [[ "${IS_LINUX:-0}" == "1" ]] && [[ "${IS_ZSH:-0}" == "1" ]] && command -v zsh >/dev/null 2>&1; then
  zsh_path="$(command -v zsh)"
  if [[ "${SHELL:-}" != "$zsh_path" ]]; then
    chsh -s "$zsh_path"
  fi
fi

if [[ "${IS_ZSH:-0}" == "1" ]]; then
  rc_file="$HOME/.zshrc"
else
  rc_file="$HOME/.bashrc"
fi

router_line='source "$HOME/.local/share/dotfiles/config/router.sh"'
touch "$rc_file"
if ! grep -qxF "$router_line" "$rc_file"; then
  printf '\n%s\n' "$router_line" >> "$rc_file"
fi



ensure_package gettext

envsubst < "$DOTFILES_DIR/templates/dot_gitconfig.tmpl" > "$HOME/.gitconfig"

mkdir -p "$HOME/.claude"
cp "$DOTFILES_DIR/config/claude/settings.json" "$HOME/.claude/settings.json"

if ! command -v claude >/dev/null 2>&1 && ! [[ -x "$HOME/.local/bin/claude" ]]; then
  curl -fsSL https://claude.ai/install.sh | bash
fi




