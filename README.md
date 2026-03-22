# dotfiles

Managed with [chezmoi](https://chezmoi.io). Secrets via [1Password CLI](https://developer.1password.com/docs/cli/).

## Bootstrap on a new machine

### Prerequisites

`op` (1Password CLI) must be available **before** running chezmoi, because templates pull secrets at render time.

**macOS:**
```
# Via 1Password app: Settings > Developer > Command-Line Interface
# Or manually (if brew already installed):
brew install 1password-cli
```

**Linux:** Install from [1password.com/downloads/linux](https://1password.com/downloads/linux)

Sign in:
```bash
op account add
eval $(op signin)
```

### Apply dotfiles

```bash
sh -c "$(curl -fsLS get.chezmoi.io)"
chezmoi init --apply github.com/voidfiles/dotfiles
```

chezmoi fetches the repo, renders templates (secrets from 1Password), runs the bootstrap script once, and fetches oh-my-zsh via externals.

## Day-to-day workflow

| Command | Purpose |
|---------|---------|
| `chezmoi diff` | Preview what chezmoi would change |
| `chezmoi status` | Show which managed files have drifted |
| `chezmoi apply` | Apply source state to home directory |
| `chezmoi re-add ~/.zshrc` | Pull manual edits back into source |
| `chezmoi edit ~/.zshrc` | Edit the source file for a managed dotfile |
| `chezmoi update` | Pull latest from git remote and apply |
| `chezmoi cd` | Open a shell in the source directory |

To make changes: `chezmoi edit <file>`, commit, push. On other machines: `chezmoi update`.

## What's managed

| File | Notes |
|------|-------|
| `~/.zshrc` | oh-my-zsh, PATH, tool hooks |
| `~/.zprofile` | brew, SSH agent, base PATH |
| `~/.gitconfig` | name + email (email from 1Password) |
| `~/.oh-my-zsh` | Fetched as archive external |

## Updating oh-my-zsh or plugins

Edit the version URLs in `.chezmoiexternal.toml`, then run `chezmoi apply`.
