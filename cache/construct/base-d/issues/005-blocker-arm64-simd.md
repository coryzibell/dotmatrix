## Resolve ARM64 SIMD bug #59

**Type:** `issue`
**Labels:** `identity:smith`, `blocker`, `platform`

### Context

From Construct review of `base-d` project. Trainman and Ramakandra identified platform issue.

**Source:** `~/.matrix/cache/construct/base-d/cross-platform.md`

### Problem

ARM64 SIMD (NEON) is disabled in CI due to bug #59. Apple Silicon users fall back to scalar code, missing significant performance gains.

`.github/workflows/pr-checks.yml:39-41` comments out macOS ARM64 testing.

### Solution

1. Investigate and fix the underlying bug #59
2. Re-enable macOS ARM64 CI testing
3. Ensure NEON implementations work correctly

### Implementation Steps

1. Review issue #59 for root cause
2. Reproduce on ARM64 (Apple Silicon or cross-compile)
3. Fix the NEON implementation bug
4. Uncomment ARM64 testing in CI
5. Verify all tests pass on ARM64

### Acceptance Criteria

- [ ] Bug #59 resolved
- [ ] macOS ARM64 tests passing in CI
- [ ] NEON SIMD active on Apple Silicon
- [ ] Performance verified (not falling back to scalar)

### Handoff

After Smith implements → Trainman verifies cross-platform → Deus runs full test suite → Neo merges
