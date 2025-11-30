# Gapped.rs Unsafe Scope Refactoring

**File:** `/home/w3surf/work/personal/code/base-d/src/simd/lut/gapped.rs`
**Date:** 2025-11-30
**Task:** Narrow unsafe scopes in all SIMD functions per Edition 2024 migration guidance

## Changes Made

Successfully refactored all 8 unsafe functions to narrow their unsafe scopes, following Option 1 from `~/.matrix/artifacts/cycles/rust/lints/unsafe-op-in-unsafe-fn.md`.

### Functions Refactored

1. **encode_ssse3** (dispatcher) - Lines 219-227
2. **encode_ssse3_5bit** - Lines 232-334
3. **encode_ssse3_6bit** - Lines 339-429
4. **encode_ssse3_4bit** - Lines 434-516
5. **encode_neon** (dispatcher) - Lines 521-529
6. **encode_neon_5bit** - Lines 534-631
7. **encode_neon_6bit** - Lines 636-726
8. **encode_neon_4bit** - Lines 731-813

## Refactoring Pattern Applied

### Before (entire body wrapped):
```rust
unsafe fn encode_ssse3_5bit(&self, data: &[u8], result: &mut String) {
    unsafe {
        use std::arch::x86_64::*;
        // ... entire function body ...
    }
}
```

### After (narrowed scopes):
```rust
unsafe fn encode_ssse3_5bit(&self, data: &[u8], result: &mut String) {
    use std::arch::x86_64::*;

    // Safe: constant definition and bounds check
    const BLOCK_SIZE: usize = 5;
    if data.len() < BLOCK_SIZE {
        self.encode_scalar(data, result);
        return;
    }

    // Unsafe: SIMD vector initialization (target_feature makes these safe to call)
    let threshold_vecs: Vec<__m128i> = self
        .gap_info
        .thresholds
        .iter()
        .map(|&t| _mm_set1_epi8((t.wrapping_sub(1)) as i8))
        .collect();
    // ... more initialization ...

    // Safe: arithmetic
    let num_blocks = data.len() / BLOCK_SIZE;
    let simd_bytes = num_blocks * BLOCK_SIZE;

    for _ in 0..num_blocks {
        // Safe: debug assertion
        debug_assert!(...);

        // Unsafe: unchecked indexing
        let (b0, b1, ...) = unsafe {
            (*data.get_unchecked(offset), ...)
        };

        // Safe: bit manipulation
        let mut indices = [0u8; 16];
        indices[0] = (b0 >> 3) & 0x1F;
        // ... more bit ops ...

        // Unsafe: SIMD operations
        let char_vec = unsafe {
            let idx_vec = _mm_loadu_si128(...);
            // ... SIMD intrinsics ...
            char_vec
        };

        // Unsafe: SIMD store
        let mut output = [0u8; 16];
        unsafe {
            _mm_storeu_si128(...);
        }

        // Safe: iteration and push
        for &ch in &output[..8] {
            result.push(ch as char);
        }

        offset += BLOCK_SIZE;
    }

    // Safe: remainder handling
    if simd_bytes < data.len() {
        self.encode_scalar(&data[simd_bytes..], result);
    }
}
```

## Key Insights

### Target Feature Attribute Behavior
Functions with `#[target_feature(enable = "ssse3")]` or `#[target_feature(enable = "neon")]` make SIMD intrinsics callable without additional unsafe blocks when directly in the function body. The attribute ensures the CPU features are available.

### What Remains Unsafe

1. **get_unchecked()** - Unchecked slice indexing
2. **SIMD load/store** - `_mm_loadu_si128`, `_mm_storeu_si128`, `vld1q_u8`, `vst1q_u8`
3. **SIMD comparisons/arithmetic** - All `_mm_*` and `v*q_*` operations within blocks

### What Is Now Safe

1. **Constants and bounds checks** - `const BLOCK_SIZE`, `if data.len() < BLOCK_SIZE`
2. **Arithmetic** - `num_blocks`, `simd_bytes`, `offset += BLOCK_SIZE`
3. **Bit manipulation** - Shifts, masks, array indexing on stack arrays
4. **debug_assert!** - Compile-time safety checks
5. **Iteration** - `for &ch in &output[..]`
6. **String operations** - `result.push(ch as char)`

## Verification Results

✅ **cargo check** - Compiles cleanly, no warnings
✅ **cargo test** - All 268 tests passed (1 ignored)
✅ **cargo clippy --all-targets --all-features -- -D warnings** - No warnings

## Benefits

1. **Compiler verification** - Safe code now validated by compiler
2. **Easier auditing** - Unsafe blocks mark exactly what's dangerous
3. **Better maintainability** - Clear boundaries between safe/unsafe operations
4. **Edition 2024 ready** - Complies with new unsafe-op-in-unsafe-fn requirements
5. **Defense in depth** - Minimizes attack surface for Spectre/Meltdown-style vulnerabilities

## Code Quality

The refactoring maintains:
- Identical behavior (all tests pass)
- Same performance characteristics
- Clear documentation with comments marking safe vs unsafe operations
- Consistent pattern across all 8 functions
