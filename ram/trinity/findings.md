# ARM64 NEON Base64 Bug - Root Cause IDENTIFIED

## Issue
NEON base64 encode produces invalid indices. Decode rejects the output.

## Root Cause
The NEON reshuffle function incorrectly simulates x86's `_mm_mulhi_epu16`.

**THE FIX ALREADY EXISTS** in commit `0a7c8ac` but was only applied to `src/simd/aarch64/generic.rs`.

The same broken code exists in:
1. `src/simd/lut/large.rs` line ~750 (reshuffle_neon_base64)
2. `src/simd/aarch64/specialized/base64.rs` line ~136 (reshuffle_neon)

## Broken Pattern

```rust
// WRONG - uses scalar multiply with single constant
let mult_hi = vmulq_n_u16(t0_u16, 0x0040);
let t1 = vreinterpretq_u32_u16(vshrq_n_u16(mult_hi, 10));

// WRONG - second extraction also broken
let mult_lo = vmulq_n_u16(t2_u16, 0x0010);
let t3 = vreinterpretq_u32_u16(vshrq_n_u16(mult_lo, 6));
```

## Correct Pattern (from generic.rs)

```rust
// CORRECT - uses vmull + vshrn to simulate mulhi_epu16
let mult_pattern = vreinterpretq_u16_u32(vdupq_n_u32(0x04000040_u32));
let lo = vget_low_u16(t0_u16);
let hi = vget_high_u16(t0_u16);
let mult_lo = vget_low_u16(mult_pattern);
let mult_hi = vget_high_u16(mult_pattern);
let lo_32 = vmull_u16(lo, mult_lo);
let hi_32 = vmull_u16(hi, mult_hi);
let lo_result = vshrn_n_u32(lo_32, 16);
let hi_result = vshrn_n_u32(hi_32, 16);
let t1 = vreinterpretq_u32_u16(vcombine_u16(lo_result, hi_result));

// CORRECT - second extraction uses vmulq_u16 (mullo equivalent)
let mult_pattern = vreinterpretq_u16_u32(vdupq_n_u32(0x01000010_u32));
let t3 = vreinterpretq_u32_u16(vmulq_u16(t2_u16, mult_pattern));
```

## Fix Strategy
Copy the corrected implementation from generic.rs to the other two files.
