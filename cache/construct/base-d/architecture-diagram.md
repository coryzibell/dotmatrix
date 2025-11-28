# base-d Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         base-d CLI Tool                          │
│     Universal Multi-Dictionary Encoder/Decoder with SIMD         │
└─────────────────────────────────────────────────────────────────┘

        ┌──────────┐
        │   main   │
        └────┬─────┘
             │
             v
        ┌────────────┐
        │   cli      │──────────────────┐
        │            │                  │
        │ - mod      │                  │
        │ - commands │                  │
        │ - config   │                  │
        └─────┬──────┘                  │
              │                         │
              v                         v
    ┌─────────────────┐        ┌──────────────┐
    │   lib (base_d)  │        │  Dictionary  │
    │                 │        │   Registry   │
    └────────┬────────┘        │  (TOML cfg)  │
             │                 └──────────────┘
             │
    ┌────────┴────────────────────────────┐
    │                                     │
    v                                     v
┌─────────┐                      ┌──────────────┐
│  core   │                      │  encoders    │
│         │                      │              │
│ - dict  │◄─────────────────────┤ - algorithms │
│ - cfg   │                      │ - streaming  │
└─────────┘                      └──────┬───────┘
                                        │
    ┌───────────────────────────────────┼───────────────┐
    │                                   │               │
    v                                   v               v
┌──────────┐                    ┌──────────────┐   ┌─────────┐
│ features │                    │     simd     │   │  tests  │
│          │                    │              │   └─────────┘
│ - comp   │                    │ - x86_64     │
│ - hash   │                    │ - aarch64    │
│ - detect │                    │ - lut        │
└──────────┘                    │ - generic    │
                                │ - variants   │
                                │ - translate  │
                                └──────────────┘
```

## Component Map

### Layer 1: Entry Point
```
main.rs
  └─> Delegates to cli::run()
```

**Responsibility**: Binary entry point only.

---

### Layer 2: CLI Interface
```
cli/
  ├─ mod.rs       - CLI argument parsing, pipeline orchestration
  ├─ commands.rs  - Matrix mode, detection, streaming wrappers
  └─ config.rs    - Dictionary creation helpers
```

**Responsibilities**:
- Parse command-line arguments (clap)
- Coordinate encoding/decoding pipeline:
  1. Input (file/stdin)
  2. Decode (optional)
  3. Decompress (optional)
  4. Hash (optional)
  5. Compress (optional)
  6. Encode (optional)
  7. Output (stdout/file)
- Special modes: Matrix effect, auto-detection, streaming

**Key Dependencies**: `base_d` library, `clap`, `crossterm`, I/O

---

### Layer 3: Library Core (`lib.rs`)

```
lib.rs
  ├─> Public API: encode(), decode()
  ├─> Re-exports from modules
  └─> Documentation
```

**Responsibilities**:
- Public API surface
- Mode-based dispatch to appropriate encoder/decoder
- Library documentation

**Exports**:
- `encode(data, dict) -> String`
- `decode(encoded, dict) -> Result<Vec<u8>>`
- Types: `Dictionary`, `DictionaryRegistry`, `EncodingMode`, etc.
- Features: compression, hashing, detection
- Streaming: `StreamingEncoder`, `StreamingDecoder`

---

### Layer 4: Core Domain (`core/`)

```
core/
  ├─ dictionary.rs  - Dictionary struct, lookup tables, validation
  └─ config.rs      - TOML parsing, registry, encoding modes
```

**Responsibilities**:

**dictionary.rs**:
- `Dictionary` struct: character mapping, reverse lookup
- Fast lookup table optimization (256-element array for ASCII)
- Three construction modes:
  - BaseConversion (arbitrary char set)
  - Chunked (power-of-2, RFC 4648)
  - ByteRange (Unicode range mapping)
- Validation (uniqueness, size constraints)

**config.rs**:
- `EncodingMode` enum: BaseConversion, Chunked, ByteRange
- `DictionaryConfig`: TOML-deserializable dictionary spec
- `DictionaryRegistry`: collection of dictionaries + settings
- TOML parsing from bundled `dictionaries.toml` or user overrides

**Dependencies**: `serde`, `toml`

---

### Layer 5: Encoding/Decoding Engine (`encoders/`)

```
encoders/
  ├─ algorithms/
  │    ├─ math.rs        - BigInt base conversion
  │    ├─ chunked.rs     - RFC 4648 bit chunking
  │    └─ byte_range.rs  - 1:1 byte→char mapping
  └─ streaming/
       ├─ encoder.rs     - Streaming encode wrapper
       ├─ decoder.rs     - Streaming decode wrapper
       └─ hasher.rs      - Streaming hash integration
```

**Responsibilities**:

**algorithms/**:
- Three encoding strategies (selected by `Dictionary.mode()`):
  1. **math.rs**: Treats data as big-endian integer, divmod by base
     - Uses `num-bigint` for arbitrary precision
     - Variable-length output
  2. **chunked.rs**: Fixed-width bit groups (6-bit for base64, etc.)
     - Padding support
     - RFC 4648 compliance
     - Delegates to SIMD when available
  3. **byte_range.rs**: Direct byte value → Unicode codepoint
     - Zero overhead (1 byte = 1 char)
     - Validates range on decode

**streaming/**:
- `StreamingEncoder`/`StreamingDecoder`: buffered I/O for large files
- `hasher.rs`: integrated hashing during streaming operations

**Dependencies**: `num-bigint`, `num-traits`, SIMD module

---

### Layer 6: SIMD Acceleration (`simd/`)

```
simd/
  ├─ mod.rs               - Unified entry point, CPU detection
  ├─ variants.rs          - Dictionary variant identification
  ├─ translate.rs         - Character translation tables
  ├─ lut/
  │    ├─ small.rs        - ≤16 char dictionaries (SIMD LUT)
  │    └─ large.rs        - 17-64 char dictionaries (SIMD LUT)
  ├─ generic/
  │    └─ mod.rs          - Power-of-2 sequential dictionaries
  ├─ x86_64/
  │    ├─ mod.rs          - Platform detection (AVX2, SSSE3)
  │    ├─ common.rs       - Shared x86_64 utilities
  │    └─ specialized/
  │         ├─ base16.rs  - Hex-optimized SIMD
  │         ├─ base32.rs  - Base32-optimized SIMD
  │         ├─ base64.rs  - Base64-optimized SIMD
  │         └─ base256.rs - Byte-range SIMD
  └─ aarch64/
       ├─ mod.rs          - NEON detection
       ├─ generic.rs      - NEON generic impl
       └─ specialized/
            ├─ base16.rs
            ├─ base32.rs
            ├─ base64.rs
            ├─ base256.rs
            └─ common.rs
```

**Responsibilities**:
- Runtime CPU feature detection (cached in `OnceLock`)
- Automatic SIMD selection via `encode_with_simd()` / `decode_with_simd()`
- Selection hierarchy:
  1. Specialized: base64/base32/base16/base256 (RFC standard dictionaries)
  2. Generic: sequential power-of-2 dictionaries
  3. LUT: arbitrary power-of-2 dictionaries (small/large)
  4. None: fallback to scalar

**Platform Support**:
- x86_64: AVX2, SSSE3
- aarch64: NEON (mandatory)
- Other: returns `None`, uses scalar fallback

**Dependencies**: `std::arch` intrinsics

---

### Layer 7: Features (`features/`)

```
features/
  ├─ compression.rs  - Compress/decompress (gzip, zstd, brotli, lz4, snappy, lzma)
  ├─ hashing.rs      - Hash algorithms (SHA, BLAKE, MD5, XXH, CRC)
  └─ detection.rs    - Auto-detect dictionary from encoded data
```

**Responsibilities**:

**compression.rs**:
- `CompressionAlgorithm` enum
- `compress(data, algo, level)` / `decompress(data, algo)`
- Algorithm-specific level normalization

**hashing.rs**:
- `HashAlgorithm` enum
- `hash(data, algo)` / `hash_with_config(data, algo, config)`
- XXHash seed/secret configuration

**detection.rs**:
- `DictionaryDetector`: statistical analysis
- `detect_dictionary()`: returns ranked matches
- Heuristics: character frequency, padding, length ratios

**Dependencies**: `flate2`, `brotli`, `zstd`, `lz4`, `snap`, `xz2`, `sha2`, `sha3`, `blake2`, `blake3`, `md-5`, `twox-hash`, `crc`

---

## Data Flow Diagrams

### Encoding Flow

```
Input Data (bytes)
    │
    ├──> [Hash?] ──> hash output ──> encode ──> stdout
    │
    └──> [Compress?] ──> compressed bytes
              │
              └──> Select Encoding Mode
                      │
                      ├──> BaseConversion ──> math::encode()
                      │                            │
                      │                            └──> BigInt conversion
                      │
                      ├──> Chunked ──────────> chunked::encode()
                      │                            │
                      │                            ├──> SIMD path (if available)
                      │                            │      └──> simd::encode_with_simd()
                      │                            │             │
                      │                            │             ├──> Specialized (base64/32/16/256)
                      │                            │             ├──> GenericSimdCodec (sequential)
                      │                            │             └──> LUT (arbitrary)
                      │                            │
                      │                            └──> Scalar fallback (bit manipulation)
                      │
                      └──> ByteRange ──────────> byte_range::encode()
                                                       │
                                                       └──> Direct byte→codepoint mapping
                                                              (SIMD for base256)

    └──> Encoded String ──> stdout
```

### Decoding Flow

```
Input String
    │
    └──> [Detect Dictionary?] ──> DictionaryDetector
              │                        │
              │                        └──> Statistical analysis
              │                               ├─ Character frequency
              │                               ├─ Padding detection
              │                               └─ Length validation
              │
              └──> Select Decoding Mode
                      │
                      ├──> BaseConversion ──> math::decode()
                      │                            │
                      │                            └──> BigInt conversion
                      │
                      ├──> Chunked ──────────> chunked::decode()
                      │                            │
                      │                            ├──> SIMD path (if available)
                      │                            │      └──> simd::decode_with_simd()
                      │                            │
                      │                            └──> Scalar fallback
                      │
                      └──> ByteRange ──────────> byte_range::decode()
                                                       │
                                                       └──> Codepoint→byte mapping

    └──> Binary Data (bytes)
              │
              └──> [Decompress?] ──> decompressed bytes ──> stdout
```

### Streaming Flow

```
Input Stream (File/Stdin)
    │
    └──> StreamingEncoder / StreamingDecoder
              │
              ├──> Buffered read (8KB chunks)
              │
              ├──> [Hash Integration?] ──> StreamingHasher
              │                                 │
              │                                 └──> Incremental hash updates
              │
              └──> Chunked processing
                      │
                      ├──> BaseConversion: accumulate to boundary
                      ├──> Chunked: process complete groups
                      └──> ByteRange: 1:1 streaming

    └──> Output Stream (File/Stdout)
```

### CLI Pipeline Flow

```
main ──> cli::run()
           │
           └──> Parse args (clap)
                  │
                  ├──> Special modes
                  │      ├─ --list ──> print dictionaries
                  │      ├─ --neo ──> Matrix mode (commands::matrix_mode)
                  │      ├─ --detect ──> Auto-detect (commands::detect_mode)
                  │      └─ config ──> Query available options
                  │
                  └──> Standard pipeline
                         │
                         ├──> Read input (file/stdin)
                         │
                         ├──> Step 1: Decode (if --decode)
                         │              └──> decode(text, dict)
                         │
                         ├──> Step 2: Decompress (if --decompress)
                         │              └──> decompress(data, algo)
                         │
                         ├──> Step 3: Hash (if --hash)
                         │              └──> hash_with_config()
                         │                     └──> encode hash ──> stdout
                         │
                         ├──> Step 4: Compress (if --compress)
                         │              └──> compress(data, algo, level)
                         │
                         └──> Step 5: Encode/Output
                                  ├──> --raw ──> raw bytes to stdout
                                  ├──> --encode ──> encode(data, dict) ──> stdout
                                  ├──> --dejavu ──> random dict encode ──> stdout
                                  └──> default ──> default dict encode ──> stdout
```

## Module Boundaries

### Clear Boundaries ✓

1. **CLI ↔ Library**: Clean separation via public API
   - CLI never imports from `encoders`, `core`, `simd` directly
   - All access through `lib.rs` re-exports

2. **Core ↔ Encoders**: Core provides `Dictionary`, encoders consume it
   - No circular dependencies
   - Core is pure data structures + configuration

3. **Encoders ↔ SIMD**: Encoders delegate to SIMD when available
   - SIMD returns `Option<T>` (fallback pattern)
   - SIMD imports `Dictionary` but doesn't modify it

4. **Features ↔ Library**: Features are optional utilities
   - Independent of encoding/decoding core
   - Used by CLI, not by encoders

### Coupling Points

1. **Dictionary dependency**: Nearly universal
   - Used by: encoders, SIMD, CLI config helpers
   - This is appropriate - Dictionary is the central domain model

2. **SIMD selection logic**: Duplicated between `simd/mod.rs` and algorithm implementations
   - `chunked.rs` and `byte_range.rs` call `simd::encode_with_simd()`
   - Selection logic exists in both places

3. **Configuration loading**: Scattered across CLI and features
   - XXHash config loaded in `cli/config.rs`
   - Compression levels loaded in `cli/config.rs`
   - Could be centralized

## Key Design Patterns

1. **Strategy Pattern**: `EncodingMode` enum dispatches to different algorithm modules
2. **Fallback Pattern**: SIMD returns `Option<T>`, scalar path used on `None`
3. **Builder Pattern**: Dictionary construction with `new_with_mode_and_range()`
4. **Registry Pattern**: `DictionaryRegistry` manages named configurations
5. **Pipeline Pattern**: CLI chains operations: decode → decompress → hash → compress → encode
6. **Streaming Pattern**: `StreamingEncoder`/`StreamingDecoder` for large files
