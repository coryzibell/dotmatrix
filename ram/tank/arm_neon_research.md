# ARM NEON SIMD Research for base-d

**Research Date:** 2025-11-30
**Target:** `/Users/coryzibell/work/personal/code/base-d`
**Issue:** #109 - ARM NEON specialized implementations for RFC dictionaries

---

## Executive Summary

ARM currently **has NO dedicated `aarch64/` directory** - the directory doesn't exist. ARM SIMD support is entirely provided through the **LUT (lookup table) codecs** in `src/simd/lut/`, which contain inline NEON code for arbitrary dictionaries. There are no ARM-specific specialized implementations for RFC 4648 standard dictionaries (base64, base32, base16, base256).

**Current State:**
- x86_64: Specialized + LUT fallback
- ARM: LUT only (no specialized paths)

**Performance Gap:** ARM is using generic arbitrary-dictionary SIMD paths even for standard RFC dictionaries that could be hardcoded for better performance.

---

## 1. Current ARM Implementation Status

### What Exists

**LUT Codecs with ARM NEON support** (`src/simd/lut/`):

1. **Base64LutCodec** (`lut/base64.rs`)
   - Lines 157-186: `encode_neon_impl()` with NEON feature detection
   - Lines 189-248: `encode_neon_base64()` - Uses `vqtbl4q_u8` for 64-byte direct lookup
   - Lines 250-316: `reshuffle_neon_base64()` - NEON-specific bit extraction
   - **Purpose:** Generic base64 encoding with arbitrary dictionaries

2. **SmallLutCodec** (`lut/base16.rs`)
   - Similar pattern for base16 with arbitrary dictionaries
   - Uses NEON table lookups for character translation

3. **GappedSequentialCodec** (`lut/gapped.rs`)
   - Handles near-sequential dictionaries with gaps (e.g., geohash, Crockford base32)
   - Has aarch64 support inline

### What's Missing

**No `src/simd/aarch64/` directory** - confirmed missing via:
```bash
Glob pattern "**/*.rs" in /Users/coryzibell/work/personal/code/base-d/src/simd/aarch64/
# Error: Directory does not exist
```

**No specialized ARM implementations for:**
- RFC 4648 base64 (standard/URL variants)
- RFC 4648 base32 (standard/hex variants)
- RFC 4648 base16 (standard hex)
- base256 (Matrix dictionary)

---

## 2. x86_64 Specialized Pattern

### Structure

```
src/simd/x86_64/
├── mod.rs                    # Public API, dispatch logic
├── common.rs                 # Shared utilities (block calculation, scalar fallbacks)
└── specialized/
    ├── mod.rs                # Module exports
    ├── base64.rs             # RFC 4648 base64 (standard/URL)
    ├── base32.rs             # RFC 4648 base32 (standard/hex)
    ├── base16.rs             # RFC 4648 hex
    └── base256.rs            # Matrix dictionary (byte range)
```

### Specialized Implementations

**base64.rs** (lines 1-942):
- **Hardcoded dictionaries:** Standard (`A-Za-z0-9+/`) and URL-safe (`A-Za-z0-9-_`)
- **AVX2 path:** 24 bytes → 32 chars per iteration
- **SSSE3 path:** 12 bytes → 16 chars per iteration
- **Key technique:** Offset-based translation using lookup tables
  - Standard: `lut = [65, 71, -4×10, -19, -16]`
  - URL-safe: `lut = [65, 71, -4×10, -17, 32]`
- **Reshuffle algorithm:** `_mm_shuffle_epi8` + multiply-shift for 6-bit extraction
- **Scalar fallback:** Handled via `encode_scalar_remainder()`

**base32.rs** (lines 1-150):
- **5-bit encoding:** 5 bytes → 8 chars
- **AVX2:** 20 bytes → 32 chars
- **SSSE3:** 10 bytes → 16 chars
- **Padding:** RFC 4648 base32 pads to 8-character boundaries
- **Validation:** `validate_base32_padding()` checks RFC compliance

**base16.rs:**
- **4-bit encoding:** 1 byte → 2 hex chars
- **Variants:** Uppercase (`0-9A-F`) and lowercase (`0-9a-f`)
- **Simple masking:** Nibble extraction + offset

**base256.rs:**
- **8-bit encoding:** 1:1 mapping (Matrix dictionary)
- **Minimal overhead:** Direct character translation

### Dispatch Logic (x86_64/mod.rs)

Lines 80-254 show the public API pattern:
```rust
pub fn encode_base64_simd(data: &[u8], dictionary: &Dictionary) -> Option<String> {
    if dictionary.base() != 64 { return None; }
    let variant = identify_base64_variant(dictionary)?;
    if !is_x86_feature_detected!("ssse3") { return None; }
    specialized::base64::encode(data, dictionary, variant)
}
```

**Key points:**
1. Base validation
2. Variant identification (matches known RFC dictionaries)
3. CPU feature detection (`ssse3`, `avx2`)
4. Dispatch to specialized implementation

---

## 3. GitHub Issue #109 Requirements

**Issue Title:** ARM NEON specialized implementations for RFC dictionaries

**Priority:** Medium (ARM performance acceptable via LUT, but optimization potential untapped)

**Proposed Work:**

1. **Create `aarch64/specialized/` structure** mirroring x86_64
2. **Implement NEON-optimized versions:**
   - base64 (RFC 4648 standard/URL)
   - base32 (RFC 4648 standard/hex)
   - base16 (standard hex)
   - base256 (Matrix dictionary)
3. **Update dispatch logic** in `simd/mod.rs` to route ARM to specialized paths

**Current Behavior:**
| Location | x86_64 | ARM |
|----------|--------|-----|
| `x86_64/specialized/base64.rs` | Hardcoded RFC 4648 | N/A |
| `x86_64/specialized/base32.rs` | Hardcoded RFC 4648 | N/A |
| `x86_64/specialized/base16.rs` | Hardcoded hex | N/A |
| `x86_64/specialized/base256.rs` | Matrix dictionary | N/A |
| `lut/*.rs` | Generic LUT (fallback) | Generic LUT (primary) |

---

## 4. LUT Codec Pattern (Fallback)

**Base64LutCodec** (`src/simd/lut/base64.rs`):

### Purpose
Generic SIMD codec for arbitrary base64-scale dictionaries (17-64 chars). Handles non-standard dictionaries that don't match RFC 4648.

### Platform Strategies
- **ARM NEON:** `vqtbl4q_u8` (64-byte direct lookup) - lines 179-248
- **x86 AVX-512 VBMI:** `vpermb` (64-byte direct lookup)
- **x86 fallback:** Range-reduction with SSSE3 (lines 374-499)

### ARM NEON Implementation Details

**Encoding Flow:**
1. **Feature detection** (line 158): `#[target_feature(enable = "neon")]`
2. **LUT loading** (lines 208-215): Load 64-byte encode table as `uint8x16x4_t`
3. **Reshuffle** (lines 250-316): Extract 6-bit indices using NEON equivalents of x86 multiply-shift
4. **Translate** (line 230): `vqtbl4q_u8(lut_tables, reshuffled)` - direct 64-byte lookup
5. **Store** (lines 233-239): `vst1q_u8` + append to result string

**Reshuffle Algorithm (NEON):**
```rust
// Lines 277-315: NEON equivalent of x86 reshuffle
// - vqtbl1q_u8: Byte shuffle (like pshufb)
// - vmull_u16 + vshrn_n_u32: Implement mulhi_epu16 (no direct NEON equivalent)
// - vmulq_u16: Implement mullo_epi16
// - vandq_u32, vorrq_u32: Bitwise operations
```

**Key difference from x86:**
- NEON has **`vqtbl4q_u8`** for 64-byte direct lookup (4×16-byte tables)
- x86 requires AVX-512 VBMI's `vpermb` for equivalent; otherwise uses range-reduction

### Constraints
- 17 ≤ Base ≤ 64
- Power-of-2 base (32 or 64)
- ASCII-only (`char < 0x80`)
- Non-sequential dictionaries only (sequential → GenericSimdCodec)

---

## 5. Recommended Approach for ARM Specialized Paths

### Directory Structure

```
src/simd/aarch64/
├── mod.rs                    # Public API, NEON feature detection, dispatch
├── common.rs                 # ARM-specific utilities
└── specialized/
    ├── mod.rs                # Module exports
    ├── base64.rs             # RFC 4648 base64 (standard/URL)
    ├── base32.rs             # RFC 4648 base32 (standard/hex)
    ├── base16.rs             # RFC 4648 hex
    └── base256.rs            # Matrix dictionary
```

### Implementation Strategy

**1. Leverage existing LUT NEON code:**
- Copy reshuffle logic from `lut/base64.rs` (lines 250-316)
- Adapt for hardcoded RFC dictionaries

**2. NEON intrinsics to use:**
- **`vqtbl1q_u8`**: Byte shuffle (equivalent to x86 `_mm_shuffle_epi8`)
- **`vqtbl4q_u8`**: 64-byte table lookup (better than x86 SSSE3 for translation)
- **`vmull_u16` + `vshrn_n_u32`**: Implement `mulhi_epu16` pattern
- **`vmulq_u16`**: Direct equivalent to `mullo_epi16`
- **`vandq_u32`, `vorrq_u32`**: Bitwise operations
- **`vld1q_u8`, `vst1q_u8`**: Load/store operations

**3. Block sizes:**
- **base64:** 12 bytes → 16 chars (matches x86 SSSE3)
- **base32:** 10 bytes → 16 chars (matches x86 SSSE3)
- **base16:** 16 bytes → 32 chars
- **base256:** 16 bytes → 16 chars

**4. Translation approach:**

**Option A: Hardcoded LUTs** (recommended for base64/32)
```rust
// base64 standard: vqtbl4q_u8 with 64-byte LUT
// Faster than range-reduction for standard dictionaries
let lut = [b'A', b'B', ..., b'/', 0, 0, ...]; // 64 bytes
let chars = vqtbl4q_u8(lut_tables, indices);
```

**Option B: Offset-based** (like x86)
```rust
// Translate using offset table + add (fewer lookups)
// Similar to x86 specialized approach (lines 549-587 in x86/specialized/base64.rs)
```

**5. Rust 2024 Edition unsafe blocks:**
```rust
// WRONG (wraps entire function):
#[target_feature(enable = "neon")]
unsafe fn encode_neon(...) {
    // All code here
}

// CORRECT (explicit unsafe blocks):
#[target_feature(enable = "neon")]
fn encode_neon(...) {
    let lut_tables = unsafe {
        uint8x16x4_t(
            vld1q_u8(lut.as_ptr()),
            vld1q_u8(lut.as_ptr().add(16)),
            vld1q_u8(lut.as_ptr().add(32)),
            vld1q_u8(lut.as_ptr().add(48)),
        )
    };

    let input_vec = unsafe { vld1q_u8(data.as_ptr().add(offset)) };
    let reshuffled = unsafe { reshuffle_neon(input_vec) };
    // Safe operations here
    unsafe { vst1q_u8(output.as_mut_ptr(), chars) };
}
```

### Dispatch Integration

**Update `src/simd/mod.rs`** to add ARM paths:

```rust
#[cfg(target_arch = "aarch64")]
mod aarch64;

#[cfg(target_arch = "aarch64")]
pub use aarch64::{
    encode_base64_simd, encode_base32_simd,
    encode_base16_simd, encode_base256_simd,
    decode_base64_simd, decode_base32_simd,
    decode_base16_simd, decode_base256_simd,
};

#[cfg(target_arch = "aarch64")]
pub fn encode_with_simd(data: &[u8], dict: &Dictionary) -> Option<String> {
    let base = dict.base();

    // 1. Try specialized base64 for known variants
    if base == 64 && let Some(_variant) = variants::identify_base64_variant(dict) {
        return aarch64::encode_base64_simd(data, dict);
    }

    // 2. Try specialized base32 for known variants
    if base == 32 && let Some(_variant) = variants::identify_base32_variant(dict) {
        return aarch64::encode_base32_simd(data, dict);
    }

    // ... rest of fallback chain to LUT codecs
}
```

---

## 6. Performance Considerations

### Why Specialized > LUT for RFC Dictionaries

**LUT approach (current ARM):**
- Builds 64-byte or 256-byte translation tables at runtime
- Flexible for arbitrary dictionaries
- Extra memory indirection for lookups
- Runtime dictionary analysis overhead

**Specialized approach (proposed):**
- Hardcoded constants at compile time
- Optimized instruction sequences for known patterns
- Compiler can optimize more aggressively
- Smaller code size (no runtime analysis)
- Better branch prediction

### Expected Performance Gains

Based on x86 specialized vs LUT patterns:
- **Throughput:** 10-20% improvement for RFC dictionaries
- **Latency:** Reduced by eliminating runtime dictionary checks
- **Code size:** Smaller specialized paths vs generic LUT
- **Energy:** Fewer memory accesses, better cache behavior

---

## 7. Testing Strategy

**Mirror x86_64 test structure:**

1. **Round-trip tests:** Encode → Decode verification
2. **Known values:** Test against RFC 4648 test vectors
3. **Edge cases:** Empty input, partial blocks, padding
4. **Length variants:** 0..100 to cover all block sizes
5. **SIMD vs scalar:** Verify specialized matches scalar output

**Test files:**
- `src/simd/aarch64/specialized/base64.rs` (tests at bottom)
- Integration tests in `src/simd/mod.rs`

---

## 8. Implementation Checklist

### Phase 1: Infrastructure
- [ ] Create `src/simd/aarch64/` directory
- [ ] Create `src/simd/aarch64/mod.rs` with NEON feature detection
- [ ] Create `src/simd/aarch64/common.rs` (shared utilities)
- [ ] Create `src/simd/aarch64/specialized/` subdirectory
- [ ] Update `src/simd/mod.rs` to import aarch64 module

### Phase 2: base64 (Highest Priority)
- [ ] `aarch64/specialized/base64.rs`: Encode (standard/URL)
- [ ] `aarch64/specialized/base64.rs`: Decode (standard/URL)
- [ ] Tests: Round-trip, known values, edge cases
- [ ] Benchmark vs LUT codec

### Phase 3: base32
- [ ] `aarch64/specialized/base32.rs`: Encode (standard/hex)
- [ ] `aarch64/specialized/base32.rs`: Decode (standard/hex)
- [ ] Tests: Round-trip, padding validation
- [ ] Benchmark vs LUT codec

### Phase 4: base16
- [ ] `aarch64/specialized/base16.rs`: Encode (upper/lower)
- [ ] `aarch64/specialized/base16.rs`: Decode (case-insensitive)
- [ ] Tests: Round-trip, both case variants
- [ ] Benchmark vs LUT codec

### Phase 5: base256
- [ ] `aarch64/specialized/base256.rs`: Encode (Matrix dictionary)
- [ ] `aarch64/specialized/base256.rs`: Decode (Matrix dictionary)
- [ ] Tests: Round-trip, byte range mode
- [ ] Benchmark vs LUT codec

### Phase 6: Integration
- [ ] Update `encode_with_simd()` dispatch in `simd/mod.rs`
- [ ] Update `decode_with_simd()` dispatch in `simd/mod.rs`
- [ ] CI: Add ARM-specific test runs
- [ ] Documentation: Update architecture docs

---

## 9. Key Files Reference

### x86_64 Reference Files (for porting)
- `/Users/coryzibell/work/personal/code/base-d/src/simd/x86_64/mod.rs` (dispatch pattern)
- `/Users/coryzibell/work/personal/code/base-d/src/simd/x86_64/specialized/base64.rs` (reference implementation)
- `/Users/coryzibell/work/personal/code/base-d/src/simd/x86_64/specialized/base32.rs` (5-bit pattern)
- `/Users/coryzibell/work/personal/code/base-d/src/simd/x86_64/common.rs` (utilities)

### ARM NEON Reference (existing code)
- `/Users/coryzibell/work/personal/code/base-d/src/simd/lut/base64.rs` (lines 157-340: NEON LUT implementation)
- `/Users/coryzibell/work/personal/code/base-d/src/simd/lut/base32.rs` (NEON base32 patterns)
- `/Users/coryzibell/work/personal/code/base-d/src/simd/lut/base16.rs` (NEON base16 patterns)

### Dispatch Integration
- `/Users/coryzibell/work/personal/code/base-d/src/simd/mod.rs` (lines 65-241: unified entry points)
- `/Users/coryzibell/work/personal/code/base-d/src/simd/variants.rs` (variant identification)

### Issue Tracking
- GitHub Issue #109: https://github.com/coryzibell/base-d/issues/109

---

## 10. NEON Intrinsic Mapping

**x86 SSSE3 → ARM NEON equivalents:**

| x86 Intrinsic | ARM NEON Equivalent | Notes |
|---------------|---------------------|-------|
| `_mm_shuffle_epi8` | `vqtbl1q_u8` | Byte shuffle within 128-bit |
| `_mm_set_epi8` | `vld1q_u8` + array | Load from constant array |
| `_mm_and_si128` | `vandq_u32` | Bitwise AND |
| `_mm_or_si128` | `vorrq_u32` | Bitwise OR |
| `_mm_mulhi_epu16` | `vmull_u16` + `vshrn_n_u32` | Multiply high (no direct equivalent) |
| `_mm_mullo_epi16` | `vmulq_u16` | Multiply low |
| `_mm_loadu_si128` | `vld1q_u8` | Unaligned load |
| `_mm_storeu_si128` | `vst1q_u8` | Unaligned store |
| `_mm_subs_epu8` | `vqsubq_u8` | Saturating subtract |
| `_mm_add_epi8` | `vaddq_u8` | Add |

**ARM-specific advantages:**
- `vqtbl4q_u8`: 64-byte lookup (no x86 SSSE3 equivalent, requires AVX-512 VBMI)
- Better table lookup performance than x86 range-reduction

---

## Conclusion

ARM NEON support exists but is **under-optimized**. The LUT codecs work well for arbitrary dictionaries but leave performance on the table for standard RFC dictionaries. Creating `aarch64/specialized/` mirroring the x86_64 structure will bring ARM performance parity with x86_64 for common use cases.

**Next Steps:**
1. Create directory structure
2. Port base64 specialized implementation first (highest impact)
3. Validate with tests and benchmarks
4. Iterate through base32, base16, base256

**Estimated Effort:** Medium (most NEON code already exists in LUT codecs, needs extraction and hardcoding for RFC dictionaries)

---

**Research compiled by:** Tank
**For:** Neo (The One)
**Ready for handoff to:** Architect (design) or Smith (implementation)
