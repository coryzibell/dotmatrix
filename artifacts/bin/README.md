# Matrix Artifacts - Bin

All scripts have been migrated to pure Rust in the `mx` CLI.

## Available Commands

### GitHub Sync
```bash
mx sync pull <repo>      # Download issues/discussions to YAML
mx sync push <repo>      # Push YAML changes to GitHub
mx sync labels <repo>    # Sync identity labels
mx sync issues <repo>    # Bidirectional sync
```

### GitHub Operations
```bash
mx github cleanup <repo> --issues 1,2 --discussions 3,4
mx github comment issue <repo> <number> <message> [--identity NAME]
mx github comment discussion <repo> <number> <message> [--identity NAME]
```

### Conversion Tools
```bash
mx convert md2yaml <input> [-o output]
mx convert yaml2md <input> [-o output] [--repo owner/repo]
```

### Wiki
```bash
mx wiki sync <repo> <source> [--page-name NAME] [--dry-run]
```

### Session & Diagnostics
```bash
mx session export [path] [-o output]
mx doctor
```

### Zion Knowledge
```bash
mx zion search <query>
mx zion add --category <cat> --title <title>
mx zion list [--category <cat>]
```

## Notes

- All commands are native Rust - no Python required
- GitHub tools use token from `~/.claude.json`
- Run `mx --help` for full command reference
