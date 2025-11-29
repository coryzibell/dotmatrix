# ARM64 NEON Base64 Decode Corruption - Root Cause Analysis

## Summary

Fixed critical bug in ARM64 NEON base64 decode implementation causing data corruption. Issue affected two locations in the codebase.

## Root Cause

The NEON implementation incorrectly emulated the x86 `maddubs` instruction when unpacking 6-bit indices back to 8-bit bytes during decode.

### Bug Location 1: `/src/simd/aarch64/generic.rs` line 483

**Broken code:**
```rust
let merge_result = vaddq_u16(even, vshlq_n_u16(odd, 6));
// This computes: even + (odd << 6)
```

**Correct code:**
```rust
let merge_result = vmlaq_n_u16(odd, even, 64);
// This computes: odd + (even * 64) = (even * 64) + odd
```

### Bug Location 2: `/src/simd/lut/large.rs` line 1904

Same bug - incorrect emulation of `maddubs`.

### Additional Bug: `/src/simd/lut/large.rs` line 735-741

**Broken shuffle indices (encode):**
```rust
[
    0, 0, 1, 2,    // WRONG
    3, 3, 4, 5,
    6, 6, 7, 8,
    9, 9, 10, 11,
]
```

**Correct shuffle indices:**
```rust
[
    1, 0, 2, 1,    // Matches x86 pattern
    4, 3, 5, 4,
    7, 6, 8, 7,
    10, 9, 11, 10,
]
```

## Technical Details

### The x86 Algorithm

x86 base64 decode uses two instructions:

1. **`maddubs_epi16(indices, [64, 1, 64, 1, ...])`**
   - Multiplies adjacent bytes: `indices[i] * multiplier[i]`
   - Adds pairs: `result[n] = indices[2n] * 64 + indices[2n+1] * 1`
   - For base64: merges two 6-bit values into one 12-bit value

2. **`madd_epi16(result, [4096, 1, 4096, 1, ...])`**
   - Multiplies 16-bit values and adds adjacent pairs
   - Combines two 12-bit values into one 24-bit value (3 bytes)

### The NEON Bug

The broken NEON code did:
```rust
even + (odd << 6)
```

Where:
- `even` = indices[0, 2, 4, ...] (e.g., 19, 5, ...)
- `odd` = indices[1, 3, 5, ...] (e.g., 22, 46, ...)

Result for indices [19, 22, 5, 46]:
- Pair 0: 19 + (22 << 6) = 19 + 1408 = 1427 ❌
- Expected: (19 << 6) + 22 = 1216 + 22 = 1238 ✓

Actually even worse - it should be:
- `(even * 64) + odd` not `even + (odd << 6)`

The fix uses `vmlaq_n_u16(odd, even, 64)` which computes:
- `odd + (even * 64)` = multiply-add exactly matching x86 semantics

### Test Case Verification

Input: "Man" (0x4D 0x61 0x6E)
Expected base64: "TWFu" (indices 19, 22, 5, 46)

**Before fix:**
- Decode indices [19, 22, 5, 46] → [0x59, 0x3B, 0x85] ❌

**After fix:**
- Decode indices [19, 22, 5, 46] → [0x4D, 0x61, 0x6E] ✓

## Files Modified

1. `/Users/coryzibell/work/personal/code/base-d/src/simd/aarch64/generic.rs`
   - Line 483: Fixed `unshuffle_6bit` decode algorithm

2. `/Users/coryzibell/work/personal/code/base-d/src/simd/lut/large.rs`
   - Line 1904: Fixed `reshuffle_decode_neon` decode algorithm
   - Lines 735-741: Fixed `reshuffle_neon_base64` encode shuffle pattern

## Test Results

All 158 tests passing:
- ✓ Generic SIMD tests (9 tests)
- ✓ LUT large tests (20 tests)
- ✓ All other tests (129 tests)

## Impact

This bug affected:
- All ARM64 NEON base64 encoding/decoding
- Any custom base64-like dictionaries (sequential 64-char alphabets)
- Both the generic SIMD codec and large LUT codec paths

The bug caused complete data corruption on decode, making all roundtrip tests fail.
