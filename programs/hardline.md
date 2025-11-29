# Program: Hardline

**Trigger:** "hardline", "ship it", "take it to prod"

*"Tank, I need a hardline."* — Neo

The permanent connection out. Takes local work all the way to merged code.

**Input:** A repo with work to ship (path, cwd, or inferred from conversation)

**Output:** Merged PR with linked issue

## Steps

### Phase 0: Locate

> See `lib/locate.md` for project detection logic.

Output: Absolute path to repo, project name

### Phase 1: Reconnaissance

1. **Assess state** - What's been done, what's staged, what branch are we on
   - Kid: `git status`, `git log --oneline -10`, `git diff --stat` (in target repo)
   - Output: Current state summary, current branch name

2. **Branch check** - If on main/master, create a feature branch
   - If already on feature branch: continue
   - If on main/master: Create branch from changes (e.g., `feature/<issue-slug>` or `fix/<description>`)
   - Kid: `git checkout -b <branch-name>`
   - Output: Branch name (existing or newly created)

3. **Find or create issue** - Check if an issue exists for this work
   - Merovingian: Search GitHub issues for related work
   - If none: Create issue describing the work
   - Output: Issue number and URL

### Phase 2: Package

4. **Commit work** - Stage and commit with encoded message
   > See `lib/mx-commit.md` for encoding details.

   Kid: `mx commit -a "<message>"` (commit only, no push yet)
   - The PR is the paper trail, commits are just noise in bulk
   - Output: Commit SHA

5. **Push branch** - Get it to origin
   - Kid: Push to remote (create upstream if needed)
   - Output: Remote branch URL

### Phase 3: Connect

6. **Open PR** - Create pull request against target branch
   - Merovingian: `mcp__github__create_pull_request`
   - Link to issue in PR body (`Closes #<issue>`)
   - Output: PR number and URL

### Phase 4: Watch

7. **Wait for CI** - Monitor checks if workflows exist
   - Merovingian: Poll `mcp__github__get_pull_request_status`
   - If CI fails: Report failure, stop here
   - Output: Green status or failure report

### Phase 5: Exit

8. **Merge** - Complete the connection
   - Merovingian: `mcp__github__merge_pull_request`
   - Squash or merge based on repo convention
   - GitHub auto-closes the linked issue on merge
   - Output: Merge confirmation

9. **Cleanup** - Return to main, pull latest, delete feature branch
   - Kid: `git checkout main && git pull && git branch -d <feature-branch>`
   - Output: Clean state

## Key Rules

- **Run autonomously** - Don't ask for confirmation unless blocked. Context from conversation is enough.
- **Always issue + PR** - The PR is the paper trail. Commits are noise.
- Stop and report if CI fails - don't force merge
- Respect branch protection - if merge blocked, report why
- If no CI workflows exist, skip Phase 4

## Example

```
kautau: hardline
Neo: *assesses state*
     Branch: feature/add-validation
     3 commits ahead of main
     No existing issue found - creating one...

     Issue #42 created: "Add input validation"
     PR #43 opened against main
     Waiting for CI...
     ✓ All checks passed
     Merged. Welcome to the real world.
```
