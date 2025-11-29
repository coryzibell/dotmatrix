# base-d Clippy CI Failure Analysis

**Date:** 2025-11-29
**Issue:** Clippy passes locally but fails in CI

## Root Cause

Mismatch between local pre-push hook and CI clippy configuration.

### Local Pre-Push Hook
**Location:** `/home/w3surf/work/personal/code/base-d/.git/hooks/pre-push`
```bash
cargo clippy -- -D warnings
```
- No `--all-targets` flag (only checks lib/bin, skips tests)
- No `--all-features` flag

### CI Configuration
**Workflow:** `.github/workflows/the-matrix-has-you.yml` (line 54)
```bash
cargo clippy --all-targets --all-features -- -D warnings
```
- Includes `--all-targets` (checks tests, benches, examples, etc.)
- Includes `--all-features`

## The Failure

When running with `--all-targets`, clippy checks the test files and finds:

**File:** `tests/cli.rs` (line 9)
```rust
Command::cargo_bin("base-d").unwrap()
```

**Error:**
```
error: use of deprecated associated function `assert_cmd::Command::cargo_bin`:
incompatible with a custom cargo build-dir, see instead `cargo::cargo_bin_cmd!`
```

The deprecation warning is treated as an error due to `-D warnings`.

## The Fix

Update `tests/cli.rs` line 8-10 from:
```rust
fn base_d() -> Command {
    Command::cargo_bin("base-d").unwrap()
}
```

To:
```rust
fn base_d() -> Command {
    Command::cargo_bin("base-d").unwrap()
}
```

Actually, need to check what the recommended replacement is. The error message says "see instead `cargo::cargo_bin_cmd!`" but this isn't clear.

## Verification Command

Run this locally to reproduce CI behavior:
```bash
cd /home/w3surf/work/personal/code/base-d
cargo clippy --all-targets --all-features -- -D warnings
```

## Recommendation

1. Fix the deprecated `cargo_bin()` usage in `tests/cli.rs`
2. Update pre-push hook to match CI exactly:
   ```bash
   cargo clippy --all-targets --all-features -- -D warnings
   ```
   This prevents future CI surprises.
