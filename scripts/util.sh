ensure_package() {
  local pkg="$1"
  if [[ "$(uname)" == "Darwin" ]]; then
    bork 'do' ok brew "$pkg"
  elif command -v apt-get &>/dev/null; then
    bork 'do' ok apt "$pkg"
  else
    echo "Unsupported OS: cannot install $pkg" >&2
    return 1
  fi
}
