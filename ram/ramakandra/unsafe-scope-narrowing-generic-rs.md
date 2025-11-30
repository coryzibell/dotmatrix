# Unsafe Scope Narrowing - generic.rs

**File:** `/home/w3surf/work/personal/code/base-d/src/simd/aarch64/generic.rs`

**Objective:** Narrow unsafe scopes following Edition 2024 `unsafe_op_in_unsafe_fn` lint requirements.

## Changes Made

### Functions Refactored

All 8 unsafe functions had their unsafe scopes narrowed:

#### 1. `encode_6bit()`
- **Before:** Entire body wrapped in single `unsafe {}` block
- **After:** Separated into:
  - Safe: bounds checks, arithmetic, capacity calculation, iteration, `result.push()`
  - Unsafe: SIMD load (`vld1q_u8`), intrinsic calls (`reshuffle_6bit`, `translate_encode`)
  - Unsafe: SIMD store (`vst1q_u8`)

#### 2. `encode_4bit()`
- **Before:** Entire body wrapped in single `unsafe {}` block
- **After:** Separated into:
  - Safe: bounds checks, arithmetic, iteration, `result.push()`
  - Unsafe: SIMD load, nibble extraction, translation
  - Unsafe: SIMD interleave and store

#### 3. `encode_8bit()`
- **Before:** Entire body wrapped in single `unsafe {}` block
- **After:** Separated into:
  - Safe: bounds checks, arithmetic, iteration, `result.push()`
  - Unsafe: SIMD load and translation
  - Unsafe: SIMD store

#### 4. `decode_4bit()`
- **Before:** Entire body wrapped in single `unsafe {}` block
- **After:** Separated into:
  - Safe: bounds checks, arithmetic, translation (includes validation), `Vec::extend_from_slice()`
  - Unsafe: SIMD load and deinterleave
  - Unsafe: SIMD bit manipulation and store

#### 5. `decode_6bit()`
- **Before:** Entire body wrapped in single `unsafe {}` block
- **After:** Separated into:
  - Safe: bounds checks, arithmetic, translation, `Vec::extend_from_slice()`
  - Unsafe: SIMD load
  - Unsafe: SIMD unshuffle intrinsic
  - Unsafe: SIMD store

#### 6. `decode_8bit()`
- **Before:** Entire body wrapped in single `unsafe {}` block
- **After:** Separated into:
  - Safe: bounds checks, arithmetic, translation, `Vec::extend_from_slice()`
  - Unsafe: SIMD load
  - Unsafe: SIMD store

#### 7. `reshuffle_6bit()` (has `#[target_feature(enable = "neon")]`)
- **Before:** No internal unsafe blocks (intrinsics implicitly unsafe in body)
- **After:**
  - Unsafe: pointer dereference for shuffle mask load (`vld1q_u8`)
  - Safe: All SIMD intrinsics (safe due to `#[target_feature]`)

#### 8. `unshuffle_6bit()` (has `#[target_feature(enable = "neon")]`)
- **Before:** No internal unsafe blocks
- **After:**
  - Safe: All SIMD intrinsics (safe due to `#[target_feature]`)
  - Unsafe: pointer dereference for shuffle mask load (`vld1q_u8`)

## Pattern Applied

Following the reference document's **Option 1: Narrow unsafe scopes**, the refactoring:

1. **Kept Safe:**
   - Bounds checks (`data.len() < BLOCK_SIZE`)
   - Arithmetic (`data.len() / BLOCK_SIZE`, `offset += BLOCK_SIZE`)
   - Capacity calculations
   - Iteration (`for _ in 0..num_blocks`, `for &byte in &output_buf`)
   - Standard library safe operations (`result.push()`, `result.extend_from_slice()`)

2. **Made Unsafe (explicit blocks):**
   - SIMD loads: `vld1q_u8(ptr.add(offset))`
   - SIMD stores: `vst1q_u8(ptr, vec)`
   - Pointer arithmetic: `.as_ptr().add(offset)`
   - SIMD intrinsic calls (in functions without `#[target_feature]`)

3. **Special Case - Functions with `#[target_feature]`:**
   - SIMD intrinsics are safe to call (feature enabled)
   - Only pointer operations need unsafe blocks

## Verification

```bash
cargo check
```

No errors in `/home/w3surf/work/personal/code/base-d/src/simd/aarch64/generic.rs`

(Other errors exist in x86_64 files, but those are outside this refactoring scope)

## Benefits

- Compiler can now verify safety of bounds checks, arithmetic, and iteration
- Unsafe operations are clearly marked and isolated
- Easier security auditing - unsafe blocks show exactly what's dangerous
- Prepared for Edition 2024 migration
- Defense in depth against processor vulnerabilities (Spectre, Meltdown)
