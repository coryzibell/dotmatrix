# Issue #128: Expose Schema IR Types

## Work Completed

Exposed schema encoding internals for library users to build custom frontends (YAML, CSV, TOML parsers).

### Files Modified

1. **`/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/mod.rs`**
   - Added re-exports for IR types: `IntermediateRepresentation`, `SchemaHeader`, `FieldDef`, `FieldType`, `SchemaValue`, `SchemaError`
   - Added re-exports for traits: `InputParser`, `OutputSerializer`
   - Added re-exports for reference implementations: `JsonParser`, `JsonSerializer`
   - Added re-exports for binary layer: `encode_framed`, `decode_framed`

2. **`/home/w3surf/work/personal/code/base-d/src/lib.rs`**
   - Created new `pub mod schema` with comprehensive documentation
   - Included architecture overview (3-layer pipeline)
   - Added CSV parser example demonstrating custom frontend
   - Documented all exported types, traits, and functions
   - Re-exported all schema types under `base_d::schema::`

3. **`/home/w3surf/work/personal/code/base-d/tests/schema_api.rs`** (new file)
   - 11 comprehensive tests verifying public API
   - Tests type accessibility, binary layer functions, traits
   - Tests custom parser/serializer implementation
   - Tests backward compatibility of high-level API

### What's Now Exported

```rust
pub mod schema {
    // High-level API (backward compatible)
    pub use encode_schema, decode_schema;

    // Compression
    pub use SchemaCompressionAlgo;

    // IR types
    pub use IntermediateRepresentation;
    pub use SchemaHeader;
    pub use FieldDef;
    pub use FieldType;
    pub use SchemaValue;

    // Traits
    pub use InputParser;
    pub use OutputSerializer;

    // Reference implementations
    pub use JsonParser;
    pub use JsonSerializer;

    // Binary layer
    pub use pack;
    pub use unpack;
    pub use encode_framed;
    pub use decode_framed;

    // Errors
    pub use SchemaError;
}
```

### Test Results

```
cargo test --test schema_api
running 11 tests
test test_compression_options ... ok
test test_binary_layer_functions ... ok
test test_custom_parser_implementation ... ok
test test_custom_serializer_implementation ... ok
test test_error_types_accessible ... ok
test test_field_type_methods ... ok
test test_high_level_api_still_works ... ok
test test_ir_get_value ... ok
test test_json_reference_implementations ... ok
test test_schema_header_methods ... ok
test test_schema_types_are_accessible ... ok

test result: ok. 11 passed; 0 failed; 0 ignored; 0 measured
```

All existing tests pass. No regressions.

```
cargo clippy --all-targets --all-features -- -D warnings
Finished `dev` profile: success (no warnings)
```

```
cargo doc --no-deps
Generated /home/w3surf/work/personal/code/base-d/target/doc/base_d/index.html
```

### Architecture

The schema module exposes a three-layer architecture:

1. **Input layer** - Parse custom formats → IR
   - Implement `InputParser` trait
   - Example: `JsonParser` (reference)

2. **Binary layer** - IR ↔ binary encoding
   - `pack()` / `unpack()` - core binary encoding
   - `encode_framed()` / `decode_framed()` - display96 + delimiters

3. **Output layer** - IR → custom formats
   - Implement `OutputSerializer` trait
   - Example: `JsonSerializer` (reference)

### Usage Example

Library users can now implement custom parsers:

```rust
use base_d::schema::{InputParser, IntermediateRepresentation, SchemaError};

struct YamlParser;

impl InputParser for YamlParser {
    type Error = SchemaError;

    fn parse(input: &str) -> Result<IntermediateRepresentation, Self::Error> {
        // Parse YAML → build IR
    }
}
```

### Backward Compatibility

Existing high-level API remains unchanged:
- `base_d::encode_schema()`
- `base_d::decode_schema()`
- `base_d::SchemaCompressionAlgo`

New schema types available under `base_d::schema::*`.
