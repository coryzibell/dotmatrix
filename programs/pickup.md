# Program: Pickup

**Trigger:** `/load pickup [pr-id or context]`

*"Your muscles have atrophied. We're rebuilding them."* — Morpheus

Picks up work from the water - gets a PR into proper shape for merge. The branch needs the full context of main to gain its strength back. Handles the case where work was done on main, needs rebasing, or just needs final prep.

## Arguments

- `[pr-id]` - GitHub PR number (e.g., `131`)
- `[context]` - Description of what we're working on (e.g., "fiche PR")
- *(none)* - Use current conversation context

## On Load

1. **Verify working directory** - `pwd` to confirm we're in the right repo
2. **Identify the PR** - From argument or conversation context
3. **Check current branch state:**
   ```
   git branch --show-current
   git status
   ```

## Branch Recovery Flow

If work is on `main` instead of a feature branch:

1. **Stash uncommitted work** (if any)
   ```
   git stash push -m "pickup: recovering work from main"
   ```

2. **Check for unpushed commits on main**
   ```
   git log origin/main..main --oneline
   ```

3. **Create feature branch from current state**
   ```
   git checkout -b feature/<name>
   ```

4. **Reset main to origin**
   ```
   git checkout main
   git reset --hard origin/main
   ```

5. **Switch back and apply stash** (if stashed)
   ```
   git checkout feature/<name>
   git stash pop
   ```

## Rebase Flow

Once on the correct feature branch:

1. **Update main**
   ```
   git checkout main
   git pull
   ```

2. **Rebase feature branch**
   ```
   git checkout feature/<name>
   git rebase main
   ```

3. **Force push** (branch only, never main)
   ```
   git push --force-with-lease
   ```

## Output

Report to kautau:
- Branch name
- Commit count ahead of main
- Push status
- PR URL

Then wait. kautau watches CI, reviews the diff, gives final approval before merge.

## Merge (On Approval)

Only after explicit approval:
```
mx pr merge <number>
```

## Safety Rules

- **NEVER force push main** - abort and escalate if this would happen
- **ALWAYS verify cwd** before any git operation
- **ALWAYS use `--force-with-lease`** not `--force`
- If rebase has conflicts, stop and report - don't auto-resolve
