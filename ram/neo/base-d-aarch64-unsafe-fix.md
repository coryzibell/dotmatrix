# base-d aarch64 unsafe block fix - Context for Mac session

## Status
Paused. Moving to ARM Mac where aarch64 code can be tested directly.

## The Problem
Mac CI fails with "unnecessary unsafe block" warnings in aarch64 NEON code, but we can't properly test/fix on x86_64 Linux because:
1. The aarch64 code is `#[cfg(target_arch = "aarch64")]` gated - doesn't compile on x86
2. We've been guessing at the fix and breaking things

## What We Know

### The Original Error (from Mac CI)
```
warning: unnecessary `unsafe` block
   --> src/simd/aarch64/specialized/base16.rs:261:5
```

Functions have pattern like:
```rust
#[cfg(target_arch = "aarch64")]
#[target_feature(enable = "neon")]
unsafe fn decode_nibble_chars_neon(chars: uint8x16_t) -> uint8x16_t {
    use std::arch::aarch64::*;

    unsafe {  // <-- Mac CI says this is unnecessary
        let zero_30 = vdupq_n_u8(0x30);
        // ...
    }
}
```

### Conflicting Information
1. Mac CI says the inner `unsafe {}` blocks are UNNECESSARY
2. But when we removed them, we got E0133 errors saying unsafe blocks ARE REQUIRED
3. This suggests Rust 2024 edition behavior differs from what we expected

### Current State
- Repo reset to commit `7f8a0a03c7c4f07ff5b5b336a6cc7aedbd2f1d28`
- Force pushed to overwrite bad attempts
- All `src/simd/` changes reverted

## Files That Need Work
From the original CI errors:
- `src/simd/aarch64/specialized/base16.rs` - line 261
- `src/simd/aarch64/specialized/base32.rs` - lines 227, 246
- `src/simd/aarch64/specialized/base64.rs` - lines 131, 333, 358, 395+
- `src/simd/aarch64/generic.rs`
- `src/simd/lut/base16.rs` - aarch64 sections
- `src/simd/lut/base32.rs` - aarch64 sections
- `src/simd/lut/base64.rs` - aarch64 sections
- `src/simd/lut/gapped.rs` - aarch64 sections

## What To Do On Mac
1. `cargo clippy -- -D warnings` to see actual errors
2. Fix the pattern - likely just remove the outer `unsafe {}` wrapper while keeping intrinsics unwrapped
3. Test with `cargo test`
4. Commit with `mx commit "fix unnecessary unsafe blocks in aarch64 NEON code" -p`

## Lint Doc Location
Updated lint documentation at:
`~/.matrix/artifacts/cycles/rust/lints/unsafe-op-in-unsafe-fn.md`

## Key Insight
On Mac with actual aarch64, we can run clippy and see exactly what the compiler wants. No more guessing.
