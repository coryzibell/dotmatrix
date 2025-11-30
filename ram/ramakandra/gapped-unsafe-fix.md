# Fixed: unsafe_op_in_unsafe_fn in gapped.rs

**Date:** 2025-11-30
**File:** `/home/w3surf/work/personal/code/base-d/src/simd/lut/gapped.rs`

## What Was Fixed

Removed the module-level `#![allow(unsafe_op_in_unsafe_fn)]` suppression and added explicit `unsafe {}` blocks inside all unsafe functions to comply with Rust Edition 2024 requirements.

## Changes Made

### Removed
- Line 16: `#![allow(unsafe_op_in_unsafe_fn)]` module-level suppression

### Functions Fixed (8 total)

All unsafe functions now have explicit `unsafe {}` blocks wrapping their bodies:

#### x86_64 SSSE3 Functions
1. `encode_ssse3` - Dispatcher function calling other unsafe functions
2. `encode_ssse3_5bit` - 5-bit encoding with SIMD intrinsics
3. `encode_ssse3_6bit` - 6-bit encoding with SIMD intrinsics
4. `encode_ssse3_4bit` - 4-bit encoding with SIMD intrinsics

#### aarch64 NEON Functions
5. `encode_neon` - Dispatcher function calling other unsafe functions
6. `encode_neon_5bit` - 5-bit encoding with NEON intrinsics
7. `encode_neon_6bit` - 6-bit encoding with NEON intrinsics
8. `encode_neon_4bit` - 4-bit encoding with NEON intrinsics

## Pattern Applied

Used **Option 1** from the learnings document: wrap entire function body in a single `unsafe {}` block. This is appropriate for these functions because:

- The entire function body consists of SIMD operations (intrinsics)
- All SIMD intrinsics (`_mm_*`, `vld1q_u8`, `vst1q_u8`, etc.) are inherently unsafe
- `get_unchecked` array access is unsafe
- No mix of safe and unsafe operations - it's all unsafe

## Verification

Both verification steps passed:

```bash
cargo check                                         # ✓ Compiles successfully
cargo clippy --all-targets --all-features -- -D warnings  # ✓ No warnings
```

## Notes

- This file was just added in a recent PR/commit
- It already had the suppression to avoid Edition 2024 issues
- Now properly fixed instead of suppressed
- All unsafe operations are now explicitly marked per Rust 2024 requirements
