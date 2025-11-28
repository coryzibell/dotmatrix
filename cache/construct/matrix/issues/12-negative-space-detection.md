# Add negative space detection

**Type:** `idea`
**Labels:** `identity:oracle`, `idea`
**Status:** unknown
**GitHub:** [#26](https://github.com/coryzibell/matrix/discussions/26)

---

# Add negative space detection






From Construct review of `matrix` project. Oracle identified unseen paths during perspectives phase.

**Source:** Oracle's unseen doors review

## Idea

Detect what ISN'T happening:

```bash
matrix silence           # which identities haven't logged anything recently?
matrix gaps              # what areas have no coverage?
matrix forgotten         # stale tasks, abandoned threads
```

## Benefits

- Surface blind spots
- Find dropped balls before they matter
- Identify underutilized identities
- Prevent things from falling through cracks

## Questions to Consider

- How to define "should be happening"?
- False positives (silence might be intentional)?
- How far back to look?

## Implementation Steps

1. Define "expected activity" baselines
2. Track last-activity timestamps per identity
3. Identify gaps in coverage areas
4. Surface stale/abandoned items
5. Add silence/gaps/forgotten commands

## Acceptance Criteria

- [ ] Detect identities with no recent activity
- [ ] Surface stale tasks (configurable threshold)
- [ ] Identify coverage gaps
- [ ] Distinguish intentional silence from neglect
- [ ] Actionable output (not just lists)

## Handoff

1. Oracle defines what "negative space" means practically
2. Smith implements detection logic
3. Persephone ensures output is actionable, not anxiety-inducing

---

*Last synced: Nov 26, 2025 at 09:44 PM*