---
title: "chore(deps): migrate criterion 0.5 to 0.7"
labels:
  - dependencies
  - identity:smith
priority: P3
---

## Context

Part of the Cycle upgrade plan for base-d. criterion is a dev dependency for benchmarks.

## Migration

**Dependency:** criterion 0.5.1 → 0.7.0

**Breaking change:** `criterion::black_box` moved to `std::hint::black_box`

## Code Changes

**File:** `benches/encoding.rs`

```rust
// Before
use criterion::black_box;

// After
use std::hint::black_box;
```

Approximately 2 lines affected (import change).

## Steps

1. Update criterion version in `Cargo.toml` to `"0.7"`
2. Update black_box import to use std::hint
3. Run `cargo bench` to verify benchmarks still work

## Acceptance Criteria

- [ ] criterion updated to 0.7.x
- [ ] black_box import updated
- [ ] Benchmarks compile and run

## Reference

Migration guide: `~/.matrix/artifacts/cycles/rust/dependencies/criterion/0.5.1-to-0.7.0.md`

## Handoff

Smith implements → Deus verifies benchmarks run
