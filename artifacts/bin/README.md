# Matrix Artifacts - Bin

Python scripts used as backends for `mx` commands and standalone utilities.

## GitHub Sync (mx backends)

These scripts are called by `mx sync` subcommands:

| Script | mx command | Purpose |
|--------|------------|---------|
| `pull_github.py` | `mx sync pull` | Download issues/discussions from GitHub to YAML |
| `sync_github.py` | `mx sync push` | Push YAML changes to GitHub |
| `sync_labels.py` | `mx sync labels` | Sync identity labels to repo |
| `sync_issues.py` | `mx sync issues` | Bidirectional issue sync |

## Standalone Utilities

| Script | Purpose | Usage |
|--------|---------|-------|
| `convert_issues.py` | Convert authored markdown to YAML | `python convert_issues.py <dir>` |
| `export_markdown.py` | Export YAML to human-readable markdown | `python export_markdown.py <yaml-dir> [output]` |
| `sync_wiki.py` | Push markdown to GitHub wiki | `python sync_wiki.py <repo> <dir>` |
| `cleanup_github.py` | Clean up GitHub artifacts | `python cleanup_github.py <repo>` |

## Session Tools

| Script | Purpose | Usage |
|--------|---------|-------|
| `extract-session.py` | Export Claude Code session to markdown | `python extract-session.py [session.jsonl]` |

## Matrix Tools

| Script | Purpose |
|--------|---------|
| `matrix_client.py` | GitHub App client for dotmatrix bot |
| `health_check.py` | System health checks |

## Notes

- Scripts are executable (`chmod +x`)
- Require Python 3.11+
- GitHub tools need `GITHUB_TOKEN` env var or `~/.claude.json`
- Prefer using `mx sync` commands over calling scripts directly
