# base-d Dependency Update Plan

**Date:** 2025-11-29
**Project:** /home/w3surf/work/personal/code/base-d
**Current Rust:** 1.91.1
**Target Edition:** 2024

---

## Confirmed Code Impact

### HIGH PRIORITY: rand 0.8 → 0.9

**Locations affected:**
- `src/cli/commands.rs:60` - `rand::thread_rng()`
- `src/cli/commands.rs:93` - `rand::thread_rng()`
- `src/cli/commands.rs:106` - `rand::thread_rng()`
- `src/cli/commands.rs:195` - `rand::thread_rng()`

**Required changes:**
```rust
// Old (0.8)
let mut rng = rand::thread_rng();

// New (0.9 - Edition 2024 compatible)
let mut rng = rand::rng();  // Simplified name
```

**Migration guide:** `/home/w3surf/.matrix/artifacts/cycles/rust/dependencies/rand/0.8.5-to-0.9.2.md`

---

### HIGH PRIORITY: criterion 0.5 → 0.7

**Locations affected:**
- `benches/encoding.rs:2` - `use criterion::{black_box, ...}`
- `benches/encoding.rs:44-152` - Multiple `black_box()` calls (9 occurrences)

**Required changes:**
```rust
// Old (0.5)
use criterion::{black_box, criterion_group, criterion_main, BenchmarkId, Criterion, Throughput};
b.iter(|| encode(black_box(data), black_box(&dictionary)));

// New (0.7)
use criterion::{criterion_group, criterion_main, BenchmarkId, Criterion, Throughput};
use std::hint::black_box;
b.iter(|| encode(black_box(data), black_box(&dictionary)));
```

**Migration guide:** `/home/w3surf/.matrix/artifacts/cycles/rust/dependencies/criterion/0.5.1-to-0.7.0.md`

---

### LOW RISK: No Code Changes Needed

These can be updated directly without code changes:

✅ **brotli:** 7.0.0 → 8.0.2
- No FFI usage detected
- Guide: `/home/w3surf/.matrix/artifacts/cycles/rust/dependencies/brotli/7.0.0-to-8.0.2.md`

✅ **dirs:** 5.0.1 → 6.0.0
- No API changes
- Guide: `/home/w3surf/.matrix/artifacts/cycles/rust/dependencies/dirs/5.0.1-to-6.0.0.md`

✅ **crossterm:** 0.28.1 → 0.29.0
- Semver-minor, API compatible
- Guide: `/home/w3surf/.matrix/artifacts/cycles/rust/dependencies/crossterm/0.28.1-to-0.29.0.md`

✅ **terminal_size:** 0.3.0 → 0.4.3
- No deprecated functions used (confirmed via grep)
- Guide: `/home/w3surf/.matrix/artifacts/cycles/rust/dependencies/terminal_size/0.3.0-to-0.4.3.md`

---

## Recommended Update Sequence

### Phase 1: Safe Updates (No Code Changes)
```bash
cargo update brotli --precise 8.0.2
cargo update dirs --precise 6.0.0
cargo update crossterm --precise 0.29.0
cargo update terminal_size --precise 0.4.3
cargo test
```

### Phase 2: rand Migration (Production Code)
1. Update Cargo.toml: `rand = "0.9"`
2. Update source code:
   - `src/cli/commands.rs`: Replace 4 instances of `thread_rng()` with `rng()`
3. Test random selection functionality

### Phase 3: criterion Migration (Dev/Bench)
1. Update Cargo.toml: `criterion = "0.7"`
2. Update benchmark code:
   - `benches/encoding.rs`: Add `use std::hint::black_box;`
   - Remove `black_box` from criterion import
3. Run benchmarks to verify

### Phase 4: Transitive Updates
Once direct deps are updated, run:
```bash
cargo update  # Pull in all transitive updates
cargo test
cargo bench
```

---

## Edition 2024 Compatibility

All target versions are Edition 2024 compatible:
- ✅ rand 0.9 - Designed for Edition 2024 (`gen` → `random`)
- ✅ criterion 0.7 - Edition 2021, works with 2024
- ✅ brotli 8.0 - No edition issues
- ✅ dirs 6.0 - No edition issues
- ✅ crossterm 0.29 - No edition issues
- ✅ terminal_size 0.4 - No edition issues

---

## Testing Checklist

After each phase:
- [ ] `cargo check` passes
- [ ] `cargo test` passes
- [ ] `cargo bench` passes (after criterion update)
- [ ] CLI commands work (test random selection)
- [ ] No new warnings

---

## Rollback Plan

If issues arise:
```bash
git checkout Cargo.lock
cargo build
```

Migration guides cached in:
`/home/w3surf/.matrix/artifacts/cycles/rust/dependencies/`

---

**Total code changes required:**
- **Production:** 4 lines in `src/cli/commands.rs` (rand)
- **Benchmarks:** 2 lines in `benches/encoding.rs` (criterion)
- **Dependencies:** 6 Cargo.toml updates

**Estimated time:** 15-20 minutes
**Risk level:** LOW (isolated changes, good test coverage assumed)
