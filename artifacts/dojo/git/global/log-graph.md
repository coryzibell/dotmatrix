# Git Log Graph

**Topic:** git
**Scope:** global
**Date:** 2025-11-30

## Knowledge

`git log --graph` displays commit history as an ASCII art tree showing branches and merges.

Common combo: `git log --graph --oneline --all` for a compact view of the entire repo history.

Many devs alias this: `git config --global alias.lg "log --graph --oneline --all"`

## Why It Matters

- Visualizes branch relationships
- Shows merge points and parallel development
- Useful for understanding complex histories before rebasing

## Quiz Question

What's the git command to show the commit history as a graph?

## Answer

`git log --graph`
