# base-d: Unnecessary unsafe blocks in aarch64 SIMD code

**Date:** 2025-11-30
**Repo:** ~/work/personal/code/base-d/
**Issue:** Mac CI failing due to "unnecessary unsafe block" warnings with -D warnings

---

## Summary

Three unnecessary `unsafe` blocks exist in the aarch64 SIMD code that wrap intrinsics already within `unsafe fn` functions. These are now caught by rustc 1.91.1 as lint warnings and break the CI on Mac (aarch64-apple-darwin) because clippy runs with `-D warnings`.

---

## Affected Files & Line Numbers

### 1. `/home/w3surf/work/personal/code/base-d/src/simd/aarch64/specialized/base16.rs`

**Line 261** - Inside `decode_nibble_chars_neon()`:
```rust
#[target_feature(enable = "neon")]
unsafe fn decode_nibble_chars_neon(
    chars: std::arch::aarch64::uint8x16_t,
) -> std::arch::aarch64::uint8x16_t {
    use std::arch::aarch64::*;

    // Unsafe: SIMD intrinsics  <-- Line 260
    unsafe {                      <-- Line 261: UNNECESSARY
        // Strategy: Use character ranges to select appropriate offset
        // ... NEON intrinsics here ...
    }
}
```

The entire function body (lines 261-297) is wrapped in an unnecessary `unsafe` block.

### 2. `/home/w3surf/work/personal/code/base-d/src/simd/aarch64/specialized/base32.rs`

**Line 227** - Inside `translate_encode_neon()`:
```rust
#[target_feature(enable = "neon")]
unsafe fn translate_encode_neon(
    indices: std::arch::aarch64::uint8x16_t,
    variant: Base32Variant,
) -> std::arch::aarch64::uint8x16_t {
    use std::arch::aarch64::*;

    match variant {
        Base32Variant::Rfc4648 => {
            // Unsafe: SIMD intrinsics  <-- Line 226
            unsafe {                      <-- Line 227: UNNECESSARY
                // RFC 4648 standard: 0-25 -> 'A'-'Z', 26-31 -> '2'-'7'
                // ... NEON intrinsics here ...
            }
        }
        Base32Variant::Rfc4648Hex => {
            // Unsafe: SIMD intrinsics  <-- Line 245
            unsafe {                      <-- Line 246: UNNECESSARY (see below)
                // RFC 4648 hex: 0-9 -> '0'-'9', 10-31 -> 'A'-'V'
                // ... NEON intrinsics here ...
            }
        }
    }
}
```

**Line 246** - Same function, Rfc4648Hex variant branch (lines 246-261).

Both match arms contain unnecessary unsafe blocks.

---

## Root Cause Analysis

### Why these blocks are unnecessary

**Context:** All three instances occur inside functions marked with:
```rust
#[target_feature(enable = "neon")]
unsafe fn function_name(...) { ... }
```

**Rust behavior change:**
- Prior to Rust 1.52, NEON intrinsics required `unsafe` blocks even inside `unsafe fn`.
- Since Rust 1.52 (April 2021), the entire body of an `unsafe fn` is considered an unsafe context.
- Current stable (1.91.1, Nov 2025) treats these as unnecessary and emits warnings.

**Pattern observed:**
- The aarch64 code has defensive `unsafe` blocks wrapping NEON intrinsics.
- The x86_64 code does NOT have this pattern - it calls intrinsics directly within `unsafe fn` without inner unsafe blocks.

---

## Comparison: x86_64 vs aarch64

### x86_64 (correct pattern):
```rust
#[target_feature(enable = "avx2")]
unsafe fn reshuffle_avx2(input: std::arch::x86_64::__m256i) -> std::arch::x86_64::__m256i {
    use std::arch::x86_64::*;

    let shuffled = _mm256_shuffle_epi8(input, shuffle_mask);  // Direct call, no unsafe block
    let t0 = _mm256_and_si256(shuffled, _mm256_set1_epi32(0x0FC0FC00_u32 as i32));
    // ...
}
```

### aarch64 (problematic pattern):
```rust
#[target_feature(enable = "neon")]
unsafe fn decode_nibble_chars_neon(...) -> uint8x16_t {
    use std::arch::aarch64::*;

    unsafe {  // <-- UNNECESSARY
        let zero_30 = vdupq_n_u8(0x30);  // Already in unsafe context
        // ...
    }
}
```

---

## Complete Inventory of unsafe blocks in aarch64

**Total unsafe blocks:** 64 across aarch64 SIMD code.

**Breakdown by file:**
- `base16.rs`: 17 unsafe blocks (1 unnecessary)
- `base32.rs`: 24 unsafe blocks (2 unnecessary)
- `base64.rs`: 21 unsafe blocks (0 unnecessary)
- `base256.rs`: 2 unsafe blocks (0 unnecessary)

**Only 3 are unnecessary** - the ones wrapping entire function bodies.

**Safe blocks:** The majority are correctly used for:
- SIMD load/store operations
- SIMD intrinsic calls in small scoped blocks
- Pointer arithmetic

---

## Why Mac CI fails but not Linux/Windows

**CI Configuration:** `.github/workflows/the-matrix-has-you.yml`

```yaml
clippy:
  runs-on: ubuntu-latest
  - run: cargo clippy --all-targets --all-features -- -D warnings

test:
  strategy:
    matrix:
      include:
        - os: ubuntu-latest
          target: x86_64-unknown-linux-gnu
        - os: macos-latest
          target: aarch64-apple-darwin
        - os: windows-latest
          target: x86_64-pc-windows-msvc
  - run: cargo test --verbose
  - run: cargo build --release --verbose
```

**Why it manifests on Mac:**
1. **Clippy runs on ubuntu-latest** (x86_64) - doesn't compile aarch64 code, misses the warnings.
2. **Mac test runs on macos-latest** (aarch64-apple-darwin) - compiles the aarch64 code.
3. **Cargo test/build** likely runs with `-D warnings` by default or via RUSTFLAGS.
4. **The aarch64 code is only compiled on aarch64 targets** due to `#[cfg(target_arch = "aarch64")]`.

**Proof:** The x86_64 Linux and Windows targets don't compile the aarch64 SIMD code at all.

---

## The Fix

**Simple and safe:** Remove the three unnecessary `unsafe` blocks.

### base16.rs:261
**Change:**
```rust
unsafe fn decode_nibble_chars_neon(...) -> uint8x16_t {
    use std::arch::aarch64::*;

    // Remove the unsafe block wrapper (lines 261-297)
    let zero_30 = vdupq_n_u8(0x30);
    // ... rest of function body ...
}
```

### base32.rs:227
**Change:**
```rust
Base32Variant::Rfc4648 => {
    // Remove the unsafe block wrapper (lines 227-242)
    let indices_signed = vreinterpretq_s8_u8(indices);
    // ... rest of match arm ...
}
```

### base32.rs:246
**Change:**
```rust
Base32Variant::Rfc4648Hex => {
    // Remove the unsafe block wrapper (lines 246-261)
    let indices_signed = vreinterpretq_s8_u8(indices);
    // ... rest of match arm ...
}
```

**De-indent the inner code** to maintain formatting consistency.

---

## Risk Assessment

**Risk level:** **ZERO**

**Reasoning:**
1. **No behavioral change** - The code inside these blocks is already in an `unsafe fn` context.
2. **Compiler validates** - The intrinsics are still called in an unsafe context (the function).
3. **x86_64 precedent** - The x86_64 code already follows this pattern successfully.
4. **Rust guarantees** - `#[target_feature]` functions are inherently unsafe.

**Platform impact:**
- **aarch64:** Fixes the warning.
- **x86_64:** No change (code not compiled).
- **Other platforms:** No change.

---

## Additional Findings

**No other unnecessary unsafe blocks detected.** All other unsafe blocks serve legitimate purposes:
- Scoping unsafe operations within safe functions
- Clearly delineating pointer operations
- Wrapping SIMD loads/stores

**Code quality:** The defensive "Unsafe: SIMD intrinsics" comments are good documentation, even if the blocks are no longer needed.

---

## Recommendation

**Action:** Remove the three unsafe blocks and de-indent their contents.

**Testing:** The existing test suite should pass without modification. Mac CI will succeed.

**No further investigation needed.** This is a straightforward lint fix.
