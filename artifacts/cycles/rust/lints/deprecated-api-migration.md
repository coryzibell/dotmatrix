# Deprecated API Migration

## Overview

This document covers migrating deprecated Dictionary constructors to the builder pattern in the base-d project.

## The Lint

**Lint:** `deprecated`
**Severity:** Error (with `-D warnings`)
**Triggered by:** Using deprecated functions or methods marked with `#[deprecated]`

## Why Fix vs Suppress

**Fix** deprecated API usage rather than suppressing warnings because:

1. **Clean Upgrade Path:** The deprecated APIs will be removed in future versions. Fixing now prevents breakage.
2. **API Evolution:** The builder pattern is more flexible and extensible than multiple constructor variants.
3. **Better Documentation:** Builder methods self-document through method names (`.chars()`, `.mode()`, `.padding()`).
4. **Type Safety:** The builder enforces required fields at compile time through the `build()` method.

## The Migration Pattern

### Before (Deprecated)

```rust
// Simple constructor
Dictionary::new(chars)

// With mode and padding
Dictionary::new_with_mode(chars, mode, padding)

// Full constructor with byte range
Dictionary::new_with_mode_and_range(chars, mode, padding, start_codepoint)
```

### After (Builder Pattern)

```rust
// Simple builder
Dictionary::builder().chars(chars).build()

// With mode and padding
Dictionary::builder()
    .chars(chars)
    .mode(mode)
    .padding(padding)
    .build()

// Full builder with byte range
Dictionary::builder()
    .mode(mode)
    .start_codepoint(start)
    .build()

// Optional padding example
let mut builder = Dictionary::builder().chars(chars).mode(mode);
if let Some(p) = padding {
    builder = builder.padding(p);
}
builder.build()
```

## Files Affected in base-d

### Production Code
- `src/core/dictionary.rs` - Internal constructor calls (allowed via `#[allow(deprecated)]`)
- `src/features/detection.rs` - Dictionary creation from config
- `src/tests.rs` - Test helper functions

### Documentation
- `src/lib.rs` - All doctests updated to use builder pattern

### Test Code (allowed via `#[allow(deprecated)]`)
- `src/core/dictionary.rs` - Unit tests
- `src/simd/mod.rs` - SIMD integration tests
- `src/encoders/algorithms/byte_range.rs` - Byte range tests
- `src/encoders/streaming/mod.rs` - Streaming tests
- `src/features/hashing.rs` - Hash tests
- `src/simd/lut/base16.rs` - Base16 LUT tests
- `src/simd/lut/base32.rs` - Base32 LUT tests
- `src/simd/lut/base64.rs` - Base64 LUT tests
- `src/simd/variants.rs` - Variant tests
- `src/simd/generic/mod.rs` - Generic SIMD tests
- `src/simd/x86_64/specialized/*.rs` - Specialized SIMD tests

## Strategy

1. **Production code:** Fully migrated to builder pattern
2. **Test code:** Allowed deprecated usage via `#[allow(deprecated)]` on test modules
3. **Internal calls:** Deprecated functions call each other internally (allowed via `#[allow(deprecated)]` on the functions themselves)

## Related Lints Fixed

### needless_range_loop

**Pattern:**
```rust
// Before
for i in 0..n {
    array[i] = value;
}

// After
array.iter_mut().take(n).for_each(|val| *val = value);

// Or with enumerate
for (i, val) in array.iter_mut().enumerate().take(n) {
    *val = compute(i);
}
```

**Files affected:**
- `src/simd/lut/common.rs` - LUT building
- `src/simd/lut/base16.rs` - Encoding LUT construction
- `src/simd/lut/base32.rs` - Bit masking
- `src/simd/lut/base64.rs` - Encoding LUT construction
- `src/simd/x86_64/specialized/base256.rs` - Dictionary LUT building

### redundant_locals

**Pattern:**
```rust
// Before
let bits_per_char = bits_per_char;  // Redundant

// After
// Just use the variable directly
```

**Files affected:**
- `src/simd/x86_64/common.rs` - Padding calculation

### should_implement_trait

**Pattern:**
```rust
// Before
pub fn from_str(s: &str) -> Result<Self, String> { ... }

// After (when intentionally not implementing FromStr)
#[allow(clippy::should_implement_trait)]
pub fn from_str(s: &str) -> Result<Self, String> { ... }
```

**Files affected:**
- `src/core/dictionary.rs` - Deprecated from_str method
- `src/features/hashing.rs` - HashAlgorithm::from_str

### large_enum_variant

**Pattern:**
```rust
// Suppress when boxing would add unnecessary complexity
#[allow(clippy::large_enum_variant)]
pub(super) enum HasherWriter { ... }
```

**Files affected:**
- `src/encoders/streaming/hasher.rs` - Hash state management

## Verification

After migration, verify with:

```bash
cargo fmt
cargo test
cargo clippy --all-targets -- -D warnings
```

All should pass with zero warnings or errors.

## Lessons Learned

1. **Deprecation in stages:** Mark APIs as deprecated first, migrate gradually, remove in next major version.
2. **Test code flexibility:** Using `#[allow(deprecated)]` in test modules reduces migration burden while keeping production code clean.
3. **Internal consistency:** Deprecated functions can call each other internally without warnings via `#[allow(deprecated)]`.
4. **Builder benefits:** The builder pattern scales better than multiple constructor variants as APIs evolve.

## Related Resources

- [Rust API Guidelines - Flexibility](https://rust-lang.github.io/api-guidelines/flexibility.html)
- [Builder Pattern](https://rust-unofficial.github.io/patterns/patterns/creational/builder.html)
- [Clippy Lint List](https://rust-lang.github.io/rust-clippy/master/index.html)
