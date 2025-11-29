# base-d Test Compilation Fix

## Issue
Test compilation failures in `/home/w3surf/work/personal/code/base-d/` after Smith's safety work.

## Root Cause
Test modules missing necessary imports. The module-level imports were behind `#[cfg(target_arch = "...")]` gates and not accessible to test modules.

## Fix Applied

### `/home/w3surf/work/personal/code/base-d/src/simd/translate.rs`
Added imports to test module:
```rust
#[cfg(test)]
mod tests {
    use super::{SequentialTranslate, SimdTranslate};

    #[cfg(target_arch = "x86_64")]
    use std::arch::x86_64::*;

    // ... tests
}
```

### `/home/w3surf/work/personal/code/base-d/src/simd/mod.rs`
Added imports to test module:
```rust
#[cfg(test)]
mod tests {
    use super::{decode_with_simd, encode_with_simd, has_ssse3, Dictionary};
    use crate::core::config::EncodingMode;

    // ... tests
}
```

## Status
- ✅ All 229 lib tests pass
- ✅ All 7 doc tests pass
- ✅ No compilation errors

## Notes
- Smith's safety work in `src/simd/lut/large.rs` (debug_assert additions) is still uncommitted
- Test fixes are independent and straightforward import issues
- No logic changes, only missing use statements
