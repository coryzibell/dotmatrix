# GitHub Sync Scripts - Updates

## Date
2025-11-26

## Changes Made

### Task 1: cleanup_github.py
**Location:** `~/.matrix/artifacts/bin/cleanup_github.py`

Created a new script to close issues and delete discussions by number.

**Features:**
- Closes issues (GitHub doesn't allow true deletion) with `state: "closed"` and adds "duplicate" label
- Deletes discussions via GraphQL `deleteDiscussion` mutation
- Reads GitHub token from `~/.claude.json` (projects.<home>.mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN)
- Reports what was closed/deleted

**Usage:**
```bash
python cleanup_github.py coryzibell/matrix --issues 2,3,4,5,6,7 --discussions 8,9,10,11,12,13,14
```

### Task 2: sync_issues.py and sync_discussions.py
**Locations:**
- `~/.matrix/artifacts/bin/sync_issues.py`
- `~/.matrix/artifacts/bin/sync_discussions.py`

**Problem:** Previous logic compared timestamps to decide whether to update. If local was newer, it updated everything. If GitHub was newer, it skipped entirely. This meant partial edits (e.g., just changing a title) wouldn't sync if timestamps were unfavorable.

**Solution:** Field-by-field comparison and granular updates.

**New Logic:**
1. Match by `github_issue_number` or `github_discussion_id` first (existing behavior)
2. If matched, compare EACH field individually:
   - `title`: check if different
   - `body`: check if different
   - `labels`: check if different
   - `assignees`: check if different (issues only)
3. Only skip if ALL fields match (truly unchanged)
4. If ANY field differs, update GitHub with current local values
5. Report which fields changed (e.g., "Changed fields: title, labels")

**Removed:**
- Timestamp-based decision making
- "Skipped (GitHub newer)" tracking category
- All references to `skipped_github_newer`

**Benefits:**
- Renaming a title locally → updates just the title
- Changing labels locally → updates just the labels
- No more silent skips due to timestamp conflicts
- Local YAML is now truly the source of truth

## Files Modified
- `/home/w3surf/.claude/artifacts/bin/cleanup_github.py` (created)
- `/home/w3surf/.claude/artifacts/bin/sync_issues.py` (updated)
- `/home/w3surf/.claude/artifacts/bin/sync_discussions.py` (updated)

## Causality Notes
The relationship between local YAML and GitHub is now unidirectional by design. Local → GitHub. Always.

If someone edits on GitHub, the scripts will overwrite those edits on next sync. This is intentional. The YAML files are canonical.

If bidirectional sync is later desired, one must implement:
1. A "pull" mode that updates YAML from GitHub
2. A conflict resolution strategy
3. Timestamp tracking *per field* (complex)

For now, cause → effect is clear: change YAML → GitHub updates.

[Identity: Merovingian | Model: Sonnet | Status: success]
