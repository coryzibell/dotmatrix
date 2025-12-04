# Schema Encoding Module Structure

**Date:** 2025-12-02
**Project:** base-d
**Issue:** #126
**Status:** Design Phase

## Executive Summary

Schema encoding adds a fourth encoding mode to base-d: a binary-packed, LLM-to-LLM wire protocol that's denser than JSON/TOON. This requires JSON parsing, binary packing, display96 dictionary, and CLI integration.

## Existing Architecture Analysis

### Current Structure
```
src/
├── main.rs                    # Entry point -> cli::run()
├── lib.rs                     # Public API, encode()/decode() dispatch
├── core/
│   ├── config.rs              # DictionaryConfig, EncodingMode enum, TOML registry
│   └── dictionary.rs          # Dictionary type, builder pattern, lookups
├── encoders/
│   ├── algorithms/
│   │   ├── radix.rs           # BigUint base conversion
│   │   ├── chunked.rs         # RFC 4648 chunked mode (SIMD-accelerated)
│   │   ├── byte_range.rs      # 1:1 byte-to-emoji mapping
│   │   └── errors.rs          # DecodeError, DictionaryNotFoundError
│   └── streaming/
│       ├── encoder.rs         # StreamingEncoder for large files
│       └── decoder.rs         # StreamingDecoder for large files
├── cli/
│   ├── args.rs                # Clap argument structs (EncodeArgs, DecodeArgs, etc.)
│   ├── commands.rs            # Helper functions (select_random_dictionary, etc.)
│   ├── config.rs              # create_dictionary(), load_xxhash_config()
│   └── handlers/
│       ├── encode.rs          # handle(EncodeArgs)
│       ├── decode.rs          # handle(DecodeArgs)
│       ├── detect.rs          # Auto-detect dictionary from encoded data
│       └── hash.rs            # Standalone hashing
└── features/
    ├── compression.rs         # CompressionAlgorithm, compress(), decompress()
    ├── hashing.rs             # HashAlgorithm, hash(), XxHashConfig
    └── detection.rs           # DictionaryDetector, detect_dictionary()
```

### Key Integration Points

1. **EncodingMode Enum** (`src/core/config.rs`):
   - Currently: `Radix`, `Chunked`, `ByteRange`
   - Add: `Schema`

2. **Public API Dispatch** (`src/lib.rs:199-257`):
   ```rust
   pub fn encode(data: &[u8], dictionary: &Dictionary) -> String {
       match dictionary.mode() {
           EncodingMode::Radix => encoders::algorithms::radix::encode(...),
           EncodingMode::Chunked => encoders::algorithms::chunked::encode_chunked(...),
           EncodingMode::ByteRange => encoders::algorithms::byte_range::encode_byte_range(...),
           // Add: EncodingMode::Schema => encoders::algorithms::schema::encode_schema(...),
       }
   }
   ```

3. **CLI Handlers** (`src/cli/handlers/`):
   - `encode.rs`: Reads input, calls compress/hash/encode pipeline
   - `decode.rs`: Calls decode/decompress/hash pipeline
   - Add: `schema.rs` for dedicated schema subcommand

4. **Dictionary Registration** (`dictionaries.toml`):
   - display96 needs to be registered as a dictionary entry
   - No existing "display" dictionaries found

## Proposed Module Structure

### New Files

```
src/encoders/algorithms/schema/
├── mod.rs                      # Public API: encode_schema(), decode_schema()
├── json_parser.rs              # JSON -> IR (intermediate representation)
├── binary_packer.rs            # IR -> binary format
├── binary_unpacker.rs          # Binary -> IR
├── json_serializer.rs          # IR -> JSON
├── frame.rs                    # Frame delimiters, display96 encoding/decoding
└── types.rs                    # IR types: SchemaValue, FieldType, SchemaHeader, etc.

src/cli/handlers/schema.rs      # CLI handler for `base-d schema` subcommand
```

### Module Responsibilities

#### `src/encoders/algorithms/schema/mod.rs`
```rust
pub fn encode_schema(json: &str, dictionary: &Dictionary) -> Result<String, SchemaError>;
pub fn decode_schema(encoded: &str, dictionary: &Dictionary) -> Result<String, SchemaError>;
```
- Entry point for schema encoding/decoding
- Orchestrates pipeline: JSON → IR → binary → display96 → framed
- Validates dictionary is display96
- Error handling

#### `src/encoders/algorithms/schema/types.rs`
```rust
pub enum FieldType { U64, I64, String, Array(Box<FieldType>), Bool, Null }
pub struct SchemaHeader { flags: u8, root_key: Option<String>, row_count: usize, ... }
pub struct SchemaValue { ... }
pub struct IntermediateRepresentation { ... }
```
- Core type definitions
- Bitflags for header (typed_values, has_nulls, has_root_key, etc.)

#### `src/encoders/algorithms/schema/json_parser.rs`
```rust
pub fn parse_json(json: &str) -> Result<IntermediateRepresentation, SchemaError>;
```
- Leverage `serde_json` (already in Cargo.toml)
- Flatten nested objects to dotted keys (`user.profile.avatar`)
- Infer types (integers, strings, arrays, nulls, bools)
- Build IR with schema + values

#### `src/encoders/algorithms/schema/binary_packer.rs`
```rust
pub fn pack_binary(ir: &IntermediateRepresentation) -> Vec<u8>;
```
- Serialize header (flags, root_key, row_count, field_count, field_types[], field_names[])
- Generate null bitmap if has_nulls flag set
- Encode values densely (varint for integers, length-prefix for strings)
- No delimiters between values - schema defines boundaries

#### `src/encoders/algorithms/schema/binary_unpacker.rs`
```rust
pub fn unpack_binary(data: &[u8]) -> Result<IntermediateRepresentation, SchemaError>;
```
- Parse header, read schema metadata
- Reconstruct IR from dense value stream
- Use schema to know where each value starts/ends

#### `src/encoders/algorithms/schema/json_serializer.rs`
```rust
pub fn serialize_json(ir: &IntermediateRepresentation) -> String;
```
- Convert IR back to JSON
- Unflatten dotted keys to nested objects
- Use `serde_json` for final JSON serialization

#### `src/encoders/algorithms/schema/frame.rs`
```rust
pub const FRAME_START: char = '𓍹';  // U+13379
pub const FRAME_END: char = '𓍺';    // U+1337A

pub fn encode_with_frame(binary: &[u8], dictionary: &Dictionary) -> String;
pub fn decode_from_frame(encoded: &str, dictionary: &Dictionary) -> Result<Vec<u8>, SchemaError>;
```
- Apply/remove frame delimiters
- Encode binary → display96 (use existing chunked.rs logic)
- Validate payload alphabet contains only display96 chars

#### `src/cli/handlers/schema.rs`
```rust
pub fn handle(args: SchemaArgs, global: &GlobalArgs, config: &DictionaryRegistry) -> Result<...>;
```
- Handle `base-d schema [JSON]` (encode) and `base-d schema -d [ENCODED]` (decode)
- Read from stdin or file
- Call `encode_schema()` / `decode_schema()`
- Output to stdout

### CLI Integration

#### New Subcommand (`src/cli/args.rs`)
```rust
#[derive(Args, Debug)]
pub struct SchemaArgs {
    /// Input file (reads from stdin if not provided)
    pub file: Option<PathBuf>,

    /// Decode mode
    #[arg(short = 'd', long)]
    pub decode: bool,

    /// Output file (writes to stdout if not provided)
    #[arg(short = 'o', long)]
    pub output: Option<PathBuf>,
}
```

#### Updated Command Enum (`src/cli/mod.rs` or equivalent)
```rust
#[derive(Subcommand, Debug)]
pub enum Command {
    Encode(EncodeArgs),
    Decode(DecodeArgs),
    Schema(SchemaArgs),  // New
    // ...
}
```

### Dictionary Registration

#### Add to `dictionaries.toml`
```toml
[dictionaries.display96]
chars = "━┃┏┓┗┛┣┫┳┻╋▀▄█▌▐░▒▓■□▪▫▬▲△▶▷▼▽◀◁◆◇○◌●★☆♠♣♥♦⬛⬜⚡⚪⚫✓✗✦✧─│┌┐└┘├┤┬┴┼╌╎═║╔╗╚╝╠╣╦╩╬⋅∘∙·•◘◙◚◛◜◝◞◟"
mode = "chunked"
common = true
```
**Note:** Exact display96 chars need to be defined. Above is illustrative.

## Reusable Components

### Existing Code to Leverage

1. **`serde_json`** (already a dependency):
   - Use for JSON parsing and serialization
   - `serde_json::from_str()` and `serde_json::to_string()`

2. **Chunked encoding** (`src/encoders/algorithms/chunked.rs`):
   - Reuse for display96 encoding (base-96 chunked mode)
   - Already handles arbitrary power-of-two bases
   - SIMD-accelerated on x86_64/aarch64

3. **Error handling** (`src/encoders/algorithms/errors.rs`):
   - Add `SchemaError` enum with variants:
     - `InvalidJson(String)`
     - `InvalidFrame`
     - `InvalidDictionary(String)`
     - `InvalidBinaryFormat(String)`
     - `MismatchedSchema`

4. **Streaming infrastructure** (`src/encoders/streaming/`):
   - **Not applicable** for schema mode (requires entire JSON document)
   - Schema encoding is inherently non-streamable (needs full object graph)

### Varint Encoding

No existing varint implementation found. Options:

1. **Add dependency**: `unsigned-varint` crate (lightweight, 0 deps)
2. **Implement inline**: Simple LEB128-style varint (10-20 lines)

**Recommendation:** Implement inline in `binary_packer.rs` / `binary_unpacker.rs`. Keeps dependencies lean.

```rust
fn encode_varint(value: usize, buf: &mut Vec<u8>) {
    let mut n = value;
    while n >= 0x80 {
        buf.push((n as u8) | 0x80);
        n >>= 7;
    }
    buf.push(n as u8);
}

fn decode_varint(data: &[u8], offset: &mut usize) -> Result<usize, SchemaError> {
    // Implementation
}
```

## Concerns and Alternatives

### Scope Considerations

1. **Type Inference Complexity**:
   - JSON values can be ambiguous (e.g., "123" vs 123)
   - Need clear rules for type coercion
   - **Mitigation**: Start with strict typing, add `typed_values` flag for mixed arrays later

2. **Nested Object Flattening**:
   - Dotted keys work for simple cases, but deep nesting is verbose
   - Circular references are impossible (JSON doesn't support them)
   - **Mitigation**: Schema format is designed for relatively flat data (tabular-ish)

3. **Array Handling**:
   - Primitive arrays are efficient (schema carries type)
   - Mixed arrays need per-value type tags (`typed_values` flag)
   - **Mitigation**: Detect homogeneous arrays, fall back to typed mode

4. **Dictionary Coupling**:
   - Schema mode is hardcoded to display96
   - Unlike other modes, it's not dictionary-agnostic
   - **Alternative**: Make dictionary configurable, but display96 is optimal (96 chars, visually safe)

### Alternative Approaches

1. **Separate CLI Tool**:
   - Implement as standalone `schema-d` tool instead of subcommand
   - **Rejected**: Adds maintenance overhead, less discoverable

2. **Use MessagePack/CBOR**:
   - Leverage existing binary JSON formats
   - **Rejected**: Not LLM-friendly (no schema in payload), less dense

3. **Streaming Support**:
   - JSON streaming parsers (e.g., `serde_json::StreamDeserializer`)
   - **Deferred**: Initial implementation focuses on document-level encoding
   - Could add later for JSONL (newline-delimited JSON)

## Implementation Order

1. **Phase 1: Core Types & Binary Format** (Smith)
   - `types.rs`: Define IR, FieldType, SchemaHeader
   - `binary_packer.rs`: Implement header + value packing
   - `binary_unpacker.rs`: Implement parsing
   - Unit tests for round-trip

2. **Phase 2: JSON Integration** (Smith)
   - `json_parser.rs`: serde_json → IR
   - `json_serializer.rs`: IR → serde_json
   - Handle object flattening/unflattening
   - Unit tests

3. **Phase 3: Framing & Dictionary** (Smith)
   - `frame.rs`: Frame delimiters, display96 encoding
   - Add display96 to `dictionaries.toml`
   - `mod.rs`: Orchestrate full pipeline
   - Integration tests

4. **Phase 4: CLI Integration** (Smith)
   - `cli/handlers/schema.rs`: Add handler
   - Update `cli/args.rs`: Add SchemaArgs
   - Wire up subcommand routing
   - E2E tests

5. **Phase 5: Error Handling & Polish** (Smith)
   - Comprehensive error messages
   - Add `--pretty` flag for formatted JSON output
   - Performance optimization (if needed)
   - Documentation

## Component Ownership

All implementation should be handled by **Smith** (execution specialist).

- Schema encoding is a new feature (greenfield code)
- Requires attention to bit-level binary format correctness
- No architectural decisions remain after this design

## File Tree Summary

```
/home/w3surf/work/personal/code/base-d/
├── src/
│   ├── encoders/
│   │   └── algorithms/
│   │       └── schema/              # NEW MODULE
│   │           ├── mod.rs            # Public API
│   │           ├── types.rs          # IR, FieldType, SchemaHeader
│   │           ├── json_parser.rs    # JSON → IR
│   │           ├── json_serializer.rs # IR → JSON
│   │           ├── binary_packer.rs  # IR → binary
│   │           ├── binary_unpacker.rs # binary → IR
│   │           └── frame.rs          # Framing + display96
│   ├── cli/
│   │   └── handlers/
│   │       └── schema.rs             # NEW HANDLER
│   └── core/
│       └── config.rs                 # UPDATE: Add EncodingMode::Schema
├── dictionaries.toml                 # UPDATE: Add display96
└── Cargo.toml                        # NO CHANGES (serde_json already present)
```

## Decision Rationale

### Why separate `schema/` submodule?

Schema encoding is architecturally distinct:
- Requires JSON parsing (other modes are format-agnostic)
- Non-streamable (needs full document)
- Complex multi-stage pipeline (JSON → IR → binary → display96 → framed)
- Hardcoded to display96 dictionary

Isolating in dedicated submodule maintains clean boundaries.

### Why IR (Intermediate Representation)?

Decouples concerns:
- JSON parsing/serialization is independent of binary format
- Binary format can evolve without touching JSON logic
- IR enables future backends (YAML, TOML, etc.) without duplicating binary logic
- Testability: Each stage can be unit tested independently

### Why inline varint instead of crate?

- Varint implementation is ~20 lines
- No need for full LEB128 spec compliance
- Reduces dependency surface area
- Easier to audit for correctness

---

**End of Design Document**
