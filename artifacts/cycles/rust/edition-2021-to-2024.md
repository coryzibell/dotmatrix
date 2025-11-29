# Rust Edition 2021 → 2024 Migration Guide

**Created:** 2025-11-29
**Requires:** Rust 1.85+

## Overview

Edition 2024 shipped with Rust 1.85 (February 2025). Migration is straightforward with `cargo fix --edition`.

## Breaking Changes

| Change | Action Required |
|--------|-----------------|
| `env::set_var` / `env::remove_var` unsafe | Wrap in `unsafe {}` block |
| `unsafe_op_in_unsafe_fn` warns by default | Add explicit `unsafe` blocks inside unsafe fns |
| `gen` reserved keyword | Rename any `gen` identifiers |
| FFI attributes need unsafe | `#[no_mangle]`, `#[export_name]` in unsafe blocks |
| RPIT lifetime capture rules | May need explicit lifetime bounds |
| `impl Trait` in associated types | Stricter type inference |

## Migration Steps

1. **Update rust-version in Cargo.toml** (if specified)
   ```toml
   rust-version = "1.85"
   ```

2. **Run cargo fix**
   ```bash
   cargo fix --edition
   ```

3. **Update edition in Cargo.toml**
   ```toml
   edition = "2024"
   ```

4. **Review changes** - especially:
   - Any new `unsafe` blocks
   - Renamed identifiers
   - Lifetime annotations

5. **Run tests**
   ```bash
   cargo test
   ```

## Rustfmt Changes

Edition 2024 changes import sorting style. Options:

1. **Accept new style** (recommended)
   ```bash
   cargo fmt
   ```
   Commit the one-time reformatting.

2. **Keep 2021 style**
   Add to `rustfmt.toml`:
   ```toml
   style_edition = "2021"
   ```

## New Features Available

With edition 2024, these stabilized features become idiomatic:

- **Let chains**: `if let Some(x) = foo && x > 5 { }`
- **Async closures**: `async || { ... }`
- **Trait upcasting**: `&dyn Trait` → `&dyn Supertrait`
- **Native file locking**: `File::lock()`, `File::try_lock()`

## Common Issues

### `env::set_var` unsafe

```rust
// Before (2021)
std::env::set_var("KEY", "value");

// After (2024)
unsafe { std::env::set_var("KEY", "value"); }
```

### `gen` keyword reserved

```rust
// Before (2021)
fn gen() { }

// After (2024)
fn generate() { }  // or use raw identifier: r#gen
```

## References

- [Rust 2024 Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2024/index.html)
- [Announcing Rust 1.85.0](https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/)
