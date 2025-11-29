# Authentication & Encryption Review: base-d

**Project:** `/home/w3surf/work/personal/code/base-d`
**Type:** CLI encoding/decoding tool
**Reviewed:** 2025-11-28
**Reviewer:** Keymaker

---

## Summary

**Finding:** Minimal auth/encryption concerns. This is a pure encoding tool.

base-d is a multi-dictionary encoding library and CLI. It converts binary data to text representations using various character sets (base64, emoji, hieroglyphics, etc.). No authentication, authorization, or encryption mechanisms present.

---

## Key Areas Analyzed

### 1. Authentication Patterns
**Status:** None found

- No user authentication
- No API key handling
- No OAuth/JWT flows
- No bearer tokens
- No session management

### 2. Encryption/Cryptography
**Status:** Hashing only (non-encryption)

**Hash implementations found:**
- **Location:** `/home/w3surf/work/personal/code/base-d/src/features/hashing.rs`
- **Purpose:** Data integrity verification (checksums/digests)
- **Algorithms:** 24 hash functions across 4 categories:
  - Cryptographic: MD5, SHA2 family (224/256/384/512), SHA3 family, Keccak, BLAKE2b/s, BLAKE3
  - CRC checksums: CRC16, CRC32, CRC32c, CRC64
  - Fast hashing: xxHash32, xxHash64, xxHash3-64, xxHash3-128
- **Dependencies:** Pure Rust (sha2, sha3, blake2, blake3, md-5, twox-hash, crc)
- **Note:** No OpenSSL dependency - fully Rust-native

**Important distinction:** Hashing is one-way data integrity verification, not encryption.

### 3. Secret/Key Handling
**Status:** Optional XXH3 secrets (specialized use case)

**XXH3 Secret Feature:**
- **Location:** `/home/w3surf/work/personal/code/base-d/src/features/hashing.rs:16-39`
- **Purpose:** Customizable secret for xxHash3 variants (advanced hashing feature)
- **Implementation:**
  ```rust
  pub struct XxHashConfig {
      pub seed: u64,
      pub secret: Option<Vec<u8>>,  // Must be >= 136 bytes
  }
  ```
- **Sources:**
  - `--hash-secret-stdin` CLI flag (reads from stdin)
  - Config file path: `config.settings.xxhash.default_secret_file`
  - Path expansion uses `shellexpand::tilde()` for `~` handling
- **Validation:** Enforces 136-byte minimum for XXH3 secrets
- **Usage:** Only applies to xxHash3-64 and xxHash3-128 algorithms
- **Security posture:** Not cryptographic - used for hash customization, not access control

**Access pattern:**
```rust
// From cli/config.rs:84-92
let secret = if cli_hash_secret_stdin {
    let mut buf = Vec::new();
    io::stdin().read_to_end(&mut buf)?;
    Some(buf)
} else if let Some(ref path) = config.settings.xxhash.default_secret_file {
    Some(fs::read(shellexpand::tilde(path).as_ref())?)
} else {
    None
};
```

### 4. Compression Features
**Status:** No encryption layer

- Compression algorithms: gzip, zstd, brotli, lz4, snappy, lzma
- Purpose: Size reduction before encoding
- Not encrypted - compression is separate from confidentiality

### 5. Configuration Files
**Status:** No credentials stored

**Config hierarchy:**
1. Built-in dictionaries (bundled)
2. `~/.config/base-d/dictionaries.toml` (user overrides)
3. `./dictionaries.toml` (project-local)

**Contents:** Character dictionaries, encoding modes, compression defaults
**No sensitive data:** No passwords, tokens, or API keys

### 6. Input/Output Handling
**Status:** Standard streams only

- **Stdin/stdout:** Standard Unix pipe pattern
- **Files:** Direct filesystem access (no network)
- **Streaming:** 4KB chunked processing for memory efficiency
- **No remote access:** Purely local tool

### 7. Dependencies Review
**Notable security-relevant deps:**
- `sha2`, `sha3`, `blake2`, `blake3` - Cryptographic hash libraries
- `md-5` - Legacy hash (MD5 is broken for crypto, but acceptable for checksums)
- `twox-hash` - Fast non-cryptographic hashing
- `crc` - Checksum library
- `shellexpand` - Expands `~` in paths (potential concern if user-controlled paths)

**No auth/crypto networking:**
- No `reqwest`, `hyper`, `rustls`, `openssl`
- No `oauth2`, `jsonwebtoken`, `ring`

---

## Observations

### What This Tool Does
- Encodes binary → text (many dictionaries: base64, emoji, hieroglyphics, etc.)
- Decodes text → binary
- Optionally compresses before encoding
- Optionally hashes during processing
- Auto-detects encoding format

### What This Tool Does NOT Do
- User authentication or authorization
- Data encryption/decryption (AES, RSA, etc.)
- Network communication
- API key management
- Secure credential storage

### XXH3 Secret Context
The "secret" handling is specific to xxHash3, a fast non-cryptographic hash function. The secret allows customization of the hash function for domain-specific applications (e.g., preventing hash flooding attacks in hash tables). This is NOT:
- An encryption key
- An authentication token
- A password

**Risk assessment:** Low. The secret is optional, non-cryptographic, and only affects hash output determinism.

---

## Potential Concerns

### 1. Path Expansion (Low Risk)
**Location:** `/home/w3surf/work/personal/code/base-d/src/cli/config.rs:89`
```rust
Some(fs::read(shellexpand::tilde(path).as_ref())?)
```

**Issue:** If `default_secret_file` path comes from untrusted config, could read arbitrary files

**Mitigation:**
- Config files are user-controlled (`~/.config/base-d/dictionaries.toml`)
- User is already in control of their own config
- No remote/untrusted config loading

**Verdict:** Acceptable for CLI tool with local configs

### 2. Stdin Secret Reading (Low Risk)
**Pattern:** `--hash-secret-stdin` reads entire stdin into memory

**Considerations:**
- No size limit validation before read
- Could be abused to exhaust memory if stdin is huge
- However, this is an explicit user action for XXH3 hashing

**Verdict:** Standard Unix pattern, user-controlled

### 3. MD5 Usage (Informational)
MD5 is cryptographically broken but still useful for:
- File integrity verification (non-adversarial)
- Legacy compatibility

**Verdict:** Acceptable for encoding tool use cases

---

## Recommendations

### Current State: Secure for Purpose
No authentication or encryption changes needed. This is a data transformation tool, not a security tool.

### If Future Auth/Encryption Features Are Added:

**For encryption:**
- Use established crates: `aes-gcm`, `chacha20poly1305`, `age`
- Avoid rolling custom crypto
- Consider `rage` (Rust implementation of `age`) for file encryption

**For secrets:**
- Never log secrets
- Clear sensitive memory (`zeroize` crate)
- Avoid config file storage of secrets
- Prefer environment variables or OS keychains

**For auth (if network features added):**
- Use `oauth2` or `jsonwebtoken` crates
- Store tokens in OS credential store (`keyring` crate)
- Never commit tokens to config files

---

## Conclusion

**base-d is not an authentication or encryption tool.** It's a pure encoding/transformation utility. The only "secret" handling is for xxHash3 customization, which is non-cryptographic.

**Security posture:** Appropriate for a local CLI tool. No auth/encryption concerns for current scope.

**Action required:** None. Continue as designed.

---

Knock knock, Neo.
