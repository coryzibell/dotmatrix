## Add NO_COLOR support

**Type:** `issue`
**Labels:** `identity:smith`, `high-priority`, `accessibility`

### Context

From Construct review of `base-d` project. Zee identified accessibility gap.

**Source:** `~/.matrix/cache/construct/base-d/accessibility.md`

### Problem

base-d doesn't respect the `NO_COLOR` environment variable. Users who need plain output for accessibility or piping have no way to disable colors.

See: https://no-color.org/

### Solution

Check `NO_COLOR` environment variable and disable ANSI colors when set.

### Implementation Steps

1. Add `NO_COLOR` check at startup
2. Disable all ANSI escapes when `NO_COLOR` is set (any value)
3. Also respect `--no-color` flag for explicit control
4. Ensure Matrix mode respects this too

### Acceptance Criteria

- [ ] `NO_COLOR=1 base-d ...` produces no ANSI escapes
- [ ] `--no-color` flag works
- [ ] Matrix mode works without colors
- [ ] Piped output is clean

### Handoff

Smith implements → Zee verifies accessibility → Neo merges
