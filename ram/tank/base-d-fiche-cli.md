# base-d Fiche CLI Research

## CLI Args Structure (`src/cli/args.rs`)

### FicheArgs (lines 212-236)
```rust
pub struct FicheArgs {
    pub file: Option<PathBuf>,           // Input file (reads from stdin if not provided)
    #[arg(short = 'd', long)]
    pub decode: bool,                    // Decode mode (fiche -> JSON)
    #[arg(short = 'p', long)]
    pub pretty: bool,                    // Pretty-print JSON output (decode only)
    #[arg(short = 'm', long)]
    pub minify: bool,                    // Minify output to single line (encode only)
    #[arg(long)]
    pub no_tokenize: bool,               // Disable field name tokenization
    #[arg(short = 'o', long)]
    pub output: Option<PathBuf>,         // Output file (writes to stdout if not provided)
}
```

**Key observation:** FicheArgs does NOT have a `--compress` flag.

### SchemaArgs (lines 142-162) - Has compression support
```rust
pub struct SchemaArgs {
    pub file: Option<PathBuf>,
    #[arg(short = 'd', long)]
    pub decode: bool,
    #[arg(short = 'p', long)]
    pub pretty: bool,
    #[arg(short = 'c', long, value_enum)]
    pub compress: Option<SchemaCompressionAlgoCli>,   // <-- COMPRESSION HERE
    #[arg(short = 'o', long)]
    pub output: Option<PathBuf>,
}
```

### SchemaCompressionAlgoCli Enum (lines 165-178)
```rust
#[derive(Clone, Copy, Debug, ValueEnum)]
pub enum SchemaCompressionAlgoCli {
    Brotli,
    Lz4,
    Zstd,
}

impl From<SchemaCompressionAlgoCli> for base_d::SchemaCompressionAlgo {
    fn from(cli: SchemaCompressionAlgoCli) -> Self {
        match cli {
            SchemaCompressionAlgoCli::Brotli => base_d::SchemaCompressionAlgo::Brotli,
            SchemaCompressionAlgoCli::Lz4 => base_d::SchemaCompressionAlgo::Lz4,
            SchemaCompressionAlgoCli::Zstd => base_d::SchemaCompressionAlgo::Zstd,
        }
    }
}
```

---

## Fiche Handler (`src/cli/handlers/fiche.rs`)

Current implementation (lines 8-45):
```rust
pub fn handle(
    args: FicheArgs,
    _global: &GlobalArgs,
    _config: &DictionaryRegistry,
) -> Result<(), Box<dyn std::error::Error>> {
    // Read input
    let input_text = if let Some(file_path) = &args.file {
        fs::read_to_string(file_path)?
    } else {
        let mut buffer = String::new();
        io::stdin().read_to_string(&mut buffer)?;
        buffer
    };

    // Process: encode or decode
    let output = if args.decode {
        decode_fiche(input_text.trim(), args.pretty)?
    } else if args.minify {
        encode_fiche_minified(input_text.trim())?
    } else if args.no_tokenize {
        encode_fiche_readable(input_text.trim())?
    } else {
        encode_fiche(input_text.trim())?
    };

    // Write output
    if let Some(output_path) = &args.output {
        fs::write(output_path, output.as_bytes())?;
    } else {
        println!("{}", output);
    }

    Ok(())
}
```

**Key observation:** No compression handling. Uses three encode variants:
- `encode_fiche()` - tokenized (default)
- `encode_fiche_minified()` - tokenized + single line
- `encode_fiche_readable()` - no tokenization

---

## Schema Handler Pattern (`src/cli/handlers/schema.rs`)

Shows how compression is handled:
```rust
let output = if args.decode {
    decode_schema(input_text.trim(), args.pretty)?
} else {
    let compress = args.compress.map(Into::into);  // Convert CLI enum to lib enum
    encode_schema(input_text.trim(), compress)?
};
```

---

## Fiche Encoding Functions (`src/encoders/algorithms/schema/mod.rs`)

Library-level functions (lines 158-204):

```rust
/// Default: tokenized field names
pub fn encode_fiche(json: &str) -> Result<String, SchemaError> {
    encode_fiche_with_options(json, false, true)
}

/// Tokenized + minified to single line
pub fn encode_fiche_minified(json: &str) -> Result<String, SchemaError> {
    encode_fiche_with_options(json, true, true)
}

/// Human-readable (no tokenization)
pub fn encode_fiche_readable(json: &str) -> Result<String, SchemaError> {
    encode_fiche_with_options(json, false, false)
}

fn encode_fiche_with_options(
    json: &str,
    minify: bool,
    tokenize: bool,
) -> Result<String, SchemaError> {
    use parsers::{InputParser, JsonParser};

    let ir = JsonParser::parse(json)?;
    match (minify, tokenize) {
        (true, _) => fiche::serialize_minified(&ir),
        (false, true) => fiche::serialize(&ir),
        (false, false) => fiche::serialize_readable(&ir),
    }
}

/// Decode fiche -> JSON
pub fn decode_fiche(fiche_input: &str, pretty: bool) -> Result<String, SchemaError> {
    use serializers::{JsonSerializer, OutputSerializer};

    let ir = fiche::parse(fiche_input)?;
    JsonSerializer::serialize(&ir, pretty)
}
```

**Key observation:** No compression in fiche pipeline. It's text-based Unicode, not binary.

---

## Fiche Format Details (`src/encoders/algorithms/schema/fiche.rs`)

### Delimiters
| Symbol | Unicode | Purpose |
|--------|---------|---------|
| `@` | U+0040 | Schema/token map prefix |
| `◉` | U+25C9 | Row start (fisheye) |
| `┃` | U+2503 | Field separator (heavy pipe) |
| `◈` | U+25C8 | Array element separator |
| `∅` | U+2205 | Null value |
| `▓` | U+2593 | Space marker (minified mode) |
| `჻` | U+10FB | Nested object separator |

### Type Markers (superscript)
| Marker | Type |
|--------|------|
| `ⁱ` | int (I64/U64) |
| `ˢ` | str (String) |
| `ᶠ` | float (F64) |
| `ᵇ` | bool |

### Format Examples
```
# Tokenized (default)
@ᚠ=id,ᚡ=name,ᚢ=active
@users┃ᚠⁱ┃ᚡˢ┃ᚢᵇ
◉1┃alice┃true
◉2┃bob┃false

# Readable (--no-tokenize)
@users┃idⁱ┃nameˢ┃activeᵇ
◉1┃alice┃true
◉2┃bob┃false

# Minified (--minify)
@ᚠ=id,ᚡ=name,ᚢ=active▓@users┃ᚠⁱ┃ᚡˢ┃ᚢᵇ▓◉1┃alice┃true▓◉2┃bob┃false
```

---

## Compression in Schema Encoding (`src/encoders/algorithms/schema/compression.rs`)

Schema uses a prefix-byte system for compression:

```rust
const ALGO_NONE: u8 = 0x00;
const ALGO_BROTLI: u8 = 0x01;
const ALGO_LZ4: u8 = 0x02;
const ALGO_ZSTD: u8 = 0x03;
const DEFAULT_LEVEL: u32 = 6;

pub fn compress_with_prefix(binary: &[u8], algo: Option<SchemaCompressionAlgo>) -> Result<Vec<u8>, SchemaError>
pub fn decompress_with_prefix(binary: &[u8]) -> Result<Vec<u8>, SchemaError>
```

**Note:** This is for binary data. Fiche is text-based and doesn't currently use this.

---

## Summary

### Current State
- **Fiche** = text-based Unicode format, model-readable
- **Schema** = binary format with display96 encoding + optional compression
- Fiche has no compression support in CLI or library

### If Adding Compression to Fiche

1. **Add to FicheArgs:**
   ```rust
   #[arg(short = 'c', long, value_enum)]
   pub compress: Option<SchemaCompressionAlgoCli>,
   ```

2. **Modify handler:** Would need new library functions that:
   - Encode fiche text
   - Compress the UTF-8 bytes
   - Encode compressed bytes to base64/display96 for transport

3. **Design question:** Fiche is meant to be model-readable. Compression makes it opaque (like schema/carrier98). May defeat the purpose unless:
   - Compression is optional for wire transport
   - Decompression happens before model parsing
   - Frame delimiters indicate compressed content

### Recommended Handoff
- **Architect** for design decision on fiche+compression semantics
- **Smith** for implementation once design is decided
