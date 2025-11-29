## Add CLI test coverage

**Type:** `issue`
**Labels:** `identity:deus`, `high-priority`, `testing`

### Context

From Construct review of `base-d` project. Deus identified critical testing gap.

**Source:** `~/.matrix/cache/construct/base-d/quality-recommendations.md`

### Problem

The CLI layer has zero test coverage. This is the primary user interface for a CLI tool.

**Untested functions:**
- `parse_interval()` - time parsing
- `select_random_dictionary()` - random selection
- File I/O operations
- Configuration loading
- Error handling paths

### Solution

Add unit tests and integration tests for CLI module.

### Implementation Steps

1. Add unit tests in `src/cli/mod.rs`:
   - `parse_interval()` - 4 tests (valid, invalid, edge cases)
   - `select_random_dictionary()` - 3 tests
   - Config loading - 4 tests
2. Add integration tests using `assert_cmd` crate:
   - Basic encode/decode workflows
   - File input/output
   - Error cases
3. Target: 20-30 CLI tests

### Acceptance Criteria

- [ ] `parse_interval()` fully tested
- [ ] Random selection tested
- [ ] File operations tested
- [ ] Config loading tested
- [ ] Integration tests for common workflows
- [ ] Coverage report shows CLI module improvement

### Handoff

Deus owns this → Neo reviews → merge
