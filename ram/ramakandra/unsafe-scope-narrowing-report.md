# Unsafe Scope Narrowing - Edition 2024 Migration

**Date:** 2025-11-30
**Task:** Refactor 4 files to narrow unsafe scopes following Option 1 from `unsafe-op-in-unsafe-fn.md`

## Summary

Successfully refactored all 4 files to minimize unsafe scope according to RFC 2585's intent. The compiler can now verify safe code is actually safe, improving security against processor vulnerabilities (Spectre, Meltdown).

## Changes by File

### 1. `/home/w3surf/work/personal/code/base-d/src/simd/lut/base32.rs`

**Functions refactored:**
- `encode_neon_base32()` - NEON base32 encoding (aarch64)
- `encode_ssse3_range_reduction_5bit()` - SSE base32 encoding (x86_64)
- `encode_avx512_vbmi_base32()` - AVX-512 base32 encoding (x86_64)
- `decode_ssse3_multi_range_5bit()` - SSE base32 decoding (x86_64)
- `unpack_5bit_ssse3()` - SIMD-accelerated unpacking
- `decode_ssse3_base32_rfc4648()` - SSE RFC4648 decoding (x86_64)
- `decode_neon_base32_rfc4648()` - NEON RFC4648 decoding (aarch64)

**Pattern applied:**
- Removed whole-body `unsafe {}` wrapper
- Created targeted `unsafe {}` blocks for:
  - SIMD intrinsics (loads, stores, shuffles, arithmetic)
  - `get_unchecked()` array access
  - Pointer arithmetic
- Left safe: bit manipulation, iteration, `result.push()`, arithmetic, conditionals

**Example transformation:**
```rust
// Before
unsafe fn encode_neon_base32(&self, data: &[u8], result: &mut String) {
    unsafe {
        // entire function body
    }
}

// After
unsafe fn encode_neon_base32(&self, data: &[u8], result: &mut String) {
    // Safe: bounds checks, arithmetic
    const BLOCK_SIZE: usize = 5;
    if data.len() < BLOCK_SIZE { ... }

    // Unsafe: NEON intrinsics
    let lut_tables = unsafe {
        vld1q_u8(self.encode_lut.as_ptr())
    };

    // Unsafe: unchecked indexing
    let bytes = unsafe {
        [*data.get_unchecked(offset), ...]
    };

    // Safe: bit manipulation
    let mut indices = [0u8; 16];
    indices[0] = (bytes[0] >> 3) & 0x1F;

    // Safe: iteration, push
    for &byte in &output_buf[0..8] {
        result.push(byte as char);
    }
}
```

### 2. `/home/w3surf/work/personal/code/base-d/src/simd/translate.rs`

**No changes required.**

Functions already use `#[target_feature]` attribute which makes SIMD intrinsics safe without nested unsafe blocks. This is correct according to Rust's safety model.

### 3. `/home/w3surf/work/personal/code/base-d/src/simd/x86_64/specialized/base256.rs`

**Functions refactored:**
- `encode()` - Runtime dispatch wrapper
- `decode()` - Runtime dispatch wrapper
- `encode_avx2_impl()` - AVX2 encoding implementation
- `encode_ssse3_impl()` - SSSE3 encoding implementation

**Pattern applied:**
- In dispatch functions: narrow unsafe to just the call to `target_feature` functions
- In implementation functions: separate SIMD ops from safe LUT lookups
- Left safe: iteration, HashMap lookups, `result.push()`, bounds checks

**Example transformation:**
```rust
// Before
unsafe {
    if is_x86_feature_detected!("avx2") {
        encode_avx2_impl(data, &lut, &mut result);
    }
}

// After
if is_x86_feature_detected!("avx2") {
    // Unsafe: calling target_feature function
    unsafe {
        encode_avx2_impl(data, &lut, &mut result);
    }
}
```

**Implementation function pattern:**
```rust
// Before
unsafe fn encode_avx2_impl(...) {
    unsafe {
        // entire body
    }
}

// After
unsafe fn encode_avx2_impl(...) {
    // Unsafe: SIMD load
    let input_vec = unsafe {
        _mm256_loadu_si256(...)
    };

    // Unsafe: SIMD store
    let mut input_buf = [0u8; 32];
    unsafe {
        _mm256_storeu_si256(...)
    };

    // Safe: LUT lookup and push
    input_buf.iter().for_each(|&byte| {
        result.push(lut[byte as usize]);
    });
}
```

### 4. `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/errors.rs`

**Functions refactored:**
- `test_error_display_no_color()` - Test function
- `test_invalid_length_error()` - Test function
- `test_dictionary_not_found_error()` - Test function

**Pattern applied:**
- Narrowed unsafe blocks around `std::env::set_var()` and `std::env::remove_var()`
- Left safe: string formatting, assertions, function calls

**Example transformation:**
```rust
// Before
unsafe { std::env::set_var("NO_COLOR", "1") };
let err = DecodeError::invalid_character(...);
// ... assertions ...
unsafe { std::env::remove_var("NO_COLOR") };

// After
// Unsafe: environment variable access (not thread-safe)
unsafe {
    std::env::set_var("NO_COLOR", "1");
}

let err = DecodeError::invalid_character(...);
// ... assertions ...

// Unsafe: environment variable access (not thread-safe)
unsafe {
    std::env::remove_var("NO_COLOR");
}
```

## Verification

Ran `cargo check` - all changes compile successfully with no errors.

**Remaining warnings:**
- 11 warnings about unnecessary unsafe blocks in `base64.rs` (not part of this task)

## Benefits

1. **Compiler verification**: Safe operations (bit manipulation, arithmetic, iteration) are now verified by the compiler
2. **Bug prevention**: Bugs in safe code get caught at compile time
3. **Security**: Defense in depth against processor vulnerabilities by letting compiler reason about memory safety
4. **Audit clarity**: Unsafe blocks mark exactly what's dangerous
5. **Edition 2024 ready**: Compliant with new safety requirements

## Next Steps

Consider applying the same pattern to:
- `src/simd/x86_64/specialized/base64.rs` (11 unnecessary unsafe blocks)
- Other SIMD implementation files in the codebase
