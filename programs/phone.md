# Phone Program

**Trigger:** `/load phone [project]`

> *The phone rings. Morpheus answers. "We're in."*

## Purpose

Wake up call. Get situational awareness on a project. Updates persistent status doc for both Neo and kautau.

Like the game of phone - context passes through sessions, things can drift. This syncs you back to reality.

> See `lib/storage.md` for public vs private storage resolution. Use `{storage}` below.

## Execution

### 1. Locate

> See `lib/locate.md` for project detection logic.

Output: Absolute path to repo, project name

### 2. Gather State

**Git:**
- `git fetch`
- Current branch, last commit
- Commits ahead/behind origin
- Uncommitted changes

**GitHub:**
- Open PRs (state, CI status, reviews needed)
- Recent issues (assigned, new since last sync)
- CI status on main

**Context:**
- Check `{storage}/ram/neo/` for session notes
- Check `{storage}/cache/` for workflow artifacts

### 3. Update Status Doc

Write to `{storage}/zion/project/<name>/STATUS.md`:

```markdown
# <Project Name> - Status

**Repository:** <url>
**Last Sync:** <ISO 8601 timestamp>
**Primary Branch:** main

---

## Current State

**Branch:** <current>
**Last Commit:** <sha> - "<message>"
**Uncommitted Changes:** Yes/No
**Ahead/Behind:** +N/-M vs origin

## CI Status

<Passing/Failing> - [link to run]

## Open PRs

- #N: <title> (state, CI, reviews)

## Active Issues

- #N: <title> (assigned, priority)

## Recent Activity

**Since last sync:**
- <commits, PRs merged, issues closed>

## Blockers

- <None or list>

## From RAM

<Any relevant session notes>

---

**Next Steps:**
1. <immediate>
2. <follow-up>
```

### 4. Update Index

Append/update entry in `{storage}/zion/project/INDEX.md`:

```markdown
| Project | Last Sync | State | Notes |
|---------|-----------|-------|-------|
| base-d  | 2025-11-28 | clean | v0.2.0 released |
```

### 5. Summary

Output brief summary:

```
## base-d - We're in.

State: clean, even with origin
CI: ✅ Passing
PRs: 2 open - #45 needs review, #47 CI failing
Issues: 1 new since last sync
Last session: SIMD optimization, ARM blocked

Sync now? [y/n]
```

## Options

- `--deep` - Full commit messages, PR descriptions
- `--sync` - Auto-pull if behind
- `--all` - Ring all indexed projects
- `--stale` - Show projects not synced in >7 days

## Ownership

- **phone** reads and writes STATUS.md directly
- **Zion Control** curates when stale, archives old activity
- **RAM** stays session-scoped, STATUS survives context resets
