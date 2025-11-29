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

### Option 1: Wrap entire body in unsafe block (recommended for SIMD code)

When the entire function body consists of unsafe operations (common in SIMD):

```rust
unsafe fn encode_neon_impl(&self, data: &[u8], result: &mut String) {
    unsafe {
        let lut_vec = vld1q_u8(self.encode_lut.as_ptr());
        // ... rest of unsafe operations
    }
}
```

### Option 2: Wrap individual operations

When only some operations are unsafe:

```rust
unsafe fn mixed_operations(&self, data: &[u8]) -> Vec<u8> {
    let len = data.len();  // safe
    let ptr = unsafe { data.as_ptr().add(offset) };  // unsafe
    // ...
}
```

### Option 3: Suppress (not recommended)

```rust
#[allow(unsafe_op_in_unsafe_fn)]
unsafe fn legacy_code() {
    // ...
}
```

Only use this for gradual migration, not as a permanent solution.

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

- `src/simd/lut/base16.rs` - NEON encode/decode
- `src/simd/lut/base32.rs` - NEON encode/decode
- `src/simd/lut/base64.rs` - NEON encode/decode

## References

- [Rust Edition Guide: unsafe_op_in_unsafe_fn](https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-op-in-unsafe-fn.html)
- [RFC 2585](https://rust-lang.github.io/rfcs/2585-unsafe-block-in-unsafe-fn.html)

## Related Lints

- `clippy::undocumented_unsafe_blocks` - requires `// SAFETY:` comments
- `unsafe_code` - warns on any unsafe usage
