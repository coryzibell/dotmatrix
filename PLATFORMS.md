# Platform Configuration

Check your environment's `Platform` value and follow the matching section.

## win32 (Windows / Git Bash)

- **Home:** `C:\Users\Cory Zibell\` or `/c/Users/Cory Zibell/` in Git Bash
- **Shell:** Git Bash (mingw64)
- **Path style:** Use forward slashes in bash, backslashes work in most tools
- **Line endings:** Git handles CRLF conversion, but watch for issues in scripts
- **Package managers:** scoop, npm, cargo
- **Claude CLI location:** `~/AppData/Local/mise/installs/npm-anthropic-ai-claude-code/`

## linux (WSL / NixOS)

- **Home:** `/home/kautau/` (or check `$HOME`)
- **Windows home access:** `/mnt/c/Users/Cory Zibell/`
- **Shell:** bash or nix shell
- **Shared config:** If using Windows claude config from WSL, symlink `~/.claude` → `/mnt/c/Users/Cory Zibell/.claude/`
- **Package managers:** nix, cargo
- **Line endings:** LF only

## darwin (macOS)

- **Home:** `/Users/kautau/` (or check `$HOME`)
- **Shell:** zsh by default
- **Package managers:** homebrew, cargo, npm
- **Line endings:** LF only

## Common Paths (use ~ expansion)

These paths work across platforms when `~` expands correctly:

- `~/.matrix/` - This config directory (tracked in git)
- `~/.matrix/agents/` - Agent identity files
- `~/.matrix/ram/` - Working directories
- `~/source/repos/` - Code repositories

## MCP Server Configuration

MCP servers are configured in `~/.claude.json` (note: outside `~/.claude/`). This file contains:
- MCP server definitions under `mcpServers` key
- OAuth/auth tokens (sensitive - don't commit)
- Runtime state and caches

Set up MCP servers on each machine separately. Tokens should not be shared across machines.
