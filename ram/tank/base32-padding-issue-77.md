# Base32 Padding Validation Inconsistency - Issue #77

**Status:** BLOCKER
**Source:** Construct/Deus quality review
**Repo:** coryzibell/base-d

## Issue Description

Base32 padding validation differs between SIMD and scalar code paths. SIMD accepts some invalid padding that scalar rejects, causing inconsistent behavior and potential round-trip failures.

## Current Code Analysis

### SIMD Path (x86_64 and aarch64)

**Location:** `src/simd/x86_64/specialized/base32.rs:53-92` and `src/simd/aarch64/specialized/base32.rs:37-61`

```rust
pub fn decode(encoded: &str, variant: Base32Variant) -> Option<Vec<u8>> {
    let encoded_bytes = encoded.as_bytes();

    // Calculate output size
    let input_no_padding = encoded.trim_end_matches('=');
    let output_len = (input_no_padding.len() / 8) * 5
        + match input_no_padding.len() % 8 {
            0 => 0,
            2 => 1,
            4 => 2,
            5 => 3,
            7 => 4,
            _ => return None, // Invalid base32
        };
    // ...
}
```

**SIMD Validation:**
- Strips padding with `trim_end_matches('=')`
- Validates remainder length: accepts only 0, 2, 4, 5, 7
- **Does NOT validate:**
  - That padding amount is correct for the data length
  - That padding appears only at the end
  - Intermediate padding characters

### Scalar Path (used for remainders)

**Location:** `src/simd/x86_64/common.rs:97-130`

```rust
pub fn decode_scalar_chunked<F>(
    data: &[u8],
    char_to_index: &mut F,
    result: &mut Vec<u8>,
    bits_per_char: usize,
) -> bool
where
    F: FnMut(u8) -> Option<u8> + ?Sized,
{
    // Processes characters one by one
    // ...
}
```

**Scalar Validation:**
- Attempts to decode each character via `char_to_index`
- Returns false on invalid characters
- **Does NOT validate:**
  - Padding at all (padding is pre-stripped by SIMD)
  - When called directly, has no concept of padding

## The Inconsistency

The SIMD path performs **lenient validation** - it strips all trailing `=` characters and only checks that the remaining length modulo 8 is valid. This means:

**SIMD accepts (incorrectly):**
- `"MY======"` (7 padding chars instead of 6) → strips to "MY", len=2 ✓
- `"MZXQ==="` (3 padding chars instead of 4) → strips to "MZXQ", len=4 ✓
- `"MZXW6YQ"` (0 padding instead of 1) → len=7 ✓

**Scalar path** called on remainders has no padding validation at all since padding is pre-stripped.

## RFC 4648 Requirements

Per RFC 4648 Section 6, Base32 has **strict padding rules**:

| Input bits | Data chars | Padding chars | Total | Valid remainder |
|-----------|------------|---------------|-------|-----------------|
| 40 (5 bytes) | 8 | 0 | 8 | 0 |
| 32 (4 bytes) | 7 | 1 | 8 | 7 |
| 24 (3 bytes) | 5 | 3 | 8 | 5 |
| 16 (2 bytes) | 4 | 4 | 8 | 4 |
| 8 (1 byte) | 2 | 6 | 8 | 2 |

**Requirements:**
1. Output length MUST be a multiple of 8 characters
2. Padding MUST use exactly the number of `=` characters shown
3. Bits with value zero are added on the right to form integral 5-bit groups

## Impact

**Correctness:** Violates RFC 4648 compliance
**Round-trip failures:** Possible when:
- Encoding produces correct padding (e.g., `"MY======"`)
- Decoding accepts incorrect padding (e.g., `"MY="`)
- Re-encoding may produce different padding

**Behavioral inconsistency:**
- SIMD path accepts malformed input
- Potential security/validation bypass issues

## Root Cause

The SIMD decode functions prioritize performance by using simple `trim_end_matches('=')` without validating:

1. **Correct padding count** for the data length
2. **Total length** is a multiple of 8
3. **Padding position** (only trailing)

Both x86_64 and aarch64 implementations share this issue.

## What Needs to Change

1. **Extract common padding validation function**
   - Validate total length is multiple of 8
   - Calculate expected padding count based on remainder
   - Verify padding count matches expectation

2. **Apply to both SIMD paths**
   - x86_64 `decode()` in `src/simd/x86_64/specialized/base32.rs`
   - aarch64 `decode()` in `src/simd/aarch64/specialized/base32.rs`

3. **Add comprehensive test matrix**
   - Test all valid remainder lengths (0, 2, 4, 5, 7)
   - Test all valid padding counts (0, 1, 3, 4, 6)
   - Test invalid cases (wrong padding count, invalid remainders)
   - Test round-trip consistency

4. **Verify RFC 4648 compliance**
   - Reject inputs with incorrect padding
   - Ensure SIMD and scalar produce identical validation results

## Files Affected

- `/home/w3surf/.matrix/ram/tank/base-d-research/src/simd/x86_64/specialized/base32.rs` (lines 53-92)
- `/home/w3surf/.matrix/ram/tank/base-d-research/src/simd/aarch64/specialized/base32.rs` (lines 37-61)
- New: Common padding validation utility (location TBD)
- Tests: Comprehensive padding validation test matrix

## Recommendation

**Priority:** BLOCKER - affects correctness and RFC compliance

**Handoff:**
- Deus identifies → **Smith implements** → Deus verifies → Neo merges

**Implementation approach:**
Create a common validation function that checks:
```rust
fn validate_base32_padding(input: &str) -> Option<&str> {
    // 1. Check total length is multiple of 8
    // 2. Find padding boundary
    // 3. Calculate expected padding count
    // 4. Verify actual padding matches expected
    // 5. Return data portion (without padding) if valid
}
```

This ensures single source of truth for padding logic across all code paths.
