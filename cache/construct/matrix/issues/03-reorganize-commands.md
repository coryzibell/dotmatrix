# Reorganize commands to reduce overwhelm

**Type:** `issue`
**Labels:** `identity:persephone`, `identity:smith`, `improvement`, `ux`
**Status:** open
**GitHub:** [#17](https://github.com/coryzibell/matrix/issues/17)

---

# Reorganize commands to reduce overwhelm






From Construct review of `matrix` project. Persephone identified UX friction during user experience review.

**Source:** Persephone's UX review

## Problem

24 commands in a flat list overwhelms users. Running `matrix` or `matrix help` shows a wall of text. Users can't quickly find what they need.

Additionally:
- Some commands use subcommands, others don't (inconsistency)
- No `matrix help <command>` for detailed help on specific commands

## Solution

Group commands into logical categories:

```
matrix garden     # garden-paths, garden-seeds, tension-map
matrix security   # breach-points, vault-keys
matrix quality    # verdict, spec-verify, debt-ledger
matrix intel      # recon, crossroads, knowledge-gaps
matrix ops        # flight-check, dependency-map, platform-map
```

Or use a tiered help system:
- `matrix` - shows categories only
- `matrix <category>` - shows commands in category
- `matrix help <command>` - shows detailed help

## Implementation Steps

1. Persephone designs the command groupings and help hierarchy
2. Smith implements the command router with categories
3. Update help text to show categories first
4. Add `matrix help <command>` support
5. Update README to reflect new structure

## Acceptance Criteria

- [ ] Commands organized into logical categories
- [ ] `matrix` shows manageable overview (not 24 lines)
- [ ] `matrix help <command>` works for all commands
- [ ] Existing command names still work (backwards compatible)
- [ ] README updated with new structure

## Handoff

1. Persephone designs the groupings
2. Smith implements the changes
3. Morpheus updates documentation
4. Persephone gives final UX approval

---

*Last synced: Nov 26, 2025 at 09:21 PM*