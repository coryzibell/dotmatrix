# Program: Pull & Export

**Trigger:** "Pull issues", "Sync from GitHub", "Download discussions", "Export to markdown"

**Purpose:** Download issues and discussions from GitHub to local YAML, optionally export to human-readable markdown.

## Commands

- `mx sync pull` - GitHub → YAML (issues, discussions, comments)
- `mx sync push` - YAML → GitHub (issues, discussions)
- `mx sync labels` - Sync identity labels to repo
- `mx sync issues` - Bidirectional issue sync

## Steps

### Phase 0: Locate

> See `lib/locate.md` for project detection logic.

Output: Absolute path to repo, project name, owner/repo

### Pull from GitHub
```bash
mx sync pull <owner/repo>
mx sync pull coryzibell/matrix -o ~/.matrix/cache/construct/matrix/issues/
```

Downloads:
- All open issues with comments
- All discussions with comments
- Stores in YAML format with `last_synced` snapshot
- Default output: `~/.matrix/cache/sync/<owner>-<repo>/`

Merge behavior on pull:
- If local YAML has changes (differs from `last_synced`), warns and skips field update
- If local unchanged, updates from remote
- Comments always updated (remote-authoritative)

### Push to GitHub
```bash
mx sync push <owner/repo>
mx sync push coryzibell/matrix -i ~/.matrix/cache/construct/matrix/issues/
```

### Export to Markdown
```bash
mx convert yaml2md <yaml-dir> [-o output-dir] [--repo owner/repo]
mx convert yaml2md ~/.matrix/cache/sync/coryzibell-matrix/ -o ./docs/issues/ --repo coryzibell/matrix
```

Generates human-readable markdown with:
- Title, type, labels, status
- Link to GitHub issue/discussion
- Full body content
- All comments with author and timestamp

## Full Sync Toolchain

| Command | Direction | Purpose |
|---------|-----------|---------|
| `mx sync labels <repo>` | → GitHub | Create identity/category labels on repo |
| `mx sync pull <repo>` | GitHub → YAML | Download issues, discussions, comments |
| `mx sync push <repo>` | YAML → GitHub | Push issues + discussions (routes by type) |
| `mx sync issues <repo>` | ↔ GitHub | Bidirectional issue sync |
| `mx convert md2yaml <dir>` | MD → YAML | Convert authored markdown to YAML |
| `mx convert yaml2md <dir>` | YAML → MD | Export for human reading |

## Dry Run

All sync commands support `--dry-run` to preview changes:
```bash
mx sync pull coryzibell/matrix --dry-run
mx sync labels coryzibell/matrix --dry-run
```
