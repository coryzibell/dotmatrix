# base-d SIMD Architecture Audit

## Executive Summary

This audit examines SIMD implementation parity between x86_64 (AVX2/SSSE3) and aarch64 (NEON) for the base-d encoding library. The analysis reveals **near-complete feature parity** for specialized codecs, with a **critical gap** in the GenericSimdCodec which has no aarch64 implementation.

---

## 1. Feature Parity Matrix

### Specialized Codecs

| Codec | Operation | x86_64 (SSSE3) | x86_64 (AVX2) | aarch64 (NEON) | Status |
|-------|-----------|----------------|---------------|----------------|--------|
| **Base64Codec** | Encode | YES | YES | YES | PARITY |
| **Base64Codec** | Decode | YES | YES | YES | PARITY |
| **Base32Codec** | Encode | YES | YES | YES | PARITY |
| **Base32Codec** | Decode | YES | YES | YES | PARITY |
| **Base16Codec** | Encode | YES | YES | YES | PARITY |
| **Base16Codec** | Decode | YES | YES | YES | PARITY |
| **Base256Codec** | Encode | YES | YES | YES | PARITY |
| **Base256Codec** | Decode | YES | YES | YES | PARITY |

### LUT-Based Codecs

| Codec | Operation | x86_64 (SSSE3) | x86_64 (AVX2) | aarch64 (NEON) | Status |
|-------|-----------|----------------|---------------|----------------|--------|
| **SmallLutCodec** | Encode | YES | YES | YES | PARITY |
| **SmallLutCodec** | Decode | YES | YES | YES | PARITY |
| **Base64LutCodec** | Encode | YES (scalar) | YES (scalar) | YES (vqtbl4) | PARITY |
| **Base64LutCodec** | Decode | YES | YES | YES | PARITY |
| **GappedSequentialCodec** | Encode | YES | - | YES | PARITY |
| **GappedSequentialCodec** | Decode | SCALAR | - | SCALAR | PARITY (both scalar) |
| **GenericSimdCodec** | Encode 4/5/6/8-bit | YES | YES | **NO (returns None)** | **GAP** |
| **GenericSimdCodec** | Decode 4/5/6/8-bit | YES | YES | **NO (returns None)** | **GAP** |

### Legend
- **PARITY**: Full implementation on both architectures
- **GAP**: Missing implementation on one architecture
- **SCALAR**: Falls back to scalar implementation

---

## 2. Dispatch Path Analysis

### x86_64 `encode_with_simd` Path (lines 103-166 of mod.rs)

```
1. Require SIMD: has_avx2() || has_ssse3() -> else return None
2. Base 64 + identify_base64_variant() -> encode_base64_simd()
3. Base 32 + identify_base32_variant() -> encode_base32_simd()
4. Base 16 + is_standard_hex() -> encode_base16_simd()
5. Base 256 + ByteRange mode -> encode_base256_simd()
6. GenericSimdCodec::from_dictionary() -> codec.encode()
7. GappedSequentialCodec::from_dictionary() -> codec.encode()
8. Base <= 16 + SmallLutCodec::from_dictionary() -> codec.encode()
9. Base 17-64 + Base64LutCodec::from_dictionary() -> codec.encode()
10. Return None (fall back to scalar)
```

### aarch64 `encode_with_simd` Path (lines 287-329 of mod.rs)

```
1. (No SIMD check - NEON always available)
2. Base 64 + identify_base64_variant() -> encode_base64_simd()
3. Base 32 + identify_base32_variant() -> encode_base32_simd()
4. Base 16 + is_standard_hex_aarch64() -> encode_base16_simd()
5. Base 256 -> encode_base256_simd()
6. Base <= 16 + SmallLutCodec::from_dictionary() -> codec.encode()
7. Base 32/64 + Base64LutCodec::from_dictionary() -> codec.encode()
8. Return None (fall back to scalar)
```

### Key Dispatch Differences

| Aspect | x86_64 | aarch64 |
|--------|--------|---------|
| SIMD availability check | Runtime (has_avx2/has_ssse3) | None (assumed) |
| GenericSimdCodec attempt | YES (step 6) | **NO (missing)** |
| GappedSequentialCodec attempt | YES (step 7) | **NO (missing)** |
| Base256 condition | Requires ByteRange mode | Any base 256 |
| Dispatch order | 9 attempts | 7 attempts |

**Impact**: Sequential dictionaries that would match GenericSimdCodec on x86_64 will fall through to scalar on aarch64.

---

## 3. Dictionary Detection Consistency

### Variant Detection Functions

| Function | Location | Behavior |
|----------|----------|----------|
| `identify_base64_variant()` | variants.rs | Pure logic, architecture-agnostic |
| `identify_base32_variant()` | variants.rs | Pure logic, architecture-agnostic |
| `is_standard_hex()` | mod.rs (x86_64 only) | Checks 0-9A-F or 0-9a-f |
| `is_standard_hex_aarch64()` | mod.rs (aarch64 only) | Same logic, different implementation |

### DictionaryMetadata Analysis

The `DictionaryMetadata::from_dictionary()` function in variants.rs:
- Detects `TranslationStrategy`: Sequential, Ranged, or Arbitrary
- Determines `LutStrategy`: SmallDirect, LargePlatformDependent, etc.
- **Architecture-agnostic** - same logic on both platforms

### Codec Selection Determinism

A given dictionary will select **different codecs** on different architectures in these cases:

| Dictionary Type | x86_64 Codec | aarch64 Codec |
|-----------------|--------------|---------------|
| Sequential power-of-2 (non-standard) | GenericSimdCodec | **None (scalar)** |
| Near-sequential with gaps | GappedSequentialCodec | **None (scalar)** |

---

## 4. Implementation Gaps

### CRITICAL: GenericSimdCodec aarch64 Stubs

**Location**: `/Users/coryzibell/work/personal/code/base-d/src/simd/generic/mod.rs` lines 784-822

All aarch64 implementations return `None`:

```rust
#[cfg(not(target_arch = "x86_64"))]
fn encode_6bit(&self, _data: &[u8], _dict: &Dictionary) -> Option<String> {
    None
}

#[cfg(not(target_arch = "x86_64"))]
fn encode_4bit(&self, _data: &[u8], _dict: &Dictionary) -> Option<String> {
    None
}

// ... same pattern for encode_5bit, encode_8bit
// ... same pattern for decode_4bit, decode_5bit, decode_6bit, decode_8bit
```

**Affected Operations**:
- `encode_4bit` (base16 sequential)
- `encode_5bit` (base32 sequential)
- `encode_6bit` (base64 sequential)
- `encode_8bit` (base256 sequential)
- `decode_4bit`, `decode_5bit`, `decode_6bit`, `decode_8bit`

### MODERATE: GappedSequentialCodec Decode is Scalar-Only

**Location**: `/Users/coryzibell/work/personal/code/base-d/src/simd/lut/gapped.rs`

Encode has both x86_64 (SSSE3) and aarch64 (NEON) implementations:
- `encode_ssse3_4bit`, `encode_ssse3_5bit`, `encode_ssse3_6bit`
- `encode_neon_4bit`, `encode_neon_5bit`, `encode_neon_6bit`

Decode uses scalar `decode_lut()` loop for **both** architectures:
```rust
pub fn decode(&self, encoded: &str, dict: &Dictionary) -> Option<Vec<u8>> {
    // ... validation ...
    self.decode_lut(input_bytes, dict)  // Scalar loop
}
```

### MINOR: aarch64 Dispatch Missing Codecs

**Location**: `/Users/coryzibell/work/personal/code/base-d/src/simd/mod.rs` lines 287-329

The aarch64 dispatch path omits:
1. `GenericSimdCodec::from_dictionary()` attempt
2. `GappedSequentialCodec::from_dictionary()` attempt

Even though GappedSequentialCodec has NEON encode support, it's never tried on aarch64.

### Known Issues

**Location**: mod.rs lines 592-594

```rust
// NOTE: Standard base16 decode has a known issue and is temporarily disabled
// Custom base16 (via GenericSimdCodec) works correctly
// TODO: Fix specialized base16 decode implementation
```

The `test_decode_with_simd_base16_round_trip` test is marked `#[ignore]`.

---

## 5. Codec-Level Analysis

### Base64Codec

| Aspect | x86_64 | aarch64 |
|--------|--------|---------|
| Encode block size | SSSE3: 12B->16C, AVX2: 24B->32C | NEON: 12B->16C |
| Decode block size | SSSE3: 16C->12B, AVX2: 32C->24B | NEON: 16C->12B |
| Variants supported | Standard, URL-safe | Standard, URL-safe |
| Algorithm | Multiply-shift bit extraction | Multiply-shift (vmull/vshrn) |

### Base32Codec

| Aspect | x86_64 | aarch64 |
|--------|--------|---------|
| Encode block size | SSSE3: 10B->16C, AVX2: 20B->32C | NEON: 10B->16C |
| Decode block size | SSSE3: 16C->10B, AVX2: 32C->20B | NEON: 16C->10B |
| Variants supported | RFC4648, RFC4648Hex | RFC4648, RFC4648Hex |
| 5-bit extraction | Scalar unpack (no clean SIMD pattern) | Scalar unpack |

### Base16Codec

| Aspect | x86_64 | aarch64 |
|--------|--------|---------|
| Encode block size | SSSE3: 16B->32C, AVX2: 32B->64C | NEON: 16B->32C |
| Decode block size | SSSE3: 32C->16B, AVX2: 64C->32B | NEON: 32C->16B |
| Nibble extraction | pshufb LUT | vqtbl1q_u8 LUT |
| Interleave | unpacklo/unpackhi | vzip1q/vzip2q |

### Base256Codec

| Aspect | x86_64 | aarch64 |
|--------|--------|---------|
| Encode approach | SIMD load, scalar LUT | SIMD load, scalar LUT |
| Decode approach | Scalar HashMap lookup | Scalar HashMap lookup |
| SIMD benefit | Better cache utilization | Better cache utilization |

Note: 256-entry LUT doesn't fit in SIMD registers, limiting SIMD benefit.

### SmallLutCodec (Arbitrary Base <= 16)

| Aspect | x86_64 | aarch64 |
|--------|--------|---------|
| Encode LUT | pshufb (16-entry) | vqtbl1q_u8 (16-entry) |
| Decode approach | Exhaustive search + validate | Exhaustive search + validate |
| AVX2 optimization | YES | N/A |

### Base64LutCodec (Arbitrary Base 32/64)

| Aspect | x86_64 | aarch64 |
|--------|--------|---------|
| Encode LUT | Scalar (range-reduction fallback) | vqtbl4q_u8 (64-entry) |
| Decode approach | Scalar with decode_lut | Scalar with decode_lut |

aarch64 has advantage here due to native 64-byte table lookup instruction.

### GappedSequentialCodec

| Aspect | x86_64 | aarch64 |
|--------|--------|---------|
| Encode | SSSE3 SIMD (4/5/6-bit) | NEON SIMD (4/5/6-bit) |
| Decode | Scalar | Scalar |
| Dispatch | Attempted at step 7 | **Never attempted** |

### GenericSimdCodec

| Aspect | x86_64 | aarch64 |
|--------|--------|---------|
| Encode 4/5/6/8-bit | Full SSSE3/AVX2 | **Stub (returns None)** |
| Decode 4/5/6/8-bit | Full SSSE3/AVX2 | **Stub (returns None)** |
| Translation strategy | Offset-based | N/A |

---

## 6. Recommendations

### High Priority

1. **Implement GenericSimdCodec for aarch64**
   - Port encode_4bit, encode_5bit, encode_6bit, encode_8bit
   - Port decode_4bit, decode_5bit, decode_6bit, decode_8bit
   - Use NEON equivalents of SSSE3 operations

2. **Add GappedSequentialCodec to aarch64 dispatch**
   - Location: mod.rs aarch64 `encode_with_simd` and `decode_with_simd`
   - Already has NEON encode implementation, just missing dispatch

### Medium Priority

3. **Implement SIMD decode for GappedSequentialCodec**
   - Currently scalar-only on both architectures
   - Would benefit geohash and Crockford base32

4. **Fix specialized base16 decode issue**
   - Currently disabled in tests
   - Custom base16 via GenericSimdCodec works

### Low Priority

5. **Unify hex detection functions**
   - `is_standard_hex()` and `is_standard_hex_aarch64()` have same logic
   - Could share implementation

6. **Add GenericSimdCodec to aarch64 dispatch**
   - Once implemented, add to aarch64 dispatch path

---

## 7. Architecture Decision Records

### ADR-001: GenericSimdCodec aarch64 Gap

**Status**: Open

**Context**: GenericSimdCodec provides SIMD acceleration for sequential power-of-2 dictionaries. Currently x86_64-only.

**Decision**: Implement NEON equivalents using same algorithmic approach.

**Consequences**: Sequential dictionaries on aarch64 will get SIMD acceleration instead of falling back to scalar.

### ADR-002: GappedSequentialCodec Dispatch Missing

**Status**: Open

**Context**: GappedSequentialCodec has NEON encode implementation but is never dispatched on aarch64.

**Decision**: Add to aarch64 dispatch path between specialized codecs and LUT codecs.

**Consequences**: Near-sequential dictionaries (geohash, Crockford) will use SIMD encode on aarch64.

---

## 8. Test Coverage Notes

- All specialized codecs have round-trip tests
- SmallLutCodec has comprehensive SIMD path verification tests
- Base64LutCodec tests cover NEON vqtbl4q_u8 path
- GappedSequentialCodec tests verify encode but not SIMD decode (none exists)
- GenericSimdCodec tests are x86_64-only due to stub implementations

---

## Files Analyzed

| File | Purpose |
|------|---------|
| `src/simd/mod.rs` | Main dispatch logic |
| `src/simd/variants.rs` | Dictionary detection and metadata |
| `src/simd/generic/mod.rs` | GenericSimdCodec implementation |
| `src/simd/lut/gapped.rs` | GappedSequentialCodec |
| `src/simd/lut/base16.rs` | SmallLutCodec |
| `src/simd/lut/base64.rs` | Base64LutCodec |
| `src/simd/x86_64/specialized/base64.rs` | x86_64 Base64 SIMD |
| `src/simd/x86_64/specialized/base32.rs` | x86_64 Base32 SIMD |
| `src/simd/x86_64/specialized/base16.rs` | x86_64 Base16 SIMD |
| `src/simd/x86_64/specialized/base256.rs` | x86_64 Base256 SIMD |
| `src/simd/aarch64/specialized/base64.rs` | aarch64 Base64 SIMD |
| `src/simd/aarch64/specialized/base32.rs` | aarch64 Base32 SIMD |
| `src/simd/aarch64/specialized/base16.rs` | aarch64 Base16 SIMD |
| `src/simd/aarch64/specialized/base256.rs` | aarch64 Base256 SIMD |

---

*Audit completed: 2025-11-30*
*Auditor: Architect*
