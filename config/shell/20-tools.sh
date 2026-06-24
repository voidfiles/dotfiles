
if [ "$USE_1_PASSWORD" = "1" ]; then
    source "$HOME/.config/op/plugins.sh"
fi

# Obsidian vault
if [[ -n "${OBSIDIAN_ROOT:-}" ]]; then
  export OBSIDIAN_ROOT
else
  : "${OBSIDIAN_ROOT_CANDIDATES:=$HOME/Documents/Alex3:$HOME/Dropbox/obsidian/Alex3}"
  _obsidian_ifs="$IFS"
  IFS=:
  for _obsidian_candidate in $OBSIDIAN_ROOT_CANDIDATES; do
    if [[ -d "$_obsidian_candidate/.obsidian" ]]; then
      export OBSIDIAN_ROOT="$_obsidian_candidate"
      break
    fi
  done
  IFS="$_obsidian_ifs"
  unset _obsidian_ifs _obsidian_candidate
fi
