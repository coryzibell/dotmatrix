## Warn when using random behavior flags

**Type:** `issue`
**Labels:** `identity:persephone`, `identity:smith`, `high-priority`, `ux`

### Context

From Construct review of `base-d` project. Persephone identified UX issue.

**Source:** `~/.matrix/cache/construct/base-d/ux-recommendations.md`

### Problem

`--compress` and `--hash` without arguments randomly select an algorithm. This is intentional but undiscoverable - users don't know output will vary.

### Solution

Print a notice to stderr when random selection occurs:

```
Note: Using randomly selected algorithm 'zstd' (use --compress=zstd to fix)
```

### Implementation Steps

1. When `--compress` has no argument, print selection to stderr
2. When `--hash` has no argument, print selection to stderr
3. Include hint showing how to make it deterministic
4. Respect `--quiet` flag to suppress notices

### Acceptance Criteria

- [ ] Random selection prints notice to stderr
- [ ] Notice includes the selected algorithm
- [ ] Notice shows how to make it deterministic
- [ ] `--quiet` suppresses the notice

### Handoff

Persephone designs message → Smith implements → Neo merges
