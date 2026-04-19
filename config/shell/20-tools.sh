
if [ "$USE_1_PASSWORD" = "1" ]; then
    source "$HOME/.config/op/plugins.sh"
fi

# Obsidian vault
for _obsidian_candidate in "$HOME/Dropbox/obsidian/Alex3" "$HOME/Documents/Alex3"; do
  if [[ -d "$_obsidian_candidate/.obsidian" ]]; then
    export OBSIDIAN_ROOT="$_obsidian_candidate"
    break
  fi
done
unset _obsidian_candidate
