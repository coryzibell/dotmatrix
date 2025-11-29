# Purge Git History Completely

Erase all history and start fresh with a clean single commit.

## The Problem

Force pushing to GitHub doesn't actually delete commits. GitHub retains all commits accessible by SHA indefinitely. Anyone with the SHA can still fetch the content.

## The Solution

Two-phase approach: clean the local repo, then recreate the remote.

### Phase 1: Local History Purge

```bash
git checkout --orphan fresh
git add -A
mx commit "Initial commit"
git branch -D main
git branch -m main
git gc --prune=now --aggressive
```

### Phase 2: Remote Recreation

1. Delete the GitHub repository entirely
2. Recreate with same name
3. Push fresh main branch

## Why This Works

`--orphan` creates a branch with no history. Deleting and recreating the repo is the only way to remove commits from GitHub's object store.

## When to Use

- Credentials leaked in history
- Large binaries bloating repo
- Starting truly fresh

---

*First documented: 2025-11-28*
