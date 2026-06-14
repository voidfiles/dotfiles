ensure_package() {
  local pkg="$1"
  local output status
  if [[ "$(uname)" == "Darwin" ]]; then
    output=$(bork 'do' ok brew "$pkg" 2>&1) || status=$?
  elif [[ "$(uname)" == "Linux" ]] && command -v apt-get &>/dev/null; then
    output=$(bork 'do' ok apt "$pkg" 2>&1) || status=$?
  else
    echo "Unsupported OS: cannot install $pkg" >&2
    return 1
  fi

  [[ -z "$output" ]] || printf '%s\n' "$output"
  if [[ "${status:-0}" -eq 0 ]]; then
    return 0
  fi

  # bork returns 1 after a successful install/upgrade because a change was made.
  [[ "${status:-0}" -eq 1 && "$output" == *"* success"* ]]
}

export -f ensure_package
