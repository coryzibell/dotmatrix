# base-d Hash Architecture - Research Intel

**Repository:** /home/w3surf/work/personal/code/base-d
**Mission:** Understanding hash implementation architecture for adding Ascon and KangarooTwelve
**Date:** 2025-12-01

---

## File Structure

```
src/
├── features/
│   ├── mod.rs                 # Re-exports all feature modules
│   ├── hashing.rs            # MAIN: HashAlgorithm enum & implementations
│   ├── compression.rs
│   └── detection.rs
├── encoders/
│   └── streaming/
│       └── hasher.rs         # HasherWriter enum for streaming support
├── cli/
│   ├── args.rs               # CLI argument definitions
│   └── handlers/
│       └── hash.rs           # CLI hash command handler
└── lib.rs                    # Public API exports
```

---

## Key Components

### 1. HashAlgorithm Enum (`src/features/hashing.rs`)

**Location:** Lines 43-71
**Purpose:** Central registry of all supported hash algorithms

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HashAlgorithm {
    // Cryptographic hashes
    Md5, Sha224, Sha256, Sha384, Sha512,
    Sha3_224, Sha3_256, Sha3_384, Sha3_512,
    Keccak224, Keccak256, Keccak384, Keccak512,
    Blake2b, Blake2s, Blake3,
    // CRC variants
    Crc32, Crc32c, Crc16, Crc64,
    // xxHash variants
    XxHash32, XxHash64, XxHash3_64, XxHash3_128,
}
```

**Key Methods:**
- `all()` - Returns Vec of all algorithms (used for config list)
- `random()` - Selects random algorithm
- `from_str()` - Parses CLI input (handles variations like "sha-256", "sha256")
- `as_str()` - Canonical string representation
- `output_size()` - Returns hash output size in bytes

### 2. Hash Computation (`src/features/hashing.rs`)

**Primary Functions:**
- `hash(data: &[u8], algorithm: HashAlgorithm) -> Vec<u8>` (line 205)
- `hash_with_config(data: &[u8], algorithm: HashAlgorithm, config: &XxHashConfig) -> Vec<u8>` (line 210)

**Pattern:** Match on algorithm, instantiate hasher, update, finalize, return Vec<u8>

```rust
HashAlgorithm::Sha256 => {
    let mut hasher = Sha256::new();
    hasher.update(data);
    hasher.finalize().to_vec()
}
```

### 3. Streaming Support (`src/encoders/streaming/hasher.rs`)

**HasherWriter Enum:** Wraps hasher instances for streaming operations

```rust
pub(super) enum HasherWriter {
    Sha256(sha2::Sha256),
    Blake3(blake3::Hasher),
    // ... one variant per algorithm
}
```

**Methods:**
- `update(&mut self, data: &[u8])` - Stream data in chunks
- `finalize(self) -> Vec<u8>` - Complete hash and return output
- `create_hasher_writer(algo: HashAlgorithm, config: &XxHashConfig)` - Factory function

### 4. CLI Integration (`src/cli/handlers/hash.rs`)

**Handler Flow:**
1. Parse algorithm string → `HashAlgorithm::from_str()`
2. Read input (file or stdin)
3. Load config (xxHash seeds/secrets)
4. Compute hash → `hash_with_config()`
5. Output (hex, raw, or encode with dictionary)

**CLI Args** (`src/cli/args.rs`, lines 92-111):
```rust
pub struct HashArgs {
    pub algorithm: String,       // Required: hash algorithm name
    pub file: Option<PathBuf>,  // Input file (stdin if None)
    pub seed: Option<u64>,      // xxHash seed
    pub encode: Option<String>, // Encode output with dictionary
    pub secret_stdin: bool,     // Read XXH3 secret from stdin
}
```

### 5. Public API Exports (`src/lib.rs`)

```rust
pub use features::{
    HashAlgorithm, XxHashConfig,
    hash, hash_with_config,
    // ... other features
};
```

---

## Current Dependencies (Cargo.toml)

```toml
sha2 = "0.10.9"
sha3 = "0.10.8"
blake2 = "0.10.6"
blake3 = "1.8.2"
md-5 = "0.10.6"
twox-hash = { version = "2.1.2", features = ["std", "xxhash32", "xxhash64", "xxhash3_64", "xxhash3_128"] }
crc = "3.3.0"
hex = "0.4.3"
```

---

## Adding New Algorithms: Step-by-Step

### Required Changes:

#### 1. Add Dependencies (Cargo.toml)
```toml
ascon-hash = "0.4"           # Example - check crates.io for actual version
kangarootwelve = "0.3"       # Example - check crates.io for actual version
```

#### 2. Update HashAlgorithm Enum (`src/features/hashing.rs`)

**Add variants:**
```rust
pub enum HashAlgorithm {
    // ... existing variants ...
    Ascon128,      // Or AsconHash if single variant
    AsconA,        // If multiple variants exist
    K12,           // KangarooTwelve
}
```

**Update methods:**
- Add to `all()` vector (line 76)
- Add to `from_str()` match (line 114) - support multiple spellings
- Add to `as_str()` match (line 144)
- Add to `output_size()` match (line 174)

**Add to `hash_with_config()` match:**
```rust
HashAlgorithm::Ascon128 => {
    // Import at top: use ascon_hash::AsconHash;
    let mut hasher = AsconHash::new();
    hasher.update(data);
    hasher.finalize().to_vec()
}
```

#### 3. Add Streaming Support (`src/encoders/streaming/hasher.rs`)

**Add HasherWriter variants:**
```rust
pub(super) enum HasherWriter {
    // ... existing variants ...
    Ascon128(ascon_hash::AsconHash),  // Example
    K12(kangarootwelve::KangarooTwelve),
}
```

**Update methods:**
- Add to `update()` match (line 33)
- Add to `finalize()` match (line 113)
- Add to `create_hasher_writer()` match (line 151)

#### 4. Add Tests (`src/features/hashing.rs`)

Add test functions following existing pattern:
```rust
#[test]
fn test_ascon128() {
    let data = b"hello world";
    let hash = hash(data, HashAlgorithm::Ascon128);
    assert_eq!(hash.len(), 32);  // Check expected output size
}
```

---

## Configuration System

**XxHashConfig** is algorithm-specific config (currently only xxHash uses it).

For new algorithms needing config:
1. Add config struct (like `XxHashConfig` at line 12-40)
2. Update `hash_with_config()` to accept config
3. Update CLI handlers to load config

**Current approach:** Single config for all algorithms, ignored by non-xxHash algorithms. Simple and extensible.

---

## Testing Strategy

Existing tests verify:
- Correct output size
- Deterministic output (same input → same output)
- Known test vectors (e.g., MD5 of "hello world")

New algorithms should include:
- Output size validation
- Known test vector if available
- Empty input test
- Large input test (if relevant)

---

## Notes

- **No trait abstraction:** Each algorithm is a direct match arm - simple and explicit
- **Streaming support is optional:** Only needed if CLI streaming mode is used
- **Config is per-algorithm:** xxHash has seeds/secrets, others may need different config
- **Output is always Vec<u8>:** Caller handles encoding (hex, base64, etc.)
- **Algorithm strings are case-insensitive:** "sha256", "SHA-256", "sha-256" all work

---

## Recommended Approach for Ascon + KangarooTwelve

1. **Research crates:** Check crates.io for `ascon` and `kangarootwelve` implementations
2. **Add dependencies:** Choose well-maintained crates with RustCrypto-style APIs
3. **Add enum variants:** Follow naming conventions (prefer short names like `K12`)
4. **Implement hash_with_config:** Match on new variants, follow existing pattern
5. **Add streaming support:** Implement HasherWriter variants
6. **Add string parsing:** Support multiple name variations in `from_str()`
7. **Add tests:** Verify output sizes and deterministic behavior
8. **Update CLI:** Will automatically work once enum is updated

**Order of operations:**
1. Cargo.toml dependencies
2. HashAlgorithm enum (all methods)
3. hash_with_config() implementation
4. HasherWriter enum + methods
5. Tests
6. Manual CLI testing

---

## Ready for Implementation

All patterns are clear and consistent. The architecture is straightforward - no complex abstractions, just enums and match statements. Adding new algorithms is mechanical.

**Handoff to Smith recommended** - Implementation is straightforward pattern-following.
