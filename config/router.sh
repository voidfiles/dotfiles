source "$HOME/.local/share/dotfiles/config/config.sh"

for f in "$HOME/.local/share/dotfiles/config/shell/"*.sh; do [ -r "$f" ] && . "$f"; done

