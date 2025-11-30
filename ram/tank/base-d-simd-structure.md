# base-d SIMD LUT Module Structure - Current State

**Scanned:** 2025-11-30
**Repository:** ~/work/personal/code/base-d

## Directory Tree

```
src/simd/
├── generic/
│   └── mod.rs
├── lut/
│   ├── mod.rs (main exports)
│   ├── common.rs (shared types & logic)
│   ├── base16.rs (SmallLutCodec)
│   ├── base32.rs (Base32-specific impls)
│   ├── base64.rs (Base64LutCodec)
│   └── gapped.rs (GappedSequentialCodec)
├── x86_64/
│   ├── common.rs (x86-specific helpers)
│   ├── mod.rs
│   └── specialized/
│       ├── base16.rs
│       ├── base32.rs
│       ├── base64.rs
│       ├── base256.rs
│       └── mod.rs
├── mod.rs
├── translate.rs
└── variants.rs
```

## Current LUT Module Files (COMPLETE REFACTOR)

### Core LUT Files - Phase Complete ✓

1. **lut/mod.rs** - Main module with public exports
   - Exports: `SmallLutCodec`, `Base64LutCodec`, `GappedSequentialCodec`
   - Marks `base32` as private (implementation detail)

2. **lut/common.rs** - Shared types for LUT-based codecs
   - `CharRange` struct (dictionary range metadata)
   - `RangeStrategy` enum (1-16 range compression strategies)
   - `RangeInfo` struct (x86_64-specific range-reduction metadata)
   - Multi-range builders

3. **lut/base16.rs** - SmallLutCodec (≤16 character dictionaries)
   - SIMD codec for small arbitrary dictionaries
   - Uses pshufb (x86) / vqtbl1q_u8 (ARM)
   - 16-byte encoding LUT, 256-byte decoding LUT
   - Power-of-2 base only

4. **lut/base32.rs** - Base32-specific implementations
   - 5-bit encoding strategies
   - NEON (aarch64), x86 variants
   - 5 bytes → 8 characters, 16 chars → 10 bytes
   - Marked private (used by Base64LutCodec)

5. **lut/base64.rs** - Base64LutCodec (17-64 character dictionaries)
   - SIMD codec for base64-scale arbitrary dictionaries
   - Platform strategies: ARM NEON, x86 AVX-512 VBMI, scalar fallback
   - 64-byte encoding LUT, 256-byte decoding LUT
   - Power-of-2 base only

6. **lut/gapped.rs** - GappedSequentialCodec
   - Handles near-sequential dictionaries with gaps
   - Examples: Geohash, Crockford Base32
   - Uses threshold comparisons instead of LUT
   - Supports ≤8 gaps

## Architecture Notes

### Type Structure
- **DictionaryMetadata** (in `variants.rs`): Common metadata for all codecs
- **LutStrategy** (in `variants.rs`): Strategy enum for LUT selection
- **TranslationStrategy** (in `variants.rs`): Platform-specific implementation choice

### x86_64 Specialization
- `/src/simd/x86_64/specialized/` contains platform-specific implementations:
  - **base16.rs** - SSSE3 pshufb for SmallLutCodec
  - **base32.rs** - SSE/AVX2 for Base32 5-bit encoding
  - **base64.rs** - AVX2 or AVX-512 VBMI for Base64LutCodec
  - **base256.rs** - For future 7-8 bit bases

### Supported Bases
- **Base16**: Via SmallLutCodec (power-of-2, ≤16)
- **Base32**: Via Base64LutCodec (power-of-2, 17-64)
- **Base64**: Via Base64LutCodec (power-of-2, 17-64)
- **Near-sequential**: Via GappedSequentialCodec (with gaps)

## R7 Phase Status

### R7.1 - LUT Architecture ✓ COMPLETE
- File organization complete
- `common.rs` with shared types ✓
- `base16.rs`, `base32.rs`, `base64.rs` as separate modules ✓
- `gapped.rs` for gap-based sequential ✓
- Clean module exports in `mod.rs` ✓

### R7.2 - SIMD Implementations
- x86_64 specializations present in `/specialized/`
- ARM NEON mentioned in base64.rs
- Scalar fallback implemented
- Status: PARTIALLY IMPLEMENTED (needs review)

### R7.3 - Performance Features
- Range-reduction for x86_64 (common.rs)
- Multi-threshold compression (1-16 ranges)
- Threshold comparisons for gapped
- Status: IMPLEMENTED (needs testing)

## Files for Review

Key files to examine for R7 phase completion:

1. `/home/w3surf/work/personal/code/base-d/src/simd/lut/mod.rs` - Module structure
2. `/home/w3surf/work/personal/code/base-d/src/simd/lut/common.rs` - Shared types
3. `/home/w3surf/work/personal/code/base-d/src/simd/lut/base16.rs` - SmallLutCodec
4. `/home/w3surf/work/personal/code/base-d/src/simd/lut/base64.rs` - Base64LutCodec
5. `/home/w3surf/work/personal/code/base-d/src/simd/lut/gapped.rs` - GappedSequentialCodec
6. `/home/w3surf/work/personal/code/base-d/src/simd/x86_64/specialized/` - Platform code

## Summary

The LUT module has been **fully refactored** from a `small.rs` / `large.rs` structure to a cleaner architecture with:
- `common.rs` for shared infrastructure
- `base16.rs`, `base32.rs`, `base64.rs` for specific implementations
- `gapped.rs` for gap-aware sequential dictionaries

**Architecture Status: REFACTORING COMPLETE**

Next steps would be:
1. Verify x86_64 specialization implementations
2. Check ARM NEON implementations
3. Add tests for each codec type
4. Performance benchmarking
