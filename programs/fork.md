# Program: Fork

**Trigger:** `/load fork [repo]` or `/load fork copy [repo]`

*"Billions of people just living out their lives... oblivious."* — Agent Smith

When you need to work on the same repo in parallel sessions without conflicts. Creates a clean working copy, you do your thing, delete it when merged.

## Input

- Repo name (from RAM context or explicit argument)
- Mode: fresh clone (default) or local copy

## Output

- Cloned repo at `~/work/personal/code/{repo}-fork-{timestamp}/`
- Session context updated to use the fork
- Ready for parallel work

## Modes

| Command | Behavior |
|---------|----------|
| `/load fork base-d` | Fresh `git clone` from origin (clean state) |
| `/load fork copy base-d` | Local `cp -r` (fast, preserves uncommitted state) |

Default is fresh clone - avoids inheriting noise from the other session.

## Naming

Forks use unix timestamp suffix: `{repo}-fork-{timestamp}`

Example: `base-d-fork-1733012345`

Why:
- Multiple sessions can fork the same repo without collision
- Timestamps are monotonic - easy to identify which is newer if something fails
- Session context tracks the full path, so Neo always knows which fork is active

## Steps

### Phase 1: Identify

1. **Determine the repo** - Check RAM context or explicit argument
2. **Verify source exists** - Confirm `~/work/personal/code/{repo}/` is valid (need it to get remote URL)
3. **Check for existing fork** - If `{repo}-fork` exists, ask: resume or replace?

### Phase 2: Clone

**Default (fresh):**
1. **Get timestamp** - `date +%s` (unix seconds)
2. **Get remote URL** - `git -C ~/work/personal/code/{repo} remote get-url origin`
3. **Clone fresh** - `git clone {url} ~/work/personal/code/{repo}-fork-{timestamp}`
4. **Clean slate** - No uncommitted changes, no stashes, pristine

**With `copy` flag:**
1. **Get timestamp** - `date +%s` (unix seconds)
2. **Copy the repo** - `cp -r ~/work/personal/code/{repo} ~/work/personal/code/{repo}-fork-{timestamp}`
3. **Preserve everything** - Uncommitted changes, stashes, local branches all come along

### Phase 3: Context Switch

1. **Update session context** - Note in RAM that this session works on the fork
2. **Confirm ready** - "Working on {repo}-fork. Original untouched."

## Cleanup: Merge

When work is done and merged upstream:

```
rm -rf ~/work/personal/code/{repo}-fork
```

Kid handles this on request. The fork is disposable.

## Key Rules

- **Forks are temporary** - Delete after merge, don't let them accumulate
- **Name convention** - `{repo}-fork-{timestamp}`, unique per session
- **Git state preserved** - Can push, pull, branch like normal
- **Context tracks the path** - Neo knows which fork is active in this session

## Example

```
User: I want to work on base-d in this session while the other one finishes
Neo: /load fork base-d
Kid: Cloned fresh to ~/work/personal/code/base-d-fork-1733012345/
Neo: Working on base-d-fork-1733012345. Clean slate. What's the task?
```

```
User: /load fork copy base-d
Kid: Copied to ~/work/personal/code/base-d-fork-1733012789/
Neo: Working on base-d-fork-1733012789. Carried over local state. What's the task?
```

## Variant: Fork with Branch

If you want to start on a specific branch:

```
/load fork base-d feature/new-thing
```

After cloning, Kid checks out the specified branch.
