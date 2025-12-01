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
#[target_feature(enable = "ssse3")]
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

    // Safe in #[target_feature] function - just vector initialization
    let base_offset_vec = _mm_set1_epi8(self.gap_info.base_offset as i8);

    for _ in 0..num_blocks {
        // Unsafe: unchecked indexing (pointer-like operation)
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

        // Unsafe: SIMD load (pointer dereference)
        let idx_vec = unsafe { _mm_loadu_si128(indices.as_ptr() as *const __m128i) };

        // Safe: vector arithmetic
        let char_vec = _mm_add_epi8(base_offset_vec, idx_vec);

        // Unsafe: SIMD store (pointer dereference)
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

## `#[target_feature]` Functions: Only Pointer Ops Need Unsafe

**Key discovery (2024-12-01):** In functions with `#[target_feature(enable = "...")]`, most SIMD intrinsics are **safe to call** without explicit `unsafe {}` blocks. Only **pointer operations** need unsafe.

### What needs unsafe:
- `_mm_loadu_si128` / `_mm_storeu_si128` (x86_64 load/store)
- `vld1q_u8` / `vst1q_u8` (NEON load/store)
- Any intrinsic that dereferences a raw pointer

### What does NOT need unsafe:
- `_mm_set1_epi8`, `_mm_add_epi8`, `_mm_sub_epi8`, `_mm_cmpgt_epi8`, `_mm_and_si128`, `_mm_movemask_epi8`
- `vdupq_n_u8`, `vaddq_u8`, `vsubq_u8`, `vcgeq_u8`, `vcgtq_u8`, `vandq_u8`
- All arithmetic, comparison, and initialization intrinsics

### Why?

The `#[target_feature]` attribute guarantees the CPU supports the instruction set. The intrinsics themselves aren't unsafe - they're just SIMD math. What's unsafe is dereferencing pointers, which load/store intrinsics do.

### Correct pattern:

```rust
#[target_feature(enable = "neon")]
unsafe fn decode_neon_5bit(&self, encoded: &str) -> Option<Vec<u8>> {
    use std::arch::aarch64::*;

    // NO unsafe needed - these are just vector initialization
    let base_offset_vec = vdupq_n_u8(self.gap_info.base_offset);
    let thresh1 = vdupq_n_u8(threshold1);

    for block in 0..num_blocks {
        // UNSAFE needed - pointer dereference
        let char_vec = unsafe { vld1q_u8(chars.as_ptr()) };

        // NO unsafe needed - vector arithmetic
        let mut idx_vec = vsubq_u8(char_vec, base_offset_vec);
        let mask1 = vcgeq_u8(char_vec, thresh1);
        idx_vec = vsubq_u8(idx_vec, vandq_u8(mask1, vdupq_n_u8(1)));

        // UNSAFE needed - pointer dereference
        unsafe { vst1q_u8(indices.as_mut_ptr(), idx_vec) };
    }

    Some(result)
}
```

### Anti-pattern: Wrapping every intrinsic

```rust
// WRONG - 60+ unnecessary unsafe blocks
let base_offset_vec = unsafe { vdupq_n_u8(self.gap_info.base_offset) };  // unnecessary
let idx_vec = unsafe { vsubq_u8(char_vec, base_offset_vec) };  // unnecessary
```

Clippy will warn about these as "unnecessary unsafe blocks".

## Lesson Learned (2024-12-01)

When you see "unnecessary unsafe block" warnings in `#[target_feature]` code:

1. **The warning is probably correct** - most SIMD intrinsics don't need unsafe
2. **Only pointer ops need unsafe** - load/store intrinsics that dereference pointers
3. **Remove the unnecessary blocks** - keep unsafe only around pointer operations
4. **Test on the target platform** - x86_64 clippy can't catch aarch64 issues

## References

- [Rust Edition Guide: unsafe_op_in_unsafe_fn](https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-op-in-unsafe-fn.html)
- [RFC 2585](https://rust-lang.github.io/rfcs/2585-unsafe-block-in-unsafe-fn.html)

## Related Lints

- `clippy::undocumented_unsafe_blocks` - requires `// SAFETY:` comments
- `unsafe_code` - warns on any unsafe usage
