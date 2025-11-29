# base-d Upgrade Plan

## Analysis Summary

**Current State:**
- Rust Edition 2021, toolchain 1.91.1
- 6 dependencies requiring updates
- No security vulnerabilities

**Target State:**
- Rust Edition 2024
- All dependencies at latest versions

## Constraints Identified

### Edition 2024 Breaking Changes
1. **`env::set_var` now unsafe** - Found in 3 test functions (`src/encoders/algorithms/errors.rs` lines 321, 336, 355)
2. **`gen` keyword reserved** - No conflicts found in codebase

### Dependency Code Changes Required
1. **rand 0.8 -> 0.9**: `thread_rng()` -> `rng()` in 4 locations (`src/cli/commands.rs` lines 60, 93, 106, 195)
2. **criterion 0.5 -> 0.7**: `black_box` import path change (already using `criterion::black_box` - may need verification)

### Zero-Code Dependencies
- brotli 7.0 -> 8.0.2
- dirs 5.0.1 -> 6.0.0
- crossterm 0.28.1 -> 0.29.0
- terminal_size 0.3.0 -> 0.4.3

---

## Phased Upgrade Plan

### Phase 1: Zero-Code Dependency Updates (Single PR)

**Rationale:** These updates have no code changes and can be batched. Low risk, quick wins.

**Changes:**
```toml
dirs = "6.0"
crossterm = "0.29"
terminal_size = "0.4"
brotli = "8.0"
```

**Verification:** `cargo build && cargo test`

**PR Title:** `deps: update dirs, crossterm, terminal_size, brotli`

---

### Phase 2: rand 0.9 Migration (Separate PR)

**Rationale:** Requires code changes. Keep isolated for clear bisect history.

**Cargo.toml:**
```toml
rand = "0.9"
```

**Code Changes in `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs`:**

| Line | Before | After |
|------|--------|-------|
| 60 | `rand::thread_rng()` | `rand::rng()` |
| 93 | `rand::thread_rng()` | `rand::rng()` |
| 106 | `rand::thread_rng()` | `rand::rng()` |
| 195 | `rand::thread_rng()` | `rand::rng()` |

**Verification:** `cargo build && cargo test`

**PR Title:** `deps: migrate rand to 0.9`

---

### Phase 3: criterion 0.7 Migration (Separate PR)

**Rationale:** Dev-only dependency. Isolated change. May require import path adjustment.

**Cargo.toml:**
```toml
criterion = { version = "0.7", features = ["html_reports"] }
```

**Verification:** `cargo bench --no-run` (compile check), optionally run benchmarks

**PR Title:** `deps(dev): update criterion to 0.7`

---

### Phase 4: Edition 2024 Migration (Final PR)

**Rationale:** Edition change affects compilation of entire crate. Must come after dependency updates to ensure compatibility. The `env::set_var` calls are in test code only.

**Cargo.toml:**
```toml
edition = "2024"
```

**Code Changes in `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/errors.rs`:**

Wrap `env::set_var` calls in unsafe blocks (lines 321, 336, 355):

```rust
// Before
std::env::set_var("NO_COLOR", "1");

// After
// SAFETY: Test-only code, single-threaded test execution
unsafe { std::env::set_var("NO_COLOR", "1"); }
```

Also update `env::remove_var` calls (lines 331, 350, 364).

**Pre-migration:** Run `cargo fix --edition` to catch any additional changes

**Verification:** `cargo build && cargo test && cargo bench --no-run`

**PR Title:** `chore: migrate to Rust edition 2024`

---

## Execution Order

```
Phase 1 (zero-code deps)
    |
    v
Phase 2 (rand 0.9)
    |
    v
Phase 3 (criterion 0.7)
    |
    v
Phase 4 (edition 2024)
```

**Why this order:**
1. Zero-code deps first - quick confidence builder, catches any unexpected API breaks
2. rand before edition - rand 0.9 was built for Edition 2021+, ensure it works before edition change
3. criterion before edition - dev tooling stable before edition migration
4. Edition last - all deps proven compatible, only edition-specific changes remain

---

## Handoff to Smith

**Implementation order by component:**

1. **PR 1 (Cargo.toml only):** Update dirs, crossterm, terminal_size, brotli versions
2. **PR 2 (Cargo.toml + src/cli/commands.rs):** rand migration
3. **PR 3 (Cargo.toml + benches/encoding.rs if needed):** criterion migration
4. **PR 4 (Cargo.toml + src/encoders/algorithms/errors.rs):** Edition 2024

Each PR should be mergeable independently. CI must pass before proceeding to next phase.

---

## Risk Assessment

| Phase | Risk | Mitigation |
|-------|------|------------|
| 1 | Low | No code changes, well-tested deps |
| 2 | Low | Simple API rename, 4 lines |
| 3 | Low | Dev-only, benchmarks optional |
| 4 | Medium | Edition changes can have subtle effects; `cargo fix --edition` helps |

**Total estimated effort:** ~1 hour implementation, spread across 4 PRs
