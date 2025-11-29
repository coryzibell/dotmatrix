# Pattern: cfg-gated imports

**Ecosystem:** Rust
**Category:** Cross-platform compilation
**Severity:** Error (on non-matching targets)

## What It Catches

When a type is defined with `#[cfg(target_arch = "...")]` but imported without the same gate, compilation fails on other architectures.

```rust
// common.rs
#[cfg(target_arch = "x86_64")]
pub struct RangeInfo { ... }

// base64.rs - ERROR on aarch64!
use super::common::RangeInfo;  // RangeInfo doesn't exist on aarch64
```

## The Error

```
error[E0432]: unresolved import `super::common::RangeInfo`
  --> src/simd/lut/base64.rs:17:32
   |
17 | use super::common::{CharRange, RangeInfo, RangeStrategy};
   |                                ^^^^^^^^^ no `RangeInfo` in `simd::lut::common`
   |
note: found an item that was configured out
  --> src/simd/lut/common.rs:27:19
   |
25 | #[cfg(target_arch = "x86_64")]
   |       ---------------------- the item is gated behind the `x86_64` feature
```

## How to Fix

### Option 1: Gate the import (recommended)

```rust
use super::common::{CharRange, RangeStrategy};

#[cfg(target_arch = "x86_64")]
use super::common::RangeInfo;
```

### Option 2: Gate the entire use block

```rust
#[cfg(target_arch = "x86_64")]
use super::common::{CharRange, RangeInfo, RangeStrategy};

#[cfg(not(target_arch = "x86_64"))]
use super::common::{CharRange, RangeStrategy};
```

### Option 3: Define on all platforms with different implementations

```rust
// common.rs
#[cfg(target_arch = "x86_64")]
pub struct RangeInfo { /* x86_64 fields */ }

#[cfg(target_arch = "aarch64")]
pub struct RangeInfo { /* aarch64 fields */ }
```

## Why This Happens During Edition Migration

1. You run `cargo fix --edition` on your dev machine (e.g., x86_64 Linux)
2. The tool only processes code paths active on your current target
3. Code gated for other architectures isn't analyzed or fixed
4. CI runs on multiple platforms and finds the unfixed code

## Prevention

After any Edition migration:

1. Search for `#[cfg(target_arch` in the codebase
2. For each gated type/function, verify imports are also gated
3. Cross-compile check if possible:
   ```bash
   rustup target add aarch64-apple-darwin
   cargo check --target aarch64-apple-darwin
   ```

## Files Affected in base-d

- `src/simd/lut/common.rs` - `RangeInfo` gated to x86_64
- `src/simd/lut/base64.rs` - import needed conditional gate
