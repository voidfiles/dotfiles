# test/helpers/integration.bash

assert_safe_home() {
  if [[ "${ALLOW_DESTRUCTIVE:-0}" == "1" ]]; then
    return 0
  fi
  case "$HOME" in
    /tmp/*|/private/tmp/*|/home/lima*|/Users/lima*|"${BATS_TEST_TMPDIR:-__never__}"*)
      return 0
      ;;
    *)
      echo "integration test refusing to run against HOME=$HOME" >&2
      echo "set ALLOW_DESTRUCTIVE=1 to override (CI does this)" >&2
      return 1
      ;;
  esac
}

reset_scratch_home() {
  assert_safe_home || return 1

  rm -rf \
    "$HOME/.local/share/dotfiles" \
    "$HOME/.gitconfig" \
    "$HOME/.zshrc" \
    "$HOME/.bashrc" \
    "$HOME/.claude" \
    "$HOME/.oh-my-zsh" \
    "$HOME/.local/bin/uv" \
    "$HOME/.local/bin/claude"

  if [[ "$(uname)" == "Linux" ]]; then
    sudo rm -rf \
      /usr/share/keyrings/1password-archive-keyring.gpg \
      /etc/apt/sources.list.d/1password.list
  else
    if command -v brew >/dev/null 2>&1 && brew list --cask 1password-cli >/dev/null 2>&1; then
      brew uninstall --cask 1password-cli
    fi
  fi

  local src="${REPO_SRC:-$DOTFILES_REPO_ROOT}"
  mkdir -p "$HOME/.local/share"
  cp -R "$src" "$HOME/.local/share/dotfiles"
}
