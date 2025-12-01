# Crate Recommendations for Ascon and KangarooTwelve

**Date:** 2025-12-01
**Mission:** Identify suitable Rust crates for adding to base-d

---

## Ascon-Hash

### Recommended Crate: `ascon-hash`

**Crates.io:** https://crates.io/crates/ascon-hash
**Docs:** https://docs.rs/ascon-hash
**Version:** 0.3.1 (published ~4 months ago)
**License:** Apache-2.0 OR MIT (matches base-d)
**MSRV:** Rust 1.85.0

**Variants Provided:**
- AsconHash256 (fixed 256-bit output)
- AsconXof128 (extensible output function)

**Status:**
- Part of RustCrypto project
- Pure Rust implementation
- no_std capable
- 42,834 total downloads
- **WARNING:** No security audits performed

**API Style:**
Follows RustCrypto digest trait pattern - compatible with existing hash implementations in base-d (sha2, sha3, blake2, etc.)

**Recommendation:**
Use `ascon-hash` v0.3.1. Start with AsconHash256 (fixed output) for simplicity. Can add AsconXof128 later if XOF functionality is desired.

---

## KangarooTwelve (K12)

### Option 1: `k12` (Pure Rust) - RECOMMENDED

**Crates.io:** https://crates.io/crates/k12
**Docs:** https://docs.rs/k12
**Version:** 0.2.1
**MSRV:** Rust 1.56+
**License:** Likely Apache/MIT (check docs)

**Pros:**
- Pure Rust (matches base-d philosophy)
- Experimental but functional
- XOF (extensible output function)
- Clean API

**Cons:**
- Marked as "experimental"
- No SIMD optimizations

### Option 2: `kangarootwelve`

**Crates.io:** https://crates.io/crates/kangarootwelve

**Pros:**
- Implements full K12 specification
- Arbitrary output length support

**Cons:**
- Non-incremental absorption API (may not fit streaming pattern)
- Unknown performance vs k12 crate

### Option 3: `kangarootwelve_xkcp` (Wrapper)

**NOT RECOMMENDED** for base-d

**Pros:**
- SSSE3, AVX2, AVX-512 optimizations
- Runtime CPU detection
- Official XKCP implementation

**Cons:**
- Requires C compiler (adds build complexity)
- Wrapper around C code (not pure Rust)

---

## Final Recommendations

### For Implementation:

**Ascon:**
```toml
ascon-hash = "0.3"
```
- Use `AsconHash256` variant
- Fixed 32-byte output
- RustCrypto compatible API

**KangarooTwelve:**
```toml
k12 = "0.2"
```
- Pure Rust, simple
- XOF with configurable output length
- Default to 32-byte output for consistency

### Hash Names for CLI

**Ascon:**
- Primary: `ascon`, `ascon-hash`, `ascon256`
- Output: 32 bytes (256 bits)

**KangarooTwelve:**
- Primary: `k12`, `kangarootwelve`, `kangaroo12`
- Output: 32 bytes (default, configurable XOF)

---

## Implementation Priority

1. **Ascon** - Simpler, fixed output, RustCrypto pattern
2. **K12** - XOF adds slight complexity but manageable

Both should be straightforward to integrate following existing patterns.

---

## Sources

- [ascon-hash on crates.io](https://crates.io/crates/ascon-hash)
- [k12 on crates.io](https://crates.io/crates/k12)
- [kangarootwelve on crates.io](https://crates.io/crates/kangarootwelve)
- [KangarooTwelve on lib.rs](https://lib.rs/crates/kangarootwelve)
