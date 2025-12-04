# Fiche Test Coverage Analysis

**Project:** base-d
**File:** `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/fiche.rs`
**Date:** 2025-12-04

## Summary

Path mode has **NO roundtrip tests**. The functions exist (`serialize_path_mode`, `parse_path_mode`) but there are zero test cases verifying the encode/decode cycle.

## Path Mode Status

### Functions Implemented
- `serialize_path_mode(json: &str) -> Result<String, SchemaError>` (line 952)
- `parse_path_mode(input: &str) -> Result<String, SchemaError>` (line 1150)

### Public API (mod.rs)
- `encode_fiche_path(json: &str) -> Result<String, SchemaError>` (line 177)
- `decode_fiche_path(path_input: &str) -> Result<String, SchemaError>` (line 182)

### Tests Found: **ZERO**

No tests exist for path mode functionality in:
- `fiche.rs` tests module (lines 1412-1839)
- `mod.rs` integration tests (lines 226-853)
- `edge_cases.rs` (schema edge case tests)

## Existing Fiche Tests (Non-Path Mode)

Located in `fiche.rs` lines 1412-1839:

| Test Name | Type | Coverage |
|-----------|------|----------|
| `test_simple_roundtrip` | Roundtrip | Basic fiche parse/serialize |
| `test_tokenized_roundtrip` | Roundtrip | Token map (runic) roundtrip |
| `test_legacy_type_format_parsing` | Parse | Pre-1.7 format compatibility |
| `test_arrays_legacy_syntax` | Parse | Old str[] array syntax |
| `test_arrays_new_bracket_syntax` | Roundtrip | New superscript array syntax |
| `test_nulls` | Roundtrip | Null bitmap handling |
| `test_embedded_json` | Roundtrip | Embedded JSON in values |
| `test_no_root_key` | Parse | Anonymous root |
| `test_type_parsing` | Unit | Type string parsing |
| `test_nested_arrays` | Roundtrip | Inline primitive arrays |
| `test_space_preservation` | Roundtrip | SPACE_MARKER encoding |
| `test_minified_output` | Roundtrip | Minified format with value restoration |
| `test_metadata_annotation` | Roundtrip | Schema metadata brackets |
| `test_metadata_minified` | Roundtrip | Minified with metadata |
| `test_value_dictionary` | Roundtrip | Hieroglyph value tokenization |
| `test_value_dictionary_no_duplicates` | Behavior | No dict when no duplicates |

**Total: 16 tests for standard fiche mode**

## Path Mode Features (Untested)

From code analysis, path mode supports:

1. **Path tokenization** - Runic tokens for repeated path segments
2. **Value tokenization** - Hieroglyph tokens for repeated values
3. **Special markers:**
   - `TRUE_MARKER` = "down tack" (U+22A4)
   - `FALSE_MARKER` = "up tack" (U+22A5)
   - `EMPTY_ARRAY_MARKER` = "mathematical white square brackets" (U+27E6, U+27E7)
   - `EMPTY_OBJECT_MARKER` = "mathematical angle brackets" (U+27E8, U+27E9)
   - `NULL_VALUE` = "empty set" (U+2205)
   - `SPACE_MARKER` = "dark shade" (U+2593)

4. **Nested path separator:** `NEST_SEP` = Georgian paragraph separator (U+10FB)

## Required Tests for Path Mode

### Basic Roundtrip Tests Needed
1. Simple object roundtrip
2. Nested object roundtrip
3. Array of objects roundtrip
4. Mixed arrays and objects
5. Empty arrays/objects
6. Null values
7. Boolean values
8. Numeric values (int, float)
9. String values with spaces
10. Unicode strings

### Dictionary Tests Needed
1. Path segment tokenization (runic)
2. Value tokenization (hieroglyphs)
3. Dictionary roundtrip preservation

### Edge Case Tests Needed
1. Deep nesting (a.b.c.d.e)
2. Array indices in paths
3. Mixed types in same document
4. Empty input handling
5. Large documents

## Recommendation

**Priority: HIGH** - Path mode is exposed in public API but has zero test coverage. Any refactoring or bug fix could silently break functionality.

Suggested test file location: Add tests to `fiche.rs` test module, or create dedicated `path_mode_tests.rs`.

---

*Research by Tank | Operator*
