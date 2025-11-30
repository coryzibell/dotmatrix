# base-d Encoding Mode Auto-Detection: Architectural Analysis

## Context

Reviewing proposal for simplifying dictionary configuration through automatic mode detection.

**Current state:**
- Three encoding modes: `Chunked`, `BaseConversion`, `ByteRange`
- Manual mode specification in TOML config
- Duplicate entries for same alphabet (`base64` + `base64_math`)
- `math.rs` naming lacks precision

---

## Analysis by Question

### 1. Schema Validation: Invalid `start + length`

**Failure modes:**
- `start + length` exceeds U+10FFFF (Unicode max)
- Range crosses surrogate pair gap (U+D800-U+DFFF)
- Range contains unassigned/noncharacter codepoints
- Range overlaps Private Use Areas (may be intentional)

**Recommendation:** Validate at parse time, not runtime.

```rust
pub enum RangeValidationError {
    ExceedsUnicodeMax { start: u32, length: u32, max_valid: u32 },
    CrossesSurrogateGap { start: u32, length: u32 },
    ContainsNoncharacters { positions: Vec<u32> },
}

fn validate_unicode_range(start: u32, length: u32) -> Result<(), RangeValidationError> {
    let end = start.checked_add(length)
        .ok_or(RangeValidationError::ExceedsUnicodeMax { ... })?;

    if end > 0x10FFFF { return Err(...); }

    // Check surrogate gap
    let surrogate_start = 0xD800u32;
    let surrogate_end = 0xDFFF;
    if start <= surrogate_end && start + length > surrogate_start {
        return Err(RangeValidationError::CrossesSurrogateGap { ... });
    }

    Ok(())
}
```

**Decision:** Fail fast with actionable error. No silent truncation.

---

### 2. Backwards Compatibility: `base_conversion` alias

**Assessment:** Required for non-breaking migration.

**Implementation:**

```rust
#[derive(Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EncodingMode {
    Radix,
    #[serde(alias = "base_conversion")]
    Radix,  // ERROR: Rust doesn't allow duplicate variants
    Chunked,
    ByteRange,
}
```

Serde limitation. Alternative approach:

```rust
fn deserialize_mode<'de, D>(deserializer: D) -> Result<EncodingMode, D::Error>
where
    D: Deserializer<'de>,
{
    let s = String::deserialize(deserializer)?;
    match s.as_str() {
        "radix" | "base_conversion" => Ok(EncodingMode::Radix),
        "chunked" => Ok(EncodingMode::Chunked),
        "byte_range" => Ok(EncodingMode::ByteRange),
        _ => Err(serde::de::Error::unknown_variant(&s, &["radix", "chunked", "byte_range"])),
    }
}
```

**Deprecation path:**
1. v1.x: Accept both, emit deprecation warning for `base_conversion`
2. v2.0: Remove alias

---

### 3. Error Handling: Forced invalid mode

User specifies `mode = "chunked"` on base-58 dictionary.

**Failure scenarios:**
- `log2(58)` = 5.857... (non-integer bits per char)
- Chunked encoding requires exact bit boundaries
- SIMD paths assume power-of-two

**Options:**

| Approach | Behavior |
|----------|----------|
| A. Silent fallback | Use radix silently |
| B. Warning + fallback | Warn, use radix |
| C. Hard error | Fail config parse |

**Recommendation:** Option C (hard error).

Rationale:
- Explicit mode override is intentional user action
- Silent fallback violates principle of least surprise
- Better to fail loudly than produce unexpected output

```rust
pub enum ConfigValidationError {
    IncompatibleMode {
        dictionary: String,
        alphabet_len: usize,
        requested_mode: EncodingMode,
        reason: &'static str,
    },
}

// Error message:
// "Dictionary 'base58' has 58 characters (not a power of 2).
//  Cannot use mode 'chunked'. Use 'radix' or omit mode for auto-detection."
```

---

### 4. Load-time Overhead of Auto-Detection

**Analysis of `is_power_of_two()` cost:**

```rust
// This is the entire detection logic:
fn auto_detect_mode(len: usize) -> EncodingMode {
    if len.is_power_of_two() {
        EncodingMode::Chunked
    } else {
        EncodingMode::Radix
    }
}
```

`is_power_of_two()` compiles to:
```asm
; x86_64
popcnt rax, rdi    ; count set bits
cmp rax, 1         ; check if exactly 1
```

**Overhead:** Single CPU instruction. Negligible compared to:
- TOML parsing (~ms)
- HashMap construction (~us per entry)
- String allocation for chars (~us)

**Verdict:** No performance concern.

---

### 5. Edge Cases and Gotchas

**5.1 Base-1 dictionary**
```toml
[dictionaries.unary]
chars = "1"
```
- Length 1 is power of 2 (2^0)
- Chunked would produce 0 bits per char
- Auto-detection selects chunked incorrectly

**Mitigation:** Special case `len < 2` to use radix.

**5.2 Base-256 ambiguity**
```toml
[dictionaries.latin1]
chars = "..."  # 256 chars
```
- Power of 2 -> auto-selects chunked
- But user might want radix for leading-zero preservation

Current `base256_matrix` already handles this correctly (chunked is fine for 256).

**5.3 Empty dictionary**
```toml
[dictionaries.empty]
chars = ""
```
- Length 0 is power of 2 (edge case)
- Must validate `len >= 2` at parse time

**5.4 Dictionary with duplicates**
```toml
[dictionaries.bad]
chars = "AABB"  # Duplicate chars
```
- Current code likely handles this elsewhere
- Auto-detection unaffected

**5.5 Unicode normalization**
```toml
[dictionaries.composed]
chars = "e\u0301"  # e + combining acute = single grapheme, 2 codepoints
```
- `chars.chars().count()` counts codepoints, not graphemes
- Could silently create invalid dictionary
- **Separate issue, but worth noting**

---

### 6. ByteRange: `chars` vs `start + length`

**Current state:** ByteRange uses `start_codepoint` + implicit length of 256.

**Question:** Should ByteRange support `chars` definition?

**Analysis:**

ByteRange semantics = 1:1 byte-to-codepoint mapping. This requires:
- Exactly 256 characters
- Contiguous codepoint range (for O(1) encode/decode)

If `chars` is provided:
- Must validate exactly 256 chars
- Must validate contiguous range
- Adds complexity for no benefit

**Recommendation:** ByteRange only supports `start + length`.

If user provides `chars` for a 256-char sequential range, auto-detect as chunked (which produces identical output anyway, per `base256_matrix` comment).

```toml
# These are equivalent for 256 sequential chars:
[dictionaries.a]
start = 0x2800
length = 256
mode = "byte_range"

[dictionaries.b]
chars = "..."  # 256 chars from U+2800
# auto-detected: chunked (identical output)
```

**Note:** If future use case requires non-contiguous 256-char dictionary, that would be chunked mode, not byte_range.

---

### 7. Padding Character Handling

**Current state:** `padding` is optional field in config.

**Proposed change:** No change needed. Padding is orthogonal to mode selection.

```toml
[dictionaries.base64]
chars = "ABC.../"
padding = "="
# auto-detected: chunked (64 = 2^6)
# padding = "=" still explicit
```

**Consideration:** Should chunked mode auto-infer padding?

**No.** Padding behavior varies:
- RFC 4648 base64: `=` padding required
- base64url: padding optional or omitted
- base32: `=` padding
- base16: no padding

Keep padding explicit in config.

---

## Proposed Schema (Refined)

```rust
#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DictionaryConfig {
    // Definition style 1: Explicit characters
    #[serde(default)]
    pub chars: Option<String>,

    // Definition style 2: Unicode range
    #[serde(default)]
    pub start: Option<char>,  // Or u32 codepoint
    #[serde(default)]
    pub length: Option<u32>,

    // Optional: override auto-detected mode
    #[serde(default, deserialize_with = "deserialize_mode_optional")]
    pub mode: Option<EncodingMode>,

    // Padding (chunked mode only)
    #[serde(default)]
    pub padding: Option<String>,

    // Metadata
    #[serde(default = "default_true")]
    pub common: bool,
}
```

**Validation logic:**

```rust
impl DictionaryConfig {
    pub fn resolve(&self, name: &str) -> Result<ResolvedDictionary, ConfigError> {
        // 1. Determine alphabet
        let (chars, alphabet_source) = match (&self.chars, &self.start, &self.length) {
            (Some(c), None, None) => (c.chars().collect(), AlphabetSource::Explicit),
            (None, Some(s), Some(l)) => {
                validate_unicode_range(*s as u32, *l)?;
                let chars = (0..*l).map(|i| char::from_u32(*s as u32 + i).unwrap()).collect();
                (chars, AlphabetSource::Range)
            },
            (None, Some(s), None) => {
                // Default length for range
                return Err(ConfigError::MissingLength { name });
            },
            _ => return Err(ConfigError::AmbiguousDefinition { name }),
        };

        // 2. Validate alphabet size
        let len = chars.len();
        if len < 2 {
            return Err(ConfigError::AlphabetTooSmall { name, len });
        }

        // 3. Determine mode
        let mode = match &self.mode {
            Some(EncodingMode::ByteRange) => {
                // ByteRange requires range definition and length=256
                if alphabet_source != AlphabetSource::Range || len != 256 {
                    return Err(ConfigError::ByteRangeRequiresRange256 { name });
                }
                EncodingMode::ByteRange
            },
            Some(EncodingMode::Chunked) => {
                if !len.is_power_of_two() {
                    return Err(ConfigError::ChunkedRequiresPowerOfTwo { name, len });
                }
                EncodingMode::Chunked
            },
            Some(EncodingMode::Radix) => EncodingMode::Radix,
            None => {
                // Auto-detect
                if len.is_power_of_two() && len >= 2 {
                    EncodingMode::Chunked
                } else {
                    EncodingMode::Radix
                }
            }
        };

        Ok(ResolvedDictionary { chars, mode, padding: self.padding.clone(), ... })
    }
}
```

---

## Migration Path

### Phase 1: Add auto-detection (non-breaking)
1. Rename `math.rs` -> `radix.rs`
2. Add `Radix` variant with `base_conversion` alias
3. Make `mode` optional with auto-detection
4. Existing configs unchanged (explicit mode still works)

### Phase 2: Simplify bundled dictionaries
1. Remove `_math` suffix variants
2. Remove redundant `mode` fields where auto-detection matches
3. Add deprecation warning for `base_conversion` in user configs

### Phase 3: Clean slate (v2.0)
1. Remove `base_conversion` alias
2. Require explicit `mode` only for overrides

---

## Concerns and Alternatives

### Concern: Auto-detection hides important choice

**Counter:** The mode is deterministic from alphabet length. No hidden magic.

Users who care about mode can still specify explicitly. Auto-detection is convenience, not opacity.

### Alternative: Separate types instead of modes

```rust
pub enum Dictionary {
    Chunked(ChunkedDictionary),
    Radix(RadixDictionary),
    ByteRange(ByteRangeDictionary),
}
```

**Tradeoff:** More type safety, more complex API. Current approach with runtime dispatch is simpler and sufficient.

### Alternative: Always require explicit mode

**Tradeoff:** More verbose configs, but eliminates any ambiguity. Against stated goal of simplification.

---

## Verdict

The proposal is sound. Key refinements:

1. **Validate ranges at parse time** - fail fast with clear errors
2. **Hard error on incompatible mode override** - no silent fallbacks
3. **Special-case len < 2** - prevent chunked with 0 bits
4. **ByteRange only via range syntax** - no chars definition
5. **Keep padding explicit** - not auto-inferred
6. **Deprecation alias for base_conversion** - smooth migration

Performance impact: negligible. API improvement: significant.

---

## Files Affected

Implementation would touch:

| File | Changes |
|------|---------|
| `src/encoders/algorithms/math.rs` | Rename to `radix.rs` |
| `src/encoders/algorithms/mod.rs` | Update module declaration |
| `src/core/config.rs` | Add auto-detection, validation, serde alias |
| `dictionaries.toml` | Remove duplicates, simplify |
| Tests throughout | Update mode references |

---

## Handoff

Smith can implement in this order:
1. Rename `math.rs` -> `radix.rs` (mechanical)
2. Add serde alias for `base_conversion` -> `Radix`
3. Make mode field optional in `DictionaryConfig`
4. Add auto-detection logic in config parsing
5. Add validation for incompatible overrides
6. Update bundled `dictionaries.toml`
7. Update tests

Each step is independently testable.
