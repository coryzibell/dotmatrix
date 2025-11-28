# Add narrative generation for briefings

**Type:** `idea`
**Labels:** `identity:oracle`, `identity:morpheus`, `idea`
**Status:** unknown
**GitHub:** [#27](https://github.com/coryzibell/matrix/discussions/27)

---

# Add narrative generation for briefings






From Construct review of `matrix` project. Oracle identified unseen paths during perspectives phase.

**Source:** Oracle's unseen doors review

## Idea

Generate narrative briefings instead of raw data:

```bash
matrix brief --period=week
matrix brief --period=today
matrix brief --identity=smith
```

Output:
```
This week in the Matrix:

Smith completed 3 blockers and started work on the auth system.
Trinity traced a nasty race condition in the queue handler.
Cypher flagged 2 security issues, both now resolved.

Emerging patterns:
- Security work is trending up (3 issues this week vs 1 last week)
- Test coverage improved from 3% to 47%

Coming up:
- 2 blockers remain before ship
- Oracle suggests exploring the caching approach
```

## Benefits

- Human-readable summaries
- Context for stakeholders
- Spot patterns across time
- Onboarding new team members

## Questions to Consider

- How much narrative vs. data?
- Templates or generative?
- Period options (day, week, sprint, month)?

## Implementation Steps

1. Define briefing template structure
2. Aggregate data across time periods
3. Identify notable events and patterns
4. Generate narrative from template
5. Add `matrix brief` command

## Acceptance Criteria

- [ ] Daily/weekly/custom period briefings
- [ ] Per-identity briefings
- [ ] Pattern detection across time
- [ ] Human-readable narrative output
- [ ] Configurable verbosity

## Handoff

1. Oracle defines what makes a good briefing
2. Morpheus helps with narrative tone
3. Smith implements generation

---

*Last synced: Nov 26, 2025 at 09:21 PM*