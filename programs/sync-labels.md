# Program: Sync Repo Labels

**Trigger:** "Sync labels", "Set up issue labels", "Make sure repo has identity labels"

**Purpose:** Ensure a GitHub repo has labels for each identity so issues can be assigned to agents.

## Steps

### Phase 0: Locate

> See `lib/locate.md` for project detection logic.

Output: Absolute path to repo, project name, owner/repo

### Phase 1: Color Palette (one-time, already complete)
1. **Persephone defined colors** - Stored at `~/.matrix/artifacts/etc/identity-colors.yaml`
   - 28 identities mapped to hex colors
   - Grouped by function: Crisis/Combat (reds), Knowledge (blues), Creation (greens), etc.

### Phase 2: Label Creation
2. **Dispatch Merovingian** - Check existing labels, create missing identity labels
   - Input: repo owner/name (e.g., `coryzibell/matrix`)
   - Reference: `~/.matrix/artifacts/etc/identity-colors.yaml` for colors
   - Actions:
     - List current labels via `mcp__github__list_issues` or `gh label list`
     - Compare against the 28 identities
     - Create missing labels using colors from the artifact
   - Output: labels created/verified

## Label Format

- Name: `identity:{name}` (e.g., `identity:smith`, `identity:trinity`)
- Color: from `~/.matrix/artifacts/etc/identity-colors.yaml`
- Description: identity's one-line role

## Key Rules

- Color palette is pre-defined in artifacts - Merovingian reads it, doesn't decide colors
- Merovingian owns the API interactions (label creation/verification)
- Use the sync script: `python ~/.matrix/artifacts/bin/sync_labels.py <owner/repo>`
- Don't duplicate existing labels - script handles idempotency

## Example Execution

```bash
python ~/.matrix/artifacts/bin/sync_labels.py coryzibell/matrix
```
