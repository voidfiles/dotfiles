# dotfiles

Boot this from any machine

```
curl "https://raw.githubusercontent.com/voidfiles/dotfiles/refs/heads/main/scripts/boot.sh" | bash
```

## Configuration

```
touch ~/.local_config.sh
echo "export USE_1_PASSWORD=0" >> ~/.local_config.sh
curl "https://raw.githubusercontent.com/voidfiles/dotfiles/refs/heads/main/scripts/boot.sh" | bash
```

Per-machine Obsidian vault overrides can also live in `~/.local_config.sh`:

```
export OBSIDIAN_ROOT="$HOME/Documents/Alex3"
```

For auto-detection without pinning one path, set a colon-separated candidate list:

```
export OBSIDIAN_ROOT_CANDIDATES="$HOME/Documents/Alex3:$HOME/Dropbox/obsidian/Alex3"
```

## Development

### Cloning

This repo vendors bats via git submodules. Clone with:

```
git clone --recurse-submodules https://github.com/voidfiles/dotfiles.git
```

Or if you already cloned without submodules:

```
git submodule update --init --recursive
```

### Running tests

```
just test           # fast unit tier (~2s)
just test-linux     # integration tier in Lima VM (Ubuntu 24.04)
just test-macos     # integration tier in tart VM (Apple Silicon only)
just test-all       # everything
```

Paranoid full VM reset:

```
just test-linux-clean
just test-macos-clean
```

Tests also run automatically on every PR and push to `main` via GitHub Actions.
