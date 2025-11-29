# base-d SIMD LUT Module Refactoring Analysis

## Issue #54: Split large SIMD files by encoding variant

---

## Current Structure Analysis

### File Sizes

| File | Lines | Purpose |
|------|-------|---------|
| `lut/large.rs` | 3,387 | All base32/64 LUT codec for x86_64 + aarch64 |
| `lut/small.rs` | 995 | Base16 LUT codec for x86_64 + aarch64 |
| `lut/mod.rs` | 11 | Re-exports only |

For reference, specialized implementations are already split:
- `x86_64/specialized/base{16,32,64,256}.rs` - 454-961 lines each
- `aarch64/specialized/base{16,32,64,256}.rs` - 320-629 lines each

### `lut/large.rs` Internal Organization

**Private support types (lines 1-430):**
```rust
struct CharRange { ... }           // Character range in dictionary
enum RangeStrategy { ... }         // Range-reduction strategy
struct RangeInfo { ... }           // Range metadata for SSE/AVX2
impl RangeInfo { ... }             // 12 methods, all #[cfg(target_arch = "x86_64")]
```

**Public codec struct (lines 432-445):**
```rust
pub struct LargeLutCodec {
    metadata: DictionaryMetadata,
    encode_lut: [u8; 64],
    decode_lut: [u8; 256],
    #[cfg(target_arch = "x86_64")]
    range_info: Option<RangeInfo>,
}
```

**impl LargeLutCodec (lines 447-2054):**
- `detect_ranges()` - x86_64 only
- `from_dictionary()` - shared
- `encode()` - dispatch, shared
- `encode_neon_impl()` - aarch64
- `encode_neon_base32()` - aarch64, ~70 lines
- `encode_neon_base64()` - aarch64, ~55 lines
- `reshuffle_neon_base64()` - aarch64, ~60 lines
- `encode_scalar_base32()` - aarch64
- `encode_scalar_base64()` - aarch64
- `encode_x86_impl()` - x86_64 dispatch
- `encode_x86_base32()` - x86_64, ~90 lines
- `encode_x86_base64()` - x86_64, ~75 lines
- `reshuffle_x86_base64()` - x86_64
- `encode_scalar_x86_base32()` - x86_64
- `encode_scalar_x86_base64()` - x86_64
- `decode()` - dispatch, shared
- `is_rfc4648_base32()` - shared
- `is_standard_base64()` - shared
- `decode_ssse3_impl()` - x86_64 dispatch
- `decode_neon_impl()` - aarch64 dispatch
- `decode_ssse3_multi_range()` - x86_64
- `decode_ssse3_multi_range_5bit()` - x86_64, ~40 lines
- `decode_ssse3_multi_range_6bit()` - x86_64, ~50 lines
- `validate_and_translate_multi_range()` - x86_64
- `unpack_5bit_ssse3()` - x86_64
- `decode_ssse3_base32_rfc4648()` - x86_64, ~100 lines
- `decode_ssse3_base64_standard()` - x86_64, ~50 lines
- `reshuffle_decode_ssse3()` - x86_64
- `decode_neon_base32_rfc4648()` - aarch64, ~100 lines
- `decode_neon_base64_standard()` - aarch64
- `reshuffle_decode_neon()` - aarch64
- `decode_scalar()` - shared fallback

**Tests (lines 2057-3387):**
~1,330 lines of tests, heavily cfg-gated by architecture.

### `lut/small.rs` Internal Organization

**Public codec struct:**
```rust
pub struct SmallLutCodec {
    metadata: DictionaryMetadata,
    encode_lut: [u8; 16],
    decode_lut: [u8; 256],
}
```

**impl SmallLutCodec:**
- `from_dictionary()` - shared
- `encode()` - dispatch
- `encode_avx2_impl()` - x86_64
- `encode_ssse3_impl()` - x86_64
- `encode_neon_impl()` - aarch64
- `encode_scalar()` - shared
- `decode()` - dispatch
- `decode_avx2_impl()` - x86_64
- `decode_ssse3_impl()` - x86_64
- `decode_neon_impl()` - aarch64
- `decode_scalar()` - shared

Tests: ~400 lines, cfg-gated.

---

## Proposed Module Structure

### Option A: Split by Encoding Type (Recommended)

```
src/simd/lut/
    mod.rs              # Re-exports, shared traits/types
    common.rs           # CharRange, RangeStrategy, RangeInfo, shared helpers
    base16.rs           # SmallLutCodec (renamed from small.rs)
    base32.rs           # LargeLutCodec base32 paths
    base64.rs           # LargeLutCodec base64 paths
```

**Rationale:**
- Mirrors existing `x86_64/specialized/` and `aarch64/specialized/` structure
- Each file focuses on one bit-width (4, 5, or 6 bits)
- Platform-specific code stays inline with `#[cfg]` attributes (same as current)
- Tests stay with their implementation

**Implementation approach:**
1. Extract `CharRange`, `RangeStrategy`, `RangeInfo` to `common.rs`
2. Keep `LargeLutCodec` struct definition in new `mod.rs` or split across files
3. Move base32 encode/decode methods to `base32.rs`
4. Move base64 encode/decode methods to `base64.rs`
5. Rename `small.rs` to `base16.rs`

### Option B: Split by Platform + Encoding

```
src/simd/lut/
    mod.rs              # Re-exports, LargeLutCodec struct, dispatch
    common.rs           # Shared types
    base16/
        mod.rs
        x86_64.rs
        aarch64.rs
    base32/
        mod.rs
        x86_64.rs
        aarch64.rs
    base64/
        mod.rs
        x86_64.rs
        aarch64.rs
```

**Rationale:**
- Maximum separation of concerns
- Platform experts can work independently
- Matches how aarch64/specialized is structured

**Drawback:**
- More files, more module boilerplate
- Tests split awkwardly

---

## Recommended Approach: Option A

### New File Layout

**`lut/mod.rs`** (~50 lines)
```rust
//! LUT-based SIMD codecs for arbitrary dictionaries

mod common;
mod base16;
mod base32;
mod base64;

pub use base16::SmallLutCodec;
pub use base32::Base32LutCodec;
pub use base64::Base64LutCodec;

// Convenience type alias for backward compatibility
pub type LargeLutCodec = Base64LutCodec; // or make generic
```

**`lut/common.rs`** (~250 lines)
- `CharRange` struct
- `RangeStrategy` enum
- `RangeInfo` struct and impl (x86_64)
- Shared validation helpers
- `DictionaryMetadata` imports from `variants.rs`

**`lut/base16.rs`** (~1,000 lines)
- `SmallLutCodec` struct (current `small.rs` content)
- x86_64 encode/decode (AVX2, SSSE3)
- aarch64 encode/decode (NEON)
- Scalar fallbacks
- Tests

**`lut/base32.rs`** (~800 lines)
- `Base32LutCodec` struct
- x86_64 encode/decode
- aarch64 encode/decode
- Scalar fallbacks
- Tests

**`lut/base64.rs`** (~1,200 lines)
- `Base64LutCodec` struct
- x86_64 encode/decode
- aarch64 encode/decode
- Scalar fallbacks
- Tests

---

## Dependencies and Shared Code

### Used by all LUT codecs:
- `crate::core::dictionary::Dictionary`
- `crate::simd::variants::{DictionaryMetadata, LutStrategy, TranslationStrategy}`

### x86_64 only:
- `std::arch::x86_64::*` intrinsics
- `RangeInfo` (internal to large.rs, can stay in common.rs)

### aarch64 only:
- `std::arch::aarch64::*` intrinsics

### Cross-file shared helpers (candidates for common.rs):
- `CharRange` struct (used by large.rs only, but logically shared)
- `RangeStrategy` enum
- `RangeInfo` and its impl methods

---

## Risks and Mitigations

### Risk 1: Breaking internal APIs
**Current state:** `LargeLutCodec` is `pub` and exported from `simd/lut/mod.rs`
**Mitigation:** Keep the public type name. Either:
- Create type alias `pub type LargeLutCodec = Base64LutCodec;`
- Or keep a unified `LargeLutCodec` that delegates to base32/base64 sub-codecs

### Risk 2: RangeInfo is tightly coupled to LargeLutCodec
**Current state:** `range_info` field exists only on x86_64
**Mitigation:** Keep `RangeInfo` in `common.rs`, import where needed. The struct itself is small.

### Risk 3: Shared scalar fallbacks
**Current state:** `decode_scalar()` is shared between base32 and base64 paths
**Mitigation:** Move to `common.rs` as a free function or trait method.

### Risk 4: Tests reference internal methods
**Current state:** Tests in `mod tests` access private methods
**Mitigation:** Keep tests in same file as implementation. Only move if tests can use public API.

### Risk 5: Platform-specific cfg sprawl
**Current state:** 100+ `#[cfg(target_arch = "...")]` annotations in large.rs
**Mitigation:** This is inherent to SIMD code. No change needed.

---

## Step-by-Step Refactoring Plan

### Phase 1: Preparation (no behavior change)

1. **Create `common.rs`**
   - Move `CharRange`, `RangeStrategy`, `RangeInfo` from large.rs
   - Add `pub(super)` visibility
   - Update imports in large.rs

2. **Verify build**
   ```bash
   cargo build --all-targets
   cargo test --lib
   ```

### Phase 2: Split small.rs to base16.rs

3. **Rename `small.rs` to `base16.rs`**
   - Update `mod.rs` module declaration
   - Update re-export

4. **Verify build**

### Phase 3: Extract base32 from large.rs

5. **Create `base32.rs`**
   - Copy struct definition (modify to be base32-specific)
   - Move all `*_base32*` methods
   - Move base32-related tests
   - Import from common.rs

6. **Update large.rs**
   - Remove base32 methods
   - Remove base32 tests

7. **Update mod.rs exports**

8. **Verify build and tests**

### Phase 4: Rename large.rs to base64.rs

9. **Rename `large.rs` to `base64.rs`**
   - Rename struct to `Base64LutCodec`
   - Clean up any remaining base32 references
   - Update mod.rs

10. **Add backward-compat alias**
    - `pub type LargeLutCodec = Base64LutCodec;`

11. **Final verification**
    ```bash
    cargo build --all-targets
    cargo test --lib
    cargo clippy
    ```

---

## Implementation Order for Smith

1. `common.rs` - Create with shared types
2. `base16.rs` - Rename from small.rs
3. `base32.rs` - Extract from large.rs
4. `base64.rs` - Rename from large.rs
5. `mod.rs` - Update exports

Each step should be a separate commit for safe rollback.

---

## Files Affected

### Modified:
- `/home/w3surf/work/personal/code/base-d/src/simd/lut/mod.rs`

### Renamed:
- `small.rs` -> `base16.rs`
- `large.rs` -> `base64.rs`

### Created:
- `common.rs`
- `base32.rs`

### Unchanged:
- `/home/w3surf/work/personal/code/base-d/src/simd/mod.rs` (imports from lut/)
- `/home/w3surf/work/personal/code/base-d/src/simd/variants.rs`
- All files in `x86_64/` and `aarch64/` directories
