# test/helpers/stubs.bash

install_stubs() {
  export STUB_LOG="$BATS_TEST_TMPDIR/stub.log"
  : > "$STUB_LOG"
  export PATH="$DOTFILES_REPO_ROOT/test/stubs:$PATH"
}

stub_assert_called() {
  local cmd="$1"
  shift
  local expected="$cmd $*"
  if ! grep -Fxq "$expected" "$STUB_LOG"; then
    echo "expected stub log to contain: $expected" >&2
    echo "actual stub log:" >&2
    cat "$STUB_LOG" >&2
    return 1
  fi
}

stub_assert_not_called() {
  local cmd="$1"
  if grep -E "^${cmd}( |$)" "$STUB_LOG" >/dev/null; then
    echo "did not expect stub log to contain calls to: $cmd" >&2
    cat "$STUB_LOG" >&2
    return 1
  fi
}

stub_respond() {
  local cmd="$1" match="$2" fixture="$3"
  export "STUB_RESPOND_${cmd//[^A-Za-z0-9]/_}=${match}::${fixture}"
}
