# Issue #77: Base32 Padding Validation Fix

## Problem
SIMD Base32 decode implementations (x86_64 and aarch64) used lenient padding validation - simply stripped all `=` characters and checked remainder length. Did not verify correct padding count per RFC 4648.

## RFC 4648 Padding Requirements

| Data chars (mod 8) | Required padding | Total length |
|-------------------|------------------|--------------|
| 0 | 0 `=` | Multiple of 8 |
| 2 | 6 `=` | 8 |
| 4 | 4 `=` | 8 |
| 5 | 3 `=` | 8 |
| 7 | 1 `=` | 8 |

Invalid data lengths: 1, 3, 6 (mod 8)

## Solution Implemented

### 1. Created `validate_base32_padding()` helper function
- Validates total length is multiple of 8 if padding present
- Checks padding count matches expected for data length
- Accepts unpadded input (some implementations omit padding)
- Returns `&str` to data portion (without padding) if valid, `None` otherwise

### 2. Applied to both architectures
- `/home/w3surf/work/personal/code/base-d/src/simd/x86_64/specialized/base32.rs`
- `/home/w3surf/work/personal/code/base-d/src/simd/aarch64/specialized/base32.rs`

### 3. Updated decode flow
- Call `validate_base32_padding(encoded)?` at entry to `decode()`
- Removed redundant padding stripping from `decode_avx2_impl()`, `decode_ssse3_impl()`, `decode_neon_impl()`
- All implementations now receive pre-validated, padding-stripped input

### 4. Added comprehensive test coverage
- `test_padding_validation_correct()` - Valid padded and unpadded cases
- `test_padding_validation_incorrect()` - Invalid padding counts, lengths, data lengths

## Files Modified
- `/home/w3surf/work/personal/code/base-d/src/simd/x86_64/specialized/base32.rs`
  - Added `validate_base32_padding()` (lines 47-82)
  - Updated `decode()` to use validation (line 92)
  - Removed padding stripping from decode impls
  - Added test cases (lines 932-962)

- `/home/w3surf/work/personal/code/base-d/src/simd/aarch64/specialized/base32.rs`
  - Added `validate_base32_padding()` (lines 33-68)
  - Updated `decode()` to use validation (line 76)
  - Removed padding stripping from decode impl
  - Added test cases (lines 598-628)

## Test Results
All 231 tests pass, including new padding validation tests.

## Impact
- Rejects previously-accepted invalid padding
- No performance impact (validation is O(n) scan, same as previous strip operation)
- Maintains backward compatibility with unpadded input
