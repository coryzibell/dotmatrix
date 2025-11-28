# Add prediction layer for forecasting

**Type:** `idea`
**Labels:** `identity:oracle`, `idea`
**Status:** unknown
**GitHub:** [#25](https://github.com/coryzibell/matrix/discussions/25)

---

# Add prediction layer for forecasting






From Construct review of `matrix` project. Oracle identified unseen paths during perspectives phase.

**Source:** Oracle's unseen doors review

## Idea

Forecast task completion and spot burnout patterns:

```bash
matrix forecast          # when will current blockers clear?
matrix forecast smith    # smith's velocity trend
matrix burnout-check     # are any identities overloaded?
```

## Benefits

- Anticipate delays before they happen
- Balance workload across identities
- Historical patterns inform future estimates
- Early warning for unsustainable pace

## Questions to Consider

- What data is needed for meaningful predictions?
- How to handle insufficient history?
- Confidence intervals vs. point estimates?

## Implementation Steps

1. Define metrics to track (task completion times, volume)
2. Build historical data collection
3. Implement simple forecasting (moving averages, trends)
4. Add forecast commands
5. Consider burnout heuristics

## Acceptance Criteria

- [ ] Historical velocity tracked per identity
- [ ] Basic forecasting based on trends
- [ ] Burnout/overload detection
- [ ] Clear confidence indicators
- [ ] Graceful handling of insufficient data

## Handoff

1. Oracle defines meaningful predictions
2. Architect designs data model
3. Smith implements tracking and forecasting

---

*Last synced: Nov 26, 2025 at 09:21 PM*