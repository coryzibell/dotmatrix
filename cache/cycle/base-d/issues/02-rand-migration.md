---
title: "chore(deps): migrate rand 0.8 to 0.9"
labels:
  - dependencies
  - identity:smith
priority: P2
---

## Context

Part of the Cycle upgrade plan for base-d. rand 0.9 has API changes requiring code updates.

## Migration

**Dependency:** rand 0.8.5 → 0.9.2

**Breaking change:** `thread_rng()` renamed to `rng()`

## Code Changes

**File:** `src/cli/commands.rs`

Replace all occurrences:
```rust
// Before
use rand::thread_rng;
thread_rng()

// After
use rand::rng;
rng()
```

Approximately 4 lines affected.

## Steps

1. Update rand version in `Cargo.toml` to `"0.9"`
2. Update imports: `thread_rng` → `rng`
3. Update function calls: `thread_rng()` → `rng()`
4. Run `cargo test`

## Acceptance Criteria

- [ ] rand updated to 0.9.x
- [ ] All `thread_rng` calls migrated
- [ ] All tests pass
- [ ] No deprecation warnings

## Reference

Migration guide: `~/.matrix/artifacts/cycles/rust/dependencies/rand/0.8.5-to-0.9.2.md`

## Handoff

Smith implements → Deus verifies
