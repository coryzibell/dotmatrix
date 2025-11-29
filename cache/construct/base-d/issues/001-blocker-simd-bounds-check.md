## Add bounds checks to SIMD get_unchecked calls

**Type:** `issue`
**Labels:** `identity:smith`, `blocker`, `security`

### Context

From Construct review of `base-d` project. Cypher identified critical security vulnerability in SIMD code.

**Source:** `~/.matrix/cache/construct/base-d/security-findings.md`

### Problem

`src/simd/lut/large.rs` uses `get_unchecked()` extensively without runtime assertions to verify bounds invariants hold.

```rust
// Current pattern - trusts SIMD logic never miscalculates offsets
*data.get_unchecked(offset),
*data.get_unchecked(offset + 1),
*data.get_unchecked(offset + 2),
```

One bug in index calculation = reading arbitrary memory. Out-of-bounds reads could leak sensitive data, cause crashes, or enable information disclosure.

### Solution

Add debug assertions before all `get_unchecked` calls to verify bounds at runtime during development/testing.

```rust
debug_assert!(offset + N < data.len(), "SIMD offset out of bounds");
```

### Implementation Steps

1. Grep for all `get_unchecked` usage in `src/simd/`
2. Add `debug_assert!` before each unsafe index operation
3. Run tests with `RUSTFLAGS="-C debug-assertions=on"`
4. Add MIRI testing for unsafe blocks if not already present

### Acceptance Criteria

- [ ] All `get_unchecked` calls have debug assertions
- [ ] Tests pass with debug assertions enabled
- [ ] No new unsafe code introduced
- [ ] Cypher re-audits after fix

### Handoff

After Smith implements → Deus verifies → Cypher re-audits → Neo merges
