[ -f "$HOME/.local_config.sh" ] && . "$HOME/.local_config.sh"

export USE_1_PASSWORD="${USE_1_PASSWORD:-1}"
export SHELL_TO_USE="${SHELL_TO_USE:-zsh}"

export GIT_EMAIL="${GIT_EMAIL:-voidfiles@gmail.com}"
export GIT_NAME="${GIT_NAME:-voidfiles}"

export IS_ZSH=0
export IS_BASH=0
case $SHELL_TO_USE in
  zsh) IS_ZSH=1 ;;
  bash)  IS_BASH=1  ;;
esac

export IS_DARWIN=0
export IS_LINUX=0
case "$(uname)" in
  Darwin) IS_DARWIN=1 ;;
  Linux)  IS_LINUX=1  ;;
esac