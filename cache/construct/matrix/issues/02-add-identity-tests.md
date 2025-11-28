# Add tests for internal/identity package

**Type:** `issue`
**Labels:** `identity:deus`, `blocker`, `testing`
**Status:** open
**GitHub:** [#16](https://github.com/coryzibell/matrix/issues/16)

---

# Add tests for internal/identity package






From Construct review of `matrix` project. Deus identified critical test coverage gap during testing review.

**Source:** Deus's test coverage analysis

## Problem

Test coverage is at 3%. Only `internal/ram` has tests. The `internal/identity` package has zero test coverage.

This package handles:
- Identity validation (`IsValid`)
- RAM path resolution (`RAMPath`)
- Identity listing

These are core functions that other commands depend on.

## Solution

Write comprehensive tests for `internal/identity` package covering:
- All 27 valid identities recognized
- Invalid identity names rejected
- RAM paths resolve correctly
- Edge cases (empty string, special characters, case sensitivity)

## Implementation Steps

1. Create `internal/identity/identity_test.go`
2. Write table-driven tests for `IsValid()`
3. Write tests for `RAMPath()`
4. Write tests for identity listing functions
5. Verify edge cases and error conditions
6. Run coverage report to confirm improvement

## Acceptance Criteria

- [ ] `internal/identity` has >80% test coverage
- [ ] All 27 identities validated in tests
- [ ] Invalid inputs properly rejected
- [ ] Tests pass on all platforms (linux, darwin, windows)
- [ ] `go test ./...` passes

## Handoff

1. Deus writes the tests
2. Kid runs `go test ./...` to verify
3. Neo reviews and merges

---

*Last synced: Nov 26, 2025 at 09:21 PM*