#!/usr/bin/env bats

load '../helpers/common'

setup() {
  make_scratch_home
}

@test "router sources config.sh and exports platform flag" {
  run bash -c "HOME='$HOME'; source '$DOTFILES_REPO_ROOT/config/router.sh' 2>/dev/null; printf '%s' \"\$IS_DARWIN\""
  assert_success
  assert_output --regexp '^[01]$'
}

@test "router sources all config/shell/*.sh files without error" {
  # IS_ZSH=0 prevents 00-omz.sh from trying to load oh-my-zsh
  # USE_1_PASSWORD=0 prevents 01-ssh.sh and 20-tools.sh from sourcing 1password plugins
  run bash --norc --noprofile -c "
    export HOME='$HOME'
    export IS_ZSH=0
    export USE_1_PASSWORD=0
    source '$DOTFILES_REPO_ROOT/config/router.sh' 2>/dev/null
  "
  assert_success
}

@test "router sets PATH additions from 10-paths.sh" {
  result="$(bash --norc --noprofile -c "
    export HOME='$HOME'
    export IS_ZSH=0
    export USE_1_PASSWORD=0
    source '$DOTFILES_REPO_ROOT/config/router.sh' 2>/dev/null
    printf '%s' \"\$PATH\"
  ")"
  # 10-paths.sh unconditionally adds \$HOME/.local/bin to PATH
  [[ "$result" == *"$HOME/.local/bin"* ]]
}
