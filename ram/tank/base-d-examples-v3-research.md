# base-d Examples Research for v3.0.0 Release

**Date:** 2025-12-01
**Status:** All examples compile and execute successfully

## Summary

All 9 examples in `/home/w3surf/work/personal/code/base-d/examples/` compile and run without issues against the current API (v2.0.12).

## Examples Inventory

| File | Purpose | Status |
|------|---------|--------|
| `hello_world.rs` | Basic encode/decode with cards dictionary | PASS |
| `custom_dictionary.rs` | Create custom DNA (base-4) dictionary | PASS |
| `list_dictionaries.rs` | List all built-in dictionaries | PASS |
| `base1024_demo.rs` | CJK ideograph encoding demo | PASS |
| `matrix_demo.rs` | base256_matrix with Japanese/geometric chars | PASS |
| `auto_simd.rs` | Automatic SIMD selection demonstration | PASS |
| `simd_check.rs` | CPU feature detection and SIMD status | PASS |
| `test_base256_simd.rs` | SIMD boundary testing for base256 | PASS |
| `generate_base1024.rs` | Utility to generate base256 dictionary file | PASS |

## API Usage Patterns (Current)

All examples use the same API pattern:

```rust
use base_d::{Dictionary, DictionaryRegistry, encode, decode};

// Load from registry
let config = DictionaryRegistry::load_default()?;
let dict_config = config.get_dictionary("name").unwrap();

// Build dictionary
let chars: Vec<char> = dict_config.chars.chars().collect();
let mut builder = Dictionary::builder()
    .chars(chars)
    .mode(dict_config.effective_mode());
if let Some(pad) = dict_config.padding.as_ref().and_then(|s| s.chars().next()) {
    builder = builder.padding(pad);
}
let dictionary = builder.build()?;

// Use
let encoded = encode(data, &dictionary);
let decoded = decode(&encoded, &dictionary)?;
```

## Key Public API Elements Used

- `DictionaryRegistry::load_default()` - Load built-in dictionaries
- `DictionaryRegistry::get_dictionary(name)` - Get specific dictionary config
- `DictionaryConfig::effective_mode()` - Get encoding mode
- `DictionaryConfig::chars` - Character string
- `DictionaryConfig::padding` - Optional padding character
- `DictionaryConfig::start_codepoint` - For ByteRange mode
- `Dictionary::builder()` - Builder pattern
- `DictionaryBuilder::chars(Vec<char>)` - Set characters
- `DictionaryBuilder::chars_from_str(&str)` - Convenience method
- `DictionaryBuilder::mode(EncodingMode)` - Set encoding mode
- `DictionaryBuilder::padding(char)` - Set padding
- `DictionaryBuilder::build()` - Finalize
- `Dictionary::base()` - Get dictionary size
- `Dictionary::mode()` - Get encoding mode
- `encode(&[u8], &Dictionary)` - Encode function
- `decode(&str, &Dictionary)` - Decode function
- `EncodingMode::{Radix, Chunked, ByteRange}` - Mode enum

## Observations

1. **Naming**: File `generate_base1024.rs` actually generates base256 (Matrix-style), name is misleading
2. **Consistency**: All examples follow the same builder pattern
3. **No deprecated API**: All examples use current, stable API
4. **SIMD**: Works correctly, detected AVX2 on test system
5. **ByteRange mode**: Used for base256 dictionaries with start_codepoint

## Recommendations for v3.0.0

1. **Rename `generate_base1024.rs`** to `generate_base256_matrix.rs` for accuracy
2. **Consider adding**: A `DictionaryRegistry::build_dictionary(name)` convenience method to reduce boilerplate
3. **All examples are v3-ready**: No API divergence found

## Files

- Examples directory: `/home/w3surf/work/personal/code/base-d/examples/`
- Library entry: `/home/w3surf/work/personal/code/base-d/src/lib.rs`
