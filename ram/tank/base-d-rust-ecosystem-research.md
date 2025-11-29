# Rust Ecosystem Research: base-d Migration Guide

**Research Date:** 2025-11-29
**Current State:** Rust 1.91.1, Edition 2021
**Target:** Latest stable ecosystem

---

## Executive Summary

You are on the current stable (1.91.1). Edition 2024 is stable and available since Rust 1.85 (February 2025). Upgrading to Edition 2024 is recommended - it brings significant improvements and `cargo fix` handles most migration automatically.

---

## 1. Current Rust Stable Version

**Latest Stable:** 1.91.1
**You have:** 1.91.1 - **You are current.**

Release schedule:
- Beta: 1.92.0 (expected December 11, 2025)
- Nightly: 1.93.0 (expected January 22, 2026)

---

## 2. Edition 2024 vs Edition 2021

### Edition 2024 Status: **STABLE** (since Rust 1.85, February 2025)

### Key Changes in Edition 2024

#### Language Changes
| Change | Impact | Migration |
|--------|--------|-----------|
| `env::set_var` / `env::remove_var` now unsafe | **Breaking** - must wrap in `unsafe {}` | `cargo fix` handles it |
| `gen` keyword reserved | Minor - can't use `gen` as identifier | Rename if used |
| `expr` macro fragment matches `const` and `_` | Expanded macro matching | Usually compatible |
| `missing_fragment_specifier` is hard error | Macros must specify fragment types | Fix macros |
| Never type `!` fallback changes | Edge cases in type inference | Usually compatible |
| RPIT lifetime capture improvements | More precise lifetime handling | May need annotations |
| Tail expression temporary scope changes | Variables drop differently in blocks | Review `if let` patterns |
| `unsafe_op_in_unsafe_fn` warns by default | Must use `unsafe {}` inside unsafe fns | Add blocks or allow lint |
| `export_name`, `link_section`, `no_mangle` require unsafe | FFI attribute changes | Wrap in unsafe block |

#### Prelude Additions
- `Future` and `IntoFuture` added to prelude
- `IntoIterator for Box<[T]>` behavior change

#### Reserved Syntax
- `#"foo"#` style strings reserved for future
- `##` tokens reserved

### New Features Available (All Editions, 1.85+)

| Feature | Description |
|---------|-------------|
| **Async closures** | `async \|\| {}` syntax - captures environment, returns futures |
| `AsyncFn` traits | `AsyncFn`, `AsyncFnMut`, `AsyncFnOnce` |
| `#[diagnostic::do_not_recommend]` | Control which trait impls appear in error messages |

---

## 3. Key Changes: 1.85 to 1.91

### Rust 1.85 (February 2025)
- Edition 2024 stable
- Async closures (`async || {}`)
- `#[diagnostic::do_not_recommend]`
- `powerpc64le-unknown-linux-musl` tier 2

### Rust 1.86 (April 2025)
- **Trait object upcasting** - coerce `&dyn Trait` to `&dyn Supertrait`
- `Vec::pop_if` stabilized

### Rust 1.87 (May 2025)
- `Vec::extract_if` stabilized
- `use<..>` syntax for lifetime bounds in trait functions
- Inline assembly: jumps to Rust code

### Rust 1.88 (June 2025)
- **Let chains** - `if let Some(x) = foo && x > 5 { }`
- **Naked functions** stabilized
- `Cell::update`
- `HashMap::extract_if`
- Cargo automatic cache cleanup

### Rust 1.89 (August 2025)
- `File::lock`, `File::try_lock`, etc. stabilized
- Improved const generics
- SIMD improvements
- Safer FFI

### Rust 1.90 (September 2025)
- **lld linker by default** on x86_64-unknown-linux-gnu (faster linking)
- Apple Intel (x86_64-apple-darwin) demoted to tier 2
- `MSG_NOSIGNAL` set for UnixStream
- `std::env::home_dir` falls back if HOME is empty

### Rust 1.91 (October 2025)
- `wasm_c_abi` warning is now hard error
  - **Action:** Upgrade wasm-bindgen to >= 0.2.89 if using
- `cenum_impl_drop_cast` is hard error (can't cast field-less enum with Drop to int)
- AArch64 Linux compiler optimized with ThinLTO + PGO

---

## 4. Cargo Improvements

### Stable Features
- **Workspace inheritance** - share versions, rust-version, deps across workspace
- **Workspace lints** - `[workspace.lints]` inherited by members
- **`--timings`** - detailed build time analysis
- Improved resolver for complex dependency graphs

### Recent/Nightly Features
- **Multi-package publishing** (cargo 1.90+, currently nightly)
- `cargo graph` command for dependency visualization
- 50% faster dependency resolution
- Smart conflict resolution

### Recommended Tool
- **cargo-autoinherit** - automatically DRYs workspace dependencies

---

## 5. Clippy Changes

### June 2025: Feature Freeze
- Focus on accuracy over new lints
- Fewer false positives
- Better edge case coverage

### Configuration
- `clippy.toml` or `.clippy.toml` for per-project config
- `avoid-breaking-exported-api = false` for library strictness
- Use `".."` to extend default lists instead of replacing

### Key Lint Groups
- `clippy::correctness` - deny-by-default, no false positives
- `clippy::restriction` - cherry-pick, don't enable whole group

---

## 6. Rustfmt Changes

### Style Editions (New in 2024)
Rustfmt now has **style editions** separate from Rust editions.

### 2024 Style Changes
| Change | Description |
|--------|-------------|
| Import sorting | New order: const, type, module (was alphabetic) |
| Natural number sort | `Thing8, Thing16, Thing32` instead of `Thing16, Thing32, Thing8` |

### Migration Options
1. **Adopt 2024 style** - let rustfmt reformat (one-time churn)
2. **Keep 2021 style** - add `style_edition = "2021"` to `rustfmt.toml`

---

## 7. Migration Checklist for base-d

### Pre-Migration
- [ ] Ensure on Rust 1.85+ (you have 1.91.1)
- [ ] Commit current state
- [ ] Review any `unsafe` usage
- [ ] Check for `gen` as identifier
- [ ] Review `if let` temporary patterns

### Migration Steps
```bash
# 1. Update Cargo.toml
edition = "2024"

# 2. Run automatic fixes
cargo fix --edition

# 3. Handle remaining issues
cargo check

# 4. Decide on rustfmt style
# Option A: Accept 2024 style (recommended)
cargo fmt

# Option B: Keep 2021 style
echo 'style_edition = "2021"' >> rustfmt.toml
```

### Post-Migration
- [ ] Run full test suite
- [ ] Check clippy with new edition
- [ ] Review any new warnings
- [ ] Update CI if needed

---

## Sources

- [Rust Changelogs](https://releases.rs/)
- [Rust 2024 Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2024/index.html)
- [Announcing Rust 1.85.0 and Rust 2024](https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/)
- [Announcing Rust 1.86.0](https://blog.rust-lang.org/2025/04/03/Rust-1.86.0/)
- [Rustfmt Style Edition](https://doc.rust-lang.org/edition-guide/rust-2024/rustfmt-style-edition.html)
- [Clippy Feature Freeze](https://blog.rust-lang.org/inside-rust/2025/06/21/announcing-the-clippy-feature-freeze/)
- [Cargo Changelog](https://doc.rust-lang.org/nightly/cargo/CHANGELOG.html)
