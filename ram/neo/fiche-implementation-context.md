# Fiche Implementation Context

*Last updated: 2025-12-04*

## Recent Session (2025-12-04)

### Built `fq` - fiche query tool

Like jq but for fiche. Queries fiche data without model needing to parse.

**Location:** `src/cli/handlers/fq.rs`

**Supported queries:**
- `.` identity
- `length`
- `.[n]` array index
- `.field.subfield` field access
- `.[] | select(.field == "value")` filtering
- `| length` chaining

**Key additions:**
- `decode_fiche_auto()` - auto-detects row vs path mode
- `NEWLINE_MARKER` (`░`) - escapes `\n` in path mode values

### Open Issues

Filed [#143](https://github.com/coryzibell/base-d/issues/143) - path mode round-trip limitations:
1. Sparse objects with numeric keys → dense arrays
2. String numbers → coerced to numeric types

Row mode (`--level full`) is workaround for exact fidelity.

### Minified row mode decoder issue

`@ᚠ=name▓@data┃ᚠˢ▓◉a▓◉b` (minified with `▓` separators) decodes to `{}`. Multiline works fine. Separate issue, not blocking fq.

---

## Previous Session (2025-12-03)

### 1. Superscript Type Markers
- Constants: `ˢ` (U+02E2 string), `ⁱ` (U+2071 int), `ᶠ` (U+1DA0 float), `ᵇ` (U+1D47 bool)
- `field_type_to_str()` outputs superscript format
- `parse_type_str()` handles both legacy (`:str`) and superscript (`ˢ`) formats
- No colon separator in new format: `nameˢ` not `name:str`

### 2. Field Name Tokenization
- Runic alphabet: 89 chars from U+16A0–U+16F8 in `tokens::RUNIC`
- Token map header: `@ᚠ=field1,ᚡ=field2,...\n`
- `serialize()` - outputs tokenized format (default)
- `serialize_readable()` - outputs human-readable without tokens
- `serialize_minified()` - tokenized + minified
- Parser detects token map by checking if first char after `@` is runic

### 3. Key Files Modified
- `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/fiche.rs`
- `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/mod.rs`

### 4. Test Status
- 446/448 tests pass
- 2 PRE-EXISTING failures (not caused by these changes):
  - `test_mixed_array_depths` - nested arrays `[[3,4],[5,6]]` come back as `[]`
  - `test_array_with_null_elements` - decoding error

## Next Task: Fix Nested Array Tests

These are pre-existing bugs in the schema encoder pipeline, not fiche-specific.

### test_mixed_array_depths
```rust
let input = r#"{"shallow":[1,2],"deep":[[3,4],[5,6]],"deeper":[[[7,8]]]}"#;
```
- `shallow` works (flat array)
- `deep` fails - comes back empty
- `deeper` works (3 levels deep but single element)

The issue is likely in:
- JSON parser flattening
- Binary pack/unpack
- JSON serializer reconstruction

### test_array_with_null_elements
```rust
let input = r#"{"items":[1,null,3,null,5]}"#;
```
- Error: `UnexpectedEndOfData { context: "reading single byte", position: 15 }`
- Likely binary encoding issue with nulls in arrays

## Spec Reference
- Docs at `/home/w3surf/work/personal/code/carrier98/docs/fiche.md` (revision 1.7)
- Token alphabet priority: Runic → Hieroglyphs → Cuneiform
- Array element separator: `◈` (diamond)
- Nested path separator: `჻` (Georgian comma)

## Testing Commands
```bash
cargo test --lib fiche::  # fiche-specific tests
cargo test --lib test_mixed_array_depths  # specific failing test
cargo test 2>&1 | tail -20  # full suite summary
```
