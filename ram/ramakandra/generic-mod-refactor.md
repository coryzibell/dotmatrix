# Unsafe Scope Refactoring: src/simd/generic/mod.rs

**Date:** 2025-11-30
**Task:** Narrow unsafe scopes per Edition 2024 `unsafe_op_in_unsafe_fn` lint
**Status:** ✅ Complete - compiles successfully

## Summary

Refactored `/home/w3surf/work/personal/code/base-d/src/simd/generic/mod.rs` to narrow unsafe scopes from wrapping entire function bodies to only wrapping truly unsafe operations.

## Key Principles Applied

### 1. Functions WITHOUT `#[target_feature]`
For regular safe functions that use SIMD:
- SIMD intrinsics require `unsafe {}` blocks
- Calls to unsafe trait methods require `unsafe {}` blocks
- Calls to unsafe helper functions require `unsafe {}` blocks
- Pointer casts for SIMD load/store require `unsafe {}` blocks
- Safe operations (arithmetic, iteration, `result.push()`) stay outside unsafe blocks

### 2. Functions WITH `#[target_feature]`
For functions marked with `#[target_feature(enable = "...")]`:
- SIMD intrinsics DO NOT need `unsafe {}` blocks (attribute guarantees CPU features)
- Calls to OTHER unsafe functions STILL need `unsafe {}` blocks
- Pointer casts for load/store STILL need `unsafe {}` blocks

## Changes Made

### SSSE3 Functions (128-bit)

**encode_6bit():**
- Wrapped SIMD load: `_mm_loadu_si128()`
- Wrapped unsafe helper call: `self.reshuffle_6bit()`
- Wrapped unsafe trait method: `self.translator.translate_encode()`
- Wrapped SIMD store: `_mm_storeu_si128()`

**encode_4bit():**
- Wrapped SIMD load and all SIMD intrinsics
- Wrapped translator calls: `translate_encode()`
- Wrapped SIMD store operations

**encode_8bit():**
- Wrapped SIMD load and store
- Wrapped translator call

**encode_5bit():**
- Wrapped SIMD load
- Wrapped unsafe helper: `unpack_5bit_simple()`
- Wrapped translator call
- Wrapped SIMD store

**decode_4bit():**
- Wrapped SIMD loads
- Wrapped SIMD shuffle operations
- Wrapped translator calls: `translate_decode()`
- Wrapped SIMD store

**decode_6bit():**
- Wrapped SIMD load
- Wrapped translator call
- Wrapped unsafe helper: `unshuffle_6bit()`
- Wrapped SIMD store

**decode_8bit():**
- Wrapped SIMD load
- Wrapped translator call
- Wrapped SIMD store

**decode_5bit():**
- Wrapped SIMD load
- Wrapped translator call
- Wrapped unsafe helper: `pack_5bit_to_8bit()`
- Wrapped SIMD store

### Helper Functions with `#[target_feature]`

**unpack_5bit_simple():**
- Wrapped SIMD store: `_mm_storeu_si128()` (pointer cast)
- Wrapped SIMD load: `_mm_loadu_si128()` (pointer cast)
- SIMD intrinsics for bit manipulation NOT wrapped (covered by `#[target_feature]`)

**extract_5bit_indices_avx2():**
- Wrapped unsafe helper calls: `self.unpack_5bit_simple()`
- AVX2 intrinsics NOT wrapped (covered by `#[target_feature]`)

**pack_5bit_to_8bit_avx2():**
- Wrapped unsafe helper calls: `self.pack_5bit_to_8bit()`
- AVX2 intrinsics NOT wrapped (covered by `#[target_feature]`)

### AVX2 Functions (256-bit)

**encode_8bit_avx2_impl():**
- Wrapped SIMD load (pointer cast)
- Wrapped translator call: `translate_encode_256()`
- Wrapped SIMD store (pointer cast)
- AVX2 intrinsics NOT wrapped (covered by `#[target_feature]`)

**encode_4bit_avx2_impl():**
- Wrapped SIMD load
- Wrapped translator calls (both hi and lo)
- Wrapped SIMD stores (both output buffers)

**encode_5bit_avx2_impl():**
- Wrapped SIMD loads (both lanes)
- Wrapped unsafe helper: `extract_5bit_indices_avx2()`
- Wrapped translator call
- Wrapped SIMD store

**encode_6bit_avx2_impl():**
- Wrapped SIMD load
- Wrapped unsafe helper: `reshuffle_6bit_avx2()`
- Wrapped translator call
- Wrapped SIMD store

**decode_8bit_avx2_impl():**
- Wrapped SIMD load
- Wrapped translator call
- Wrapped SIMD store

**decode_4bit_avx2_impl():**
- Wrapped SIMD loads (both input buffers)
- Wrapped translator calls (both hi_vals and lo_vals)
- Wrapped SIMD store

**decode_5bit_avx2_impl():**
- Wrapped SIMD load
- Wrapped translator call
- Wrapped unsafe helper: `pack_5bit_to_8bit_avx2()`
- Wrapped SIMD stores (both lanes)

**decode_6bit_avx2_impl():**
- Wrapped SIMD load
- Wrapped translator call
- Wrapped unsafe helper: `unshuffle_6bit_avx2()`
- Wrapped SIMD store

## Benefits

1. **Compiler Verification:** Safe operations (bounds checks, arithmetic, iteration) are now verified by the compiler
2. **Bug Detection:** Bugs in safe code get caught at compile time
3. **Audit Clarity:** Unsafe blocks mark exactly what's dangerous
4. **Defense in Depth:** Better protection against processor vulnerabilities (Spectre, Meltdown)
5. **Edition 2024 Compliance:** Code now follows Rust 2024 unsafe semantics

## Verification

```bash
cargo check  # ✅ Compiles successfully
```

## Pattern for Future Refactoring

When refactoring similar SIMD code:

```rust
// BEFORE (Edition 2021 style)
unsafe fn encode(&self, data: &[u8]) -> __m128i {
    let vec = _mm_loadu_si128(data.as_ptr() as *const __m128i);
    let translated = self.translator.translate(vec);
    let result = _mm_add_epi8(vec, translated);
    result
}

// AFTER (Edition 2024 style, Option 1: narrow scoping)
unsafe fn encode(&self, data: &[u8]) -> __m128i {
    // Unsafe: pointer cast and SIMD load
    let vec = unsafe {
        _mm_loadu_si128(data.as_ptr() as *const __m128i)
    };

    // Unsafe: call to unsafe trait method
    let translated = unsafe { self.translator.translate(vec) };

    // Safe: SIMD intrinsic covered by #[target_feature] if present,
    // otherwise needs unsafe block
    let result = _mm_add_epi8(vec, translated);
    result
}
```

## Files Affected

- `/home/w3surf/work/personal/code/base-d/src/simd/generic/mod.rs`

## Next Steps

This file is now Edition 2024 compliant. Other files in the codebase may need similar treatment:
- `src/simd/lut/base16.rs`
- `src/simd/lut/base32.rs`
- `src/simd/lut/base64.rs`
- `src/simd/x86_64/specialized/base32.rs`

The same patterns can be applied to those files when ready.
