# Program: Pull & Export

**Trigger:** "Pull issues", "Sync from GitHub", "Download discussions", "Export to markdown"

**Purpose:** Download issues and discussions from GitHub to local YAML, optionally export to human-readable markdown.

## Scripts

- `pull_github.py` - GitHub → YAML (issues, discussions, comments)
- `export_markdown.py` - YAML → Markdown (human-readable docs)

## Steps

### Phase 0: Locate

> See `lib/locate.md` for project detection logic.

Output: Absolute path to repo, project name, owner/repo

### Pull from GitHub
```bash
python ~/.matrix/artifacts/bin/pull_github.py <owner/repo> <output-dir>
python ~/.matrix/artifacts/bin/pull_github.py coryzibell/matrix ~/.matrix/cache/construct/matrix/issues/
```

Downloads:
- All open issues with comments
- All discussions with comments
- Stores in YAML format with `last_synced` snapshot

Merge behavior on pull:
- If local YAML has changes (differs from `last_synced`), warns and skips field update
- If local unchanged, updates from remote
- Comments always updated (remote-authoritative)

### Export to Markdown
```bash
python ~/.matrix/artifacts/bin/export_markdown.py <yaml-dir> [output-dir]
python ~/.matrix/artifacts/bin/export_markdown.py ~/.matrix/cache/construct/matrix/issues/ ./docs/issues/
```

Generates human-readable markdown with:
- Title, type, labels, status
- Link to GitHub issue/discussion
- Full body content
- All comments with author and timestamp

## Full Sync Toolchain

| Script | Direction | Purpose |
|--------|-----------|---------|
| `sync_labels.py` | → GitHub | Create identity/category labels on repo |
| `convert_issues.py` | MD → YAML | Convert authored markdown to YAML |
| `sync_github.py` | YAML → GitHub | Push issues + discussions (routes by type) |
| `pull_github.py` | GitHub → YAML | Download issues, discussions, comments |
| `export_markdown.py` | YAML → MD | Export for human reading |
| `sync_wiki.py` | MD → Wiki | Push markdown to GitHub wiki (via git) |

## Deprecated

Kept for reference:
- `sync_issues.py` - Replaced by `sync_github.py`
- `sync_discussions.py` - Replaced by `sync_github.py`
