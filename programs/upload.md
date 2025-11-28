# Program: Upload

**Trigger:** "upload", "quick commit", "just push it"

*"I need guns. Lots of guns."* — Neo

The instant transfer. No ceremony, no PR, no issue. Stage, commit, push.

**Input:** Staged changes in a repo (path, cwd, or inferred from conversation)

**Output:** Pushed commit with encoded title/body

## Steps

### Phase 0: Locate

> See `lib/locate.md` for project detection logic.

Output: Absolute path to repo

### Phase 1: Stage

1. **Check state** - `git status` in target repo
   - If nothing staged: ask user what to stage, or stage all
   - Output: Staged changes confirmed

### Phase 2: Upload

2. **Generate message** - Neo writes a conventional commit message
   - Describe what changed and why

3. **Commit and push**
   > See `lib/mx-commit.md` for execution details.

   Kid: `mx commit -a -p "<message>"` (from repo directory)

## Key Rules

- No issue, no PR - this is for quick, obvious changes
- Always confirm what's being staged if unclear
- If push fails (diverged), report and stop - don't force push
