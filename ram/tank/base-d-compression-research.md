# base-d Compression Implementation Research

**Research Date**: 2025-11-29
**Target**: `/home/w3surf/work/personal/code/base-d/`
**Operator**: Tank

## Summary

base-d has compression support built-in, but **NO minimum size threshold**. It compresses everything you feed it, regardless of size.

## How Compression Works

### Implementation Location
- **Module**: `/home/w3surf/work/personal/code/base-d/src/features/compression.rs`
- **CLI Handler**: `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs`

### Compression Flow
Data flows through these stages:
1. **Decode** (if `--decode` specified)
2. **Decompress** (if `--decompress` specified)
3. **Compress** (if `--compress` specified)
4. **Encode** (if `--encode` specified, or default if compressed)

### Supported Algorithms

| Algorithm | Flag | Default Level | Implementation |
|-----------|------|---------------|----------------|
| gzip | `--compress gzip` | 6 | `flate2::write::GzEncoder` |
| zstd | `--compress zstd` | 3 | `zstd::encode_all()` |
| brotli | `--compress brotli` | 6 | `brotli::CompressorReader` |
| lz4 | `--compress lz4` | 0 | `lz4::block::compress()` |
| snappy | `--compress snappy` | 0 | `snap::raw::Encoder` |
| lzma | `--compress lzma` | 6 | `xz2::write::XzEncoder` |

## Critical Finding: NO Size Threshold

### Code Analysis

Examined the compression module (`compression.rs`) - it's a straightforward wrapper:

```rust
pub fn compress(
    data: &[u8],
    algorithm: CompressionAlgorithm,
    level: u32,
) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
    match algorithm {
        CompressionAlgorithm::Gzip => compress_gzip(data, level),
        CompressionAlgorithm::Zstd => compress_zstd(data, level),
        // ... etc
    }
}
```

**No conditional logic**. No size checks. No thresholds.

### Behavior on Small Data

From the documentation (`COMPRESSION.md`), there's an explicit example showing the problem:

**Without compression**:
```bash
$ echo "This is repeated text. This is repeated text." | base-d -e base64
VGhpcyBpcyByZXBlYXRlZCB0ZXh0LiBUaGlzIGlzIHJlcGVhdGVkIHRleHQuCg==
# 64 characters
```

**With compression**:
```bash
$ echo "This is repeated text. This is repeated text." | base-d --compress gzip -e base64
H4sIAAAAAAAA/8tIzcnJVyjPL8pJUQhJLcpLzE1VKM8v0lEIy88vySzJzM9TSMxLUQIA1hIOdSwAAAA=
# 84 characters (overhead for small data)
```

**Result**: 31% size INCREASE on small data. The documentation acknowledges this but doesn't prevent it.

## How It Handles Small Data

**Answer**: It doesn't. The implementation blindly compresses everything:

1. User provides data via stdin or file
2. CLI passes data to `compress()` function
3. Compression library (gzip, zstd, etc.) adds headers/metadata
4. Result is encoded (base64 by default)
5. Output is larger than input for small data

### Example Compression Functions

**gzip** (lines 72-78):
```rust
fn compress_gzip(data: &[u8], level: u32) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
    use flate2::write::GzEncoder;
    use flate2::Compression;

    let mut encoder = GzEncoder::new(Vec::new(), Compression::new(level));
    encoder.write_all(data)?;
    Ok(encoder.finish()?)
}
```

**zstd** (lines 90-92):
```rust
fn compress_zstd(data: &[u8], level: u32) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
    Ok(zstd::encode_all(data, level as i32)?)
}
```

No pre-checks. No size validation. Just raw compression calls.

## Minimum Size Threshold

**Status**: DOES NOT EXIST

Searched entire codebase for:
- `threshold`
- `min.*size`
- `should.*compress`

Only results were SIMD-related lookup table thresholds (unrelated to compression).

## Configuration

Default compression levels are in `dictionaries.toml`:

```toml
[compression.gzip]
default_level = 6

[compression.zstd]
default_level = 3

[compression.brotli]
default_level = 6

[compression.lz4]
default_level = 0

[compression.snappy]
default_level = 0

[compression.lzma]
default_level = 6
```

But there's **no configuration option** for minimum size thresholds.

## Usage Examples

```bash
# Compress with gzip, encode with base64 (default)
echo "Hello, World!" | base-d --compress gzip

# Specify compression level
echo "Data" | base-d --compress brotli --level 11 -e base64

# Decompress after decoding
echo "H4sIAAAAAAAA/..." | base-d -d base64 --decompress gzip

# Raw compressed output (no encoding)
echo "Data" | base-d --compress gzip --raw > output.gz
```

## Limitations (From Documentation)

1. **Streaming Mode**: Not supported with compression
2. **Memory Usage**: Compression loads entire file into memory
3. **No Algorithm Detection**: Must manually specify compression algorithm when decompressing

## Conclusion

base-d compression:
1. Uses zstd (and 5 other algorithms)
2. Provides configurable compression levels
3. **Does NOT check data size before compressing**
4. **Does NOT have a minimum threshold before compression kicks in**
5. Will happily make small data larger (as demonstrated in their own docs)

This is exactly the zstd overhead problem kautau mentioned. The tool compresses blindly without considering whether compression makes sense for the data size.

## Relevant File Paths

- Compression module: `/home/w3surf/work/personal/code/base-d/src/features/compression.rs`
- CLI commands: `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs`
- Config handling: `/home/w3surf/work/personal/code/base-d/src/cli/config.rs`
- Documentation: `/home/w3surf/work/personal/code/base-d/docs/COMPRESSION.md`
- Feature docs: `/home/w3surf/work/personal/code/base-d/COMPRESSION_FEATURE.md`
- Dependencies: `/home/w3surf/work/personal/code/base-d/Cargo.toml`

## Recommendations

If you wanted to add threshold logic, you'd modify:
1. `compress()` function in `compression.rs` to check data size
2. Add threshold config to `dictionaries.toml` structure
3. Update CLI to expose threshold override flags

But currently, no such logic exists.
