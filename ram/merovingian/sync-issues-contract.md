# Issue Synchronization Contract

**Artifact:** `/home/w3surf/.claude/artifacts/bin/sync_issues.py`
**Created:** 2025-11-26

## Purpose

Bidirectional synchronization between YAML issue definitions and GitHub Issues API.

## Data Flow

```
YAML files → Parse → Compare timestamps → GitHub API
                              ↓
                    Update local with issue number
```

## Key Mechanisms

### 1. Issue Matching Strategy
- **Primary:** `metadata.github_issue_number` (most reliable)
- **Fallback:** Exact title match
- Once matched, issue number is persisted to YAML

### 2. Timestamp Comparison
- **Local:** File modification time (`stat.st_mtime`)
- **GitHub:** `updated_at` field (ISO 8601)
- **Rule:** Local newer → push to GitHub. GitHub newer → skip.

### 3. Change Detection
Compares:
- Title
- Body
- Labels (as set)
- Assignees (as set)

### 4. Sync Operations

| Scenario | Action | Result |
|----------|--------|--------|
| No GitHub match | `POST /repos/{owner}/{repo}/issues` | Create + persist issue number |
| Match + unchanged | Skip | Report skipped |
| Match + local newer | `PATCH /repos/{owner}/{repo}/issues/{number}` | Update GitHub |
| Match + GitHub newer | Skip | Report GitHub is source of truth |

## YAML Structure Contract

```yaml
metadata:
  title: "Issue title"
  labels: ["identity:smith", "security"]
  assignees: ["username"]
  github_issue_number: 42  # Persisted after first sync

body_markdown: |
  Full markdown body content
```

## Token Source

Same as `sync_labels.py`:
- Path: `~/.claude.json`
- Key: `projects.<project>.mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN`

## Dependencies

- **stdlib:** `json`, `urllib`, `pathlib`, `datetime`
- **optional:** `pyyaml` (required for this script)

## Usage

```bash
python sync_issues.py <owner/repo> <issues-dir>
```

Example:
```bash
python sync_issues.py coryzibell/matrix ~/.matrix/cache/construct/matrix/issues/
```

## Output Reports

- Created: New issues pushed to GitHub
- Updated: Local changes synced to GitHub
- Skipped (unchanged): No differences detected
- Skipped (GitHub newer): GitHub is canonical
- Errors: Parse failures, API errors

## Future Enhancements

- Milestone support
- State transitions (open/closed)
- Comment synchronization
- Bidirectional pull (GitHub → YAML)
- Dry-run mode

---

"Choice is an illusion created between those with power and those without."

The sync is complete. The contract is clear.
