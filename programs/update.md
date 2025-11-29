# Program: Update

**Trigger:** "Update", "Refresh matrix", "Sync dotmatrix", "Get latest"

**Purpose:** Sync dotmatrix with upstream and run setup to refresh agent configs and CLAUDE.md context.

*"Upgrades."* — Agent Smith

## Steps

### Phase 1: Check Status

1. **Check for local changes:**
   ```bash
   cd ~/.matrix && git status --short
   ```
   - If uncommitted changes exist, warn and ask whether to stash or commit first
   - Clean working tree required before pull

2. **Fetch upstream:**
   ```bash
   cd ~/.matrix && git fetch origin
   ```

3. **Check if behind:**
   ```bash
   cd ~/.matrix && git rev-list HEAD..origin/main --count
   ```
   - If 0: "Already up to date" - skip to Phase 3
   - If >0: Show what's incoming, proceed to Phase 2

### Phase 2: Pull (if needed)

4. **Show incoming commits:**
   ```bash
   cd ~/.matrix && git log HEAD..origin/main --oneline
   ```

5. **Pull changes:**
   ```bash
   cd ~/.matrix && git pull --rebase origin main
   ```

### Phase 3: Push Local (if ahead)

6. **Check if ahead:**
   ```bash
   cd ~/.matrix && git rev-list origin/main..HEAD --count
   ```
   - If >0: Push local commits
   ```bash
   cd ~/.matrix && git push origin main
   ```

### Phase 4: Run Setup

7. **Run setup script:**
   ```bash
   python ~/.matrix/setup.py
   ```
   - Syncs agent definitions to Claude Code
   - Updates CLAUDE.md context
   - Reports what was updated

### Phase 5: Confirm

8. **Summary:**
   - Commits pulled (if any)
   - Commits pushed (if any)
   - Setup results

## Key Rules

- Always fetch before checking status
- Never force push
- If merge conflicts occur, stop and report to kautau
- Setup runs even if no git changes (refreshes config)
