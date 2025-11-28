# Fix file permissions from 0644 to 0600

**Type:** `issue`
**Labels:** `identity:smith`, `improvement`, `security`
**Status:** open
**GitHub:** [#20](https://github.com/coryzibell/matrix/issues/20)

---

# Fix file permissions from 0644 to 0600






From Construct review of `matrix` project. Cypher identified minor security issue during security audit.

**Source:** Cypher's security audit

## Problem

Files written by matrix use permissions `0644` (world-readable). Since these files may contain sensitive information in `~/.matrix/ram/`, they should be `0600` (owner-only).

## Solution

Change all `os.WriteFile` and file creation calls to use `0600` permissions.

## Implementation Steps

1. Grep for all `0644` in codebase
2. Change to `0600`
3. Verify file creation still works
4. Check no tests depend on specific permissions

## Acceptance Criteria

- [ ] All new files created with `0600` permissions
- [ ] No `0644` permissions in codebase
- [ ] Tests pass
- [ ] Existing functionality unchanged

## Handoff

1. Smith makes the change
2. Deus verifies tests pass
3. Neo reviews and merges

---

*Last synced: Nov 26, 2025 at 09:21 PM*