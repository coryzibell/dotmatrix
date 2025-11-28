# Add SHA-3 support to base-d

## Context
base-d currently supports: md5, sha256, sha512, blake3, xxh64, xxh3

Missing SHA-3 family (Keccak) for completeness and compliance contexts.

## SHA-3 variants to add
- `sha3-256` - 256-bit, sponge construction
- `sha3-512` - 512-bit
- `shake128` - extendable output (XOF)
- `shake256` - extendable output (XOF)

## Why
- NIST standardized (FIPS 202)
- Required for some compliance contexts
- Completeness - we support the SHA-2 family, should support SHA-3
- Different construction than SHA-2 (hedge against future SHA-2 breaks)

## Rust crate
`sha3` from RustCrypto - same ecosystem as our other hash implementations.

```toml
sha3 = "0.10"
```

## Priority
Low - BLAKE3 covers most use cases. Add when someone needs it or for completeness pass.
