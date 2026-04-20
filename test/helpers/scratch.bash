# test/helpers/scratch.bash

make_scratch_home() {
  local home_dir="$BATS_TEST_TMPDIR/home"
  mkdir -p "$home_dir/.local/share"
  ln -snf "$DOTFILES_REPO_ROOT" "$home_dir/.local/share/dotfiles"
  export HOME="$home_dir"
  export DOTFILES_DIR="$home_dir/.local/share/dotfiles"
}

teardown_scratch_home() {
  :
}
