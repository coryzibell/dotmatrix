# Claude Artifacts - Bin

Permanent scripts and tools.

## Session Tools

| Script | Purpose | Usage |
|--------|---------|-------|
| `extract-session.py` | Export Claude Code session to readable markdown | `python3 extract-session.py [session.jsonl]` |

## GitHub Sync Tools

| Script | Purpose |
|--------|---------|
| `sync_github.py` | Main sync orchestrator |
| `sync_issues.py` | Sync GitHub issues to local markdown |
| `sync_discussions.py` | Sync GitHub discussions |
| `sync_labels.py` | Sync label definitions |
| `sync_wiki.py` | Sync wiki pages |
| `sync_merge.py` | Merge synced content |
| `pull_github.py` | Pull from GitHub |
| `export_markdown.py` | Export to markdown |
| `convert_issues.py` | Convert issue formats |
| `cleanup_github.py` | Clean up GitHub artifacts |

## Matrix Tools

| Script | Purpose |
|--------|---------|
| `matrix_client.py` | GitHub App client for dotmatrix bot |
| `health_check.py` | System health checks |

## Notes

- Scripts are executable (`chmod +x`)
- Most require Python 3.11+
- GitHub tools need `GITHUB_TOKEN` env var
