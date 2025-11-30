# Git Reset: Soft vs Hard

**Topic:** git
**Scope:** global
**Date:** 2025-11-30

## Knowledge

`git reset --soft` moves HEAD to a commit but keeps your staged changes and working directory intact. `git reset --hard` moves HEAD and resets both the staging area AND working directory to match that commit - it's destructive.

## Why It Matters

- `--soft` is useful for squashing commits or redoing a commit message
- `--hard` is the nuclear option - use with caution as it discards uncommitted work
- There's also `--mixed` (default) which resets staging but keeps working directory

## Quiz Question

In Git, what's the difference between `git reset --soft` and `git reset --hard`?

## Answer

`--soft` just moves HEAD, keeping files and staging intact. `--hard` resets everything to match the target commit, discarding uncommitted changes.
