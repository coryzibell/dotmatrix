# Lint: unsafe_op_in_unsafe_fn

**Ecosystem:** Rust
**Category:** Edition 2024 migration
**Severity:** Error (in Edition 2024)

## What It Catches

In Rust Edition 2024, the body of an `unsafe fn` is no longer implicitly unsafe. Calling unsafe functions or performing unsafe operations inside an `unsafe fn` now requires explicit `unsafe {}` blocks.

```rust
// Edition 2021 - compiles fine
unsafe fn example() {
    std::ptr::read(ptr);  // OK, whole body is unsafe
}

// Edition 2024 - error!
unsafe fn example() {
    std::ptr::read(ptr);  // ERROR: call to unsafe function requires unsafe block
}
```

## Why This Changed

The implicit unsafety of `unsafe fn` bodies was considered a footgun. It made it too easy to accidentally perform unsafe operations without explicit acknowledgment. Edition 2024 requires you to be explicit about which operations are unsafe.

## How to Fix

### Option 1: Narrow unsafe scopes (RECOMMENDED)

The RFC's intent is to **minimize the scope of unsafety** so the compiler can verify safe code is actually safe. This matters for security - with modern processor attack vectors (Spectre, Meltdown, etc.), letting the compiler reason about memory safety in as much code as possible is valuable.

```rust
unsafe fn encode_ssse3_5bit(&self, data: &[u8], result: &mut String) {
    use std::arch::x86_64::*;

    // Safe: bounds check, arithmetic
    const BLOCK_SIZE: usize = 5;
    if data.len() < BLOCK_SIZE {
        self.encode_scalar(data, result);
        return;
    }

    let num_blocks = data.len() / BLOCK_SIZE;
    let mut offset = 0;

    // Unsafe: SIMD intrinsic calls
    let base_offset_vec = unsafe { _mm_set1_epi8(self.gap_info.base_offset as i8) };

    for _ in 0..num_blocks {
        // Unsafe: unchecked indexing
        let (b0, b1, b2, b3, b4) = unsafe {(
            *data.get_unchecked(offset),
            *data.get_unchecked(offset + 1),
            *data.get_unchecked(offset + 2),
            *data.get_unchecked(offset + 3),
            *data.get_unchecked(offset + 4),
        )};

        // Safe: bit manipulation
        let mut indices = [0u8; 16];
        indices[0] = (b0 >> 3) & 0x1F;
        indices[1] = ((b0 << 2) | (b1 >> 6)) & 0x1F;
        // ...

        // Unsafe: SIMD load/store
        let char_vec = unsafe {
            let idx_vec = _mm_loadu_si128(indices.as_ptr() as *const __m128i);
            _mm_add_epi8(base_offset_vec, idx_vec)
        };

        // Safe: iteration, push
        let mut output = [0u8; 16];
        unsafe { _mm_storeu_si128(output.as_mut_ptr() as *mut __m128i, char_vec) };

        for &ch in &output[..8] {
            result.push(ch as char);  // safe
        }

        offset += BLOCK_SIZE;  // safe
    }
}
```

**Benefits:**
- Compiler verifies safe operations (bounds checks, arithmetic, iteration)
- Bugs in safe code get caught at compile time
- Easier to audit: unsafe blocks mark exactly what's dangerous
- Defense in depth against processor vulnerabilities

### Option 2: Wrap entire body (quick migration)

For initial Edition 2024 migration, wrapping the whole body works but should be refactored later:

```rust
unsafe fn encode_neon_impl(&self, data: &[u8], result: &mut String) {
    unsafe {
        let lut_vec = vld1q_u8(self.encode_lut.as_ptr());
        // ... rest of unsafe operations
    }
}
```

**Use this for:** Quick migration, will refactor later.
**Don't use for:** Long-term code. Refactor to Option 1.

### Option 3: Suppress (NOT recommended)

```rust
#[allow(unsafe_op_in_unsafe_fn)]
unsafe fn legacy_code() {
    // ...
}
```

Only use this for gradual migration, not as a permanent solution. This opts out of the safety benefits entirely.

## Common Patterns Affected

### SIMD Intrinsics

All architecture-specific SIMD intrinsics (`vld1q_u8`, `_mm_loadu_si128`, etc.) are unsafe:

```rust
// x86_64
unsafe fn simd_x86() {
    unsafe {
        let vec = _mm_loadu_si128(ptr);
        _mm_storeu_si128(out_ptr, vec);
    }
}

// aarch64 (NEON)
unsafe fn simd_neon() {
    unsafe {
        let vec = vld1q_u8(ptr);
        vst1q_u8(out_ptr, vec);
    }
}
```

### Pointer Operations

```rust
unsafe fn ptr_ops(ptr: *const u8, offset: usize) {
    unsafe {
        let new_ptr = ptr.add(offset);
        let value = *new_ptr;
    }
}
```

### Unchecked Indexing

```rust
unsafe fn unchecked(slice: &[u8], idx: usize) -> u8 {
    unsafe { *slice.get_unchecked(idx) }
}
```

## cargo fix Limitations

`cargo fix --edition` will attempt to fix this, but it only runs on the current target architecture. If you have `#[cfg(target_arch = "...")]` gated code:

- Code for your current arch gets fixed
- Code for other archs (e.g., aarch64 on x86_64 machine) does NOT get fixed
- CI on other platforms will fail

**Solution:** After running `cargo fix --edition`, manually check all architecture-gated SIMD code.

## Cross-Platform Checklist

When migrating SIMD code to Edition 2024:

1. Run `cargo fix --edition` on your dev machine
2. Search for `#[cfg(target_arch = ` to find platform-specific code
3. Manually verify all `unsafe fn` in those modules have proper `unsafe {}` blocks
4. If possible, cross-compile check: `cargo check --target aarch64-apple-darwin`

## Files Affected in base-d

- `src/simd/aarch64/specialized/base16.rs` - NEON encode/decode
- `src/simd/aarch64/specialized/base32.rs` - NEON encode/decode
- `src/simd/aarch64/specialized/base64.rs` - NEON encode/decode
- `src/simd/aarch64/specialized/base256.rs` - NEON encode/decode
- `src/simd/aarch64/generic.rs` - Generic NEON reshuffling

## The Double-Block Anti-Pattern

**Problem:** You have an `unsafe fn` with a single large `unsafe {}` block wrapping the entire body.

```rust
// ANTI-PATTERN: Double unsafe nesting
unsafe fn decode_nibble_chars_neon(chars: uint8x16_t) -> uint8x16_t {
    use std::arch::aarch64::*;

    unsafe {  // <-- This wrapper is redundant AND creates lint confusion
        let zero = vdupq_n_u8(0x30);
        // ... 30 lines of SIMD code ...
    }
}
```

**Why it's confusing:**
- On x86_64: This code isn't compiled (it's `#[cfg(target_arch = "aarch64")]`)
- On aarch64 with Rust 2024: Clippy warns "unnecessary unsafe block" because `unsafe fn` body is *supposed to* require `unsafe {}` around each intrinsic, but ONE big block looks redundant
- The warning is technically wrong - the big block IS necessary for the intrinsics - but the pattern is still bad

**The fix:** Replace the single large block with per-intrinsic `unsafe {}` blocks:

```rust
// CORRECT: Per-intrinsic unsafe blocks
unsafe fn decode_nibble_chars_neon(chars: uint8x16_t) -> uint8x16_t {
    use std::arch::aarch64::*;

    let zero = unsafe { vdupq_n_u8(0x30) };
    let nine = unsafe { vdupq_n_u8(0x39) };
    let is_digit = unsafe { vandq_u8(vcgeq_u8(chars, zero), vcleq_u8(chars, nine)) };
    // ... each intrinsic wrapped individually ...
}
```

This satisfies Rust 2024's `unsafe_op_in_unsafe_fn` while avoiding the "unnecessary unsafe block" warning.

## Lesson Learned (2024-11-30)

When you see "unnecessary unsafe block" warnings on platform-specific code:

1. **Don't blindly remove the unsafe blocks** - the intrinsics inside still need them
2. **Check if it's a "double wrapping" issue** - one big block vs per-intrinsic blocks
3. **The fix is restructuring**, not removal
4. **Test on the target platform** - x86_64 clippy can't catch aarch64 issues

## References

- [Rust Edition Guide: unsafe_op_in_unsafe_fn](https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-op-in-unsafe-fn.html)
- [RFC 2585](https://rust-lang.github.io/rfcs/2585-unsafe-block-in-unsafe-fn.html)

## Related Lints

- `clippy::undocumented_unsafe_blocks` - requires `// SAFETY:` comments
- `unsafe_code` - warns on any unsafe usage
