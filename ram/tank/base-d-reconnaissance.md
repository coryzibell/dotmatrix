# Base-D Repository Research
Tank - Reconnaissance Report
Date: 2025-12-01

## 1. dictionaries.toml Contents

**Location:** `/home/w3surf/work/personal/code/base-d/dictionaries.toml`

Comprehensive dictionary configuration file with:

### Structure
- `[settings]` section for default config (none currently set)
- Compression algorithm defaults (gzip, zstd, brotli, lz4, snappy, lzma)
- 60+ dictionary entries

### Dictionary Categories

**Fundamental** (base2, base4, base8):
- Binary, quaternary, octal

**RFC 4648 Standards** (chunked mode):
- base64, base64url, base32, base32hex, base16, hex, bioctal
- base64_imap (RFC 3501 - IMAP variant)

**Cryptocurrency** (base conversion mode):
- base58, base58flickr, base58ripple (Bitcoin/blockchain)

**Other Encodings**:
- base36, base62, base91, base85, ascii85, z85
- base32_crockford, base32_zbase, base32_geohash
- base45 (QR codes, COVID certificates)

**Legacy**:
- uuencode, xxencode, binhex

**Unicode/Esoteric**:
- 100 characters (emoji range U+1F3F7)
- cards, dna, binary
- Egyptian hieroglyphs, cuneiform, domino, mahjong
- chess, alchemy symbols, zodiac
- emoji_faces, emoji_animals, runic, arrows, weather, music
- base1024 (CJK ideographs + Hangul + Yi)
- base256_matrix (Matrix-style: Katakana + Greek + Math symbols + Box drawing)

**Unicode Blocks**:
- blocks_full, volume (8-char bar), barcode, blocks, gradient, boxdraw

---

## 2. Hash Algorithms: Hardcoded vs Config

**FINDING: Completely Hardcoded**

### src/cli/commands.rs (line 86)
```rust
pub const HASH_ALGORITHMS: &[&str] = &["md5", "sha256", "sha512", "blake3", "ascon", "k12", "xxh64", "xxh3"];
```
- Defined as constant
- Not loaded from config
- Used by `select_random_hash()` function (line 93-103)

### src/cli/handlers/config.rs (line 8)
```rust
const HASH_ALGORITHMS: &[&str] = &["md5", "sha256", "sha512", "blake3", "ascon", "k12", "xxh64", "xxh3"];
```
- Duplicate constant definition
- Same 8 algorithms
- Used for listing/config output (line 31)

### dictionaries.toml
- Has compression algorithm defaults
- NO hash algorithm configuration
- NO way to add/modify hash algorithms via config

---

## 3. HASH_ALGORITHMS Usage Patterns

### In src/cli/commands.rs:
1. **select_random_hash()** (lines 93-103)
   - Uses `HASH_ALGORITHMS.choose()` from rand crate
   - Selects random hash for `--dejavu` mode
   - Prints selection to stderr unless `quiet=true`

2. **select_random_compress()** (lines 106-116)
   - Similar pattern but for `COMPRESS_ALGORITHMS`

3. **matrix_mode()** (lines 118-383)
   - Does NOT use HASH_ALGORITHMS directly
   - Focuses on dictionary switching
   - Handles keyboard controls (arrows, space, esc)

### In src/cli/handlers/config.rs:
1. **handle_list()** (lines 24-78)
   - Lists algorithms under ConfigCategory::Hashes
   - Outputs as comma-separated or JSON
   - Line 31: `let hash_list = HASH_ALGORITHMS.to_vec();`

2. **handle_show()** (lines 80-129)
   - Shows individual dictionary details
   - Does NOT interact with hash algorithms

### Other Functions Using Hash:
- `streaming_encode()` - takes `hash: Option<String>` parameter
- `streaming_decode()` - takes `hash: Option<String>` parameter
- Both convert hash string via `HashAlgorithm::from_str()`

---

## Summary

| Question | Answer | Details |
|----------|--------|---------|
| **dictionaries.toml contents?** | Large TOML config file | 60+ dictionaries, compression defaults, 3 encoding modes (base_conversion, chunked, byte_range, radix) |
| **Hash algorithms loaded from config?** | **NO** | Hardcoded constant in two files, not in dictionaries.toml |
| **HASH_ALGORITHMS usage?** | Random selection & listing | Used in `select_random_hash()` and `config list --json` output |

### Key Insight
The hash algorithms are **purely hardcoded**, while dictionary configurations are **fully externalized to TOML**. This creates an asymmetry: users can add custom dictionaries but cannot extend hash algorithm options without recompiling.
