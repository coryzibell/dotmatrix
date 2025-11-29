---
title: "chore: upgrade to Rust Edition 2024"
labels:
  - enhancement
  - identity:smith
priority: P2
---

## Context

Final step of the Cycle upgrade plan for base-d. Edition 2024 brings new language features and stricter safety requirements.

## Migration

**Edition:** 2021 → 2024

**Key changes:**
- `env::set_var` and `env::remove_var` now require `unsafe`
- `gen` is a reserved keyword
- Stricter lifetime capture in RPIT

## Code Changes

**File:** `src/encoders/algorithms/errors.rs` (test code only)

The `env::set_var` and `env::remove_var` calls in tests need `unsafe` blocks:

```rust
// Before
std::env::set_var("NO_COLOR", "1");
std::env::remove_var("NO_COLOR");

// After
unsafe { std::env::set_var("NO_COLOR", "1"); }
unsafe { std::env::remove_var("NO_COLOR"); }
```

Approximately 6 lines affected.

## Steps

1. Run `cargo fix --edition` to auto-fix what it can
2. Manually wrap any remaining `env::set_var`/`env::remove_var` in `unsafe`
3. Update `edition` in `Cargo.toml` to `"2024"`
4. Run `cargo fmt` (style changes in Edition 2024)
5. Run `cargo test`
6. Run `cargo clippy`

## Acceptance Criteria

- [ ] Edition updated to 2024 in Cargo.toml
- [ ] All unsafe blocks added where needed
- [ ] All tests pass
- [ ] No clippy warnings
- [ ] Code formatted with new style

## Reference

Migration guide: `~/.matrix/artifacts/cycles/rust/edition-2021-to-2024.md`

## Handoff

Smith implements → Deus verifies full test suite
