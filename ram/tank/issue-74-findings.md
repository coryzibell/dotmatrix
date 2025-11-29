# Issue #74: SIMD Bounds Checking Missing in LUT Codec

## Issue Details

**Title:** [BLOCKER] SIMD bounds checking missing in LUT codec  
**Source:** Construct security audit (Cypher identification)  
**File:** `/home/w3surf/work/personal/code/base-d/src/simd/lut/large.rs`  
**Severity:** BLOCKER - Memory safety violation

## Problem Statement

The issue states that lines 245-270 in `simd/lut/large.rs` perform unsafe SIMD operations without validating input length alignment. However, upon examination, **lines 245-270 contain threshold building logic, not SIMD processing loops**.

The actual vulnerability exists in multiple SIMD encode/decode functions throughout the file that use `get_unchecked()` and pointer arithmetic without sufficient length validation.

## Affected Code Locations

### 1. **encode_ssse3_range_reduction_5bit** (lines 881-961)
**Vulnerable Pattern:**
```rust
unsafe fn encode_ssse3_range_reduction_5bit(&self, data: &[u8], result: &mut String) {
    const BLOCK_SIZE: usize = 5; // 5 bytes → 8 chars (40 bits)

    if data.len() < BLOCK_SIZE {
        self.encode_scalar_base32_x86(data, result);
        return;
    }

    let num_blocks = data.len() / BLOCK_SIZE;
    let simd_bytes = num_blocks * BLOCK_SIZE;

    let mut offset = 0;
    for _ in 0..num_blocks {
        let bytes = [
            *data.get_unchecked(offset),      // ⚠️ UNSAFE
            *data.get_unchecked(offset + 1),  // ⚠️ UNSAFE
            *data.get_unchecked(offset + 2),  // ⚠️ UNSAFE
            *data.get_unchecked(offset + 3),  // ⚠️ UNSAFE
            *data.get_unchecked(offset + 4),  // ⚠️ UNSAFE
        ];
        // ... processing ...
        offset += BLOCK_SIZE;
    }
}
```

**Issue:** While there's a check `if data.len() < BLOCK_SIZE`, the loop uses `get_unchecked()` which bypasses bounds checking. The calculation `num_blocks * BLOCK_SIZE` is safe, but using unchecked access is still risky.

### 2. **encode_ssse3_range_reduction_6bit** (lines 996-1086)
**Vulnerable Pattern:**
```rust
let num_blocks = data.len() / BLOCK_SIZE;
let mut offset = 0;
for _ in 0..num_blocks {
    let input_vec = _mm_loadu_si128(data.as_ptr().add(offset) as *const __m128i);
    // ... processing ...
    offset += BLOCK_SIZE;
}
```

**Issue:** Uses raw pointer arithmetic (`.add(offset)`) without explicit bounds validation. If BLOCK_SIZE is 16 bytes and input isn't aligned, could read past buffer.

### 3. **encode_neon_base32** (lines 600-670)
**Vulnerable Pattern:**
```rust
for _ in 0..num_blocks {
    let bytes = [
        *data.get_unchecked(offset),
        *data.get_unchecked(offset + 1),
        *data.get_unchecked(offset + 2),
        *data.get_unchecked(offset + 3),
        *data.get_unchecked(offset + 4),
    ];
    // ... processing ...
}
```

**Issue:** Same pattern - unchecked array access in loop.

### 4. **encode_neon_base64** (lines 671-787)
**Vulnerable Pattern:**
```rust
let input_vec = vld1q_u8(data.as_ptr().add(offset));
```

**Issue:** NEON intrinsic loading without bounds check.

### 5. **Decode Functions** (lines 1402-1495)
**Multiple vulnerable patterns:**
```rust
// decode_ssse3_multi_range_5bit (line 1424)
let chars = _mm_loadu_si128(encoded.as_ptr().add(offset) as *const __m128i);

// decode_ssse3_multi_range_6bit (line 1471)
let chars = _mm_loadu_si128(input_no_padding.as_ptr().add(offset) as *const __m128i);

// decode_ssse3_base32_rfc4648 (line 1588)
let input = _mm_loadu_si128(encoded.as_ptr().add(offset) as *const __m128i);

// decode_neon_base32_rfc4648 (line 1656)
let input_vec = vld1q_u8(encoded.as_ptr().add(offset));
```

**Issue:** All use pointer arithmetic in loops without explicit validation that `offset + SIMD_WIDTH <= buffer.len()`.

## Vulnerability Details

### Memory Safety Violations
1. **Out-of-bounds reads:** If input length is not a multiple of SIMD register width (16 bytes for SSE, variable for NEON), the last iteration could read past buffer bounds
2. **get_unchecked() abuse:** Multiple uses of `get_unchecked()` without proving safety invariants
3. **Raw pointer arithmetic:** `.add(offset)` operations assume offset is valid but don't verify

### Impact
- **Information disclosure:** Reading past buffer bounds could leak memory contents
- **Crash on malformed input:** Segfault if reading unmapped memory
- **Undefined behavior:** Violates Rust safety guarantees

### Exploitation Scenario
```rust
let malformed_input = vec![0u8; 17]; // Not multiple of 16
codec.decode(&malformed_input, &dict); // Last block reads 16 bytes starting at offset 16 → OOB
```

## Required Fixes

### 1. Explicit Bounds Validation
Add checks before SIMD processing:
```rust
const SIMD_WIDTH: usize = 16;

if input.len() < SIMD_WIDTH {
    return scalar_fallback(input);
}

let aligned_len = input.len() - (input.len() % SIMD_WIDTH);
let num_blocks = aligned_len / SIMD_WIDTH;

// Process only aligned portion
for i in 0..num_blocks {
    let offset = i * SIMD_WIDTH;
    // SAFE: offset + SIMD_WIDTH <= aligned_len <= input.len()
    let vec = _mm_loadu_si128(input.as_ptr().add(offset) as *const __m128i);
    // ...
}

// Scalar fallback for remainder
if aligned_len < input.len() {
    scalar_fallback(&input[aligned_len..]);
}
```

### 2. Replace get_unchecked() with Safe Indexing
Where performance-critical and provably safe, add explicit assertions:
```rust
assert!(offset + BLOCK_SIZE <= data.len());
let bytes = [
    data[offset],
    data[offset + 1],
    // ...
];
```

Or refactor to use safe slice indexing:
```rust
let block = &data[offset..offset + BLOCK_SIZE];
let bytes = [block[0], block[1], block[2], block[3], block[4]];
```

### 3. Validate Pointer Arithmetic
Before any `.add(offset)` operation:
```rust
debug_assert!(offset + SIMD_WIDTH <= buffer.len());
```

## Acceptance Criteria (from Issue)

- [ ] Bounds check added before SIMD loop
- [ ] Scalar fallback for undersized inputs
- [ ] Fuzz testing confirms no OOB reads
- [ ] No performance regression for aligned inputs

## Recommended Testing

```rust
#[test]
fn test_unaligned_input_no_oob() {
    for len in 1..100 {
        let input = vec![0u8; len];
        let result = codec.encode(&input, &dict);
        // Should not crash or trigger ASAN
    }
}

// Fuzz testing with cargo-fuzz
fuzz_target!(|data: &[u8]| {
    let _ = codec.encode(data, &dict);
    let _ = codec.decode(data, &dict);
});
```

## Files Requiring Modification

**Primary file:**
- `/home/w3surf/work/personal/code/base-d/src/simd/lut/large.rs`

**Functions requiring fixes:**
1. `encode_ssse3_range_reduction_5bit` (line 881)
2. `encode_ssse3_range_reduction_6bit` (line 996)
3. `encode_neon_base32` (line 600)
4. `encode_neon_base64` (line 671)
5. `encode_avx512_vbmi_base32` (line 1087)
6. `encode_avx512_vbmi_base64` (line 1152)
7. `decode_ssse3_multi_range_5bit` (line 1413)
8. `decode_ssse3_multi_range_6bit` (line 1452)
9. `decode_ssse3_base32_rfc4648` (line 1578)
10. `decode_neon_base32_rfc4648` (line 1646)
11. `decode_ssse3_base64_standard` (line 1711)
12. `decode_neon_base64_standard` (line 1799)

**Total:** 12 functions across ~3330 lines of code

## Handoff Plan (per Issue)

1. **Cypher** → Identifies (COMPLETE - this research)
2. **Smith** → Implements fixes
3. **Deus** → Verifies with fuzzing
4. **Neo** → Merges

---

**Research completed by:** Tank  
**Date:** 2025-11-29  
**Storage location:** `~/.matrix/ram/tank/issue-74-findings.md`
