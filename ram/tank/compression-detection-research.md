# Compression Detection in Rust - Research Report

**Date:** 2025-11-29
**Target:** base-d auto-detection feature
**Objective:** Detect compression algorithm from byte stream

---

## Executive Summary

Three primary approaches for compression detection in Rust:

1. **`infer`** - Magic byte file type detection (supports 8 compression formats)
2. **`autocompress`** - Auto-detects gzip, bzip2, xz, zstd and provides decoder
3. **`detect-compression`** - Extension-based detection (less useful for byte streams)

**Recommendation:** Use `infer` for detection, then dispatch to appropriate decompressor.

---

## Crate Analysis

### 1. infer (v0.19.0)
**URL:** https://crates.io/crates/infer
**GitHub:** https://github.com/bojand/infer
**Docs:** https://docs.rs/infer

**Supported Compression Formats:**
- gz (gzip) - `application/gzip`
- bz2 (bzip2) - `application/x-bzip2`
- bz3 (bzip3) - `application/vnd.bzip3`
- 7z - `application/x-7z-compressed`
- xz - `application/x-xz`
- zst (zstd) - `application/zstd`
- lz4 - `application/x-lz4`
- lz (lzip) - `application/x-lzip`

**Also handles:** ZIP, TAR, RAR, EPUB, etc.

**Features:**
- Pure magic byte detection (no filesystem required)
- `no_std` and `no_alloc` support
- Custom matcher support (with `alloc`)
- No external magic file database needed
- Hardcoded magic byte patterns

**Usage Example:**
```rust
use infer;

let buf = [0x1F, 0x8B, 0x08, ...]; // gzip magic bytes
let kind = infer::get(&buf).expect("file type is known");

if kind.matcher_type() == infer::MatcherType::Archive {
    println!("{} - {}", kind.mime_type(), kind.extension());
    // Output: application/gzip - gz
}
```

**Pros:**
- Simple API
- Wide format support
- Lightweight
- Actively maintained (v0.13.0 added zstd skippable frames)

**Cons:**
- No Brotli support (Brotli has no standard magic bytes)
- Detection only, not decompression

---

### 2. autocompress (v0.1.0)
**URL:** https://crates.io/crates/autocompress
**Docs:** https://docs.rs/autocompress/0.1.0/autocompress/

**Supported Formats:**
- gzip
- bzip2
- xz
- zstd

**Features:**
- Auto-detection from magic bytes
- Built-in decoder/encoder
- I/O thread pool for background compression
- Parallel compression support

**Usage Example:**
```rust
use std::io::prelude::*;
use autocompress::autodetect_open;

let mut reader = autodetect_open("file.xz")?;
let mut buf = Vec::new();
reader.read_to_end(&mut buf)?;
```

**Pros:**
- Detection + decompression in one
- Parallel processing support
- Clean API

**Cons:**
- Limited format support (4 formats)
- File-based API (may not work well with pure byte streams)
- No Brotli or LZ4

---

### 3. detect-compression
**URL:** https://lib.rs/crates/detect-compression
**Docs:** https://docs.rs/detect-compression/latest/detect_compression/

**Features:**
- BufRead and Writer with auto-detection
- Detection from file extension (not magic bytes)

**Pros:**
- Simple integration with I/O traits

**Cons:**
- Extension-based, not magic byte-based
- Not suitable for byte stream detection without filename

---

## Magic Bytes Reference

| Format | Magic Bytes (Hex) | Notes |
|--------|------------------|-------|
| **Gzip** | `1F 8B` | Well-established, reliable |
| **Bzip2** | `42 5A 68` | "BZh" in ASCII |
| **Zstd** | `28 B5 2F FD` | 4-byte signature |
| **LZ4 (frame)** | `04 22 4D 18` | Frame format only (little-endian `0x184D2204`) |
| **XZ** | `FD 37 7A 58 5A 00` | 6-byte signature |
| **7z** | `37 7A BC AF 27 1C` | "7z¼¯'" |
| **Brotli** | None | **No standard magic bytes** - relies on HTTP headers |
| **Deflate (raw)** | None | No magic bytes |
| **Zlib** | `78 xx` | Deflate wrapper, varies by compression level |

**Sources:**
- https://stackoverflow.com/questions/11108188/compression-algorithm-magic-signatures
- https://stackoverflow.com/questions/68637971/how-to-detect-zstd-compression
- https://github.com/google/brotli/issues/298 (Brotli lacks magic bytes)
- https://gist.github.com/leommoore/f9e57ba2aa4bf197ebc5

---

## Brotli Problem

**Critical Finding:** Brotli does not have standardized magic bytes.

- Issue tracked: https://github.com/google/brotli/issues/298
- Raw Brotli streams are not self-identifying
- Typically relies on HTTP `Content-Encoding: br` header
- Cannot be reliably auto-detected from byte stream alone

**Workarounds:**
1. Try decompression and catch errors (trial and error)
2. Require explicit format flag for Brotli
3. Use container format with Brotli payload

---

## Recommended Implementation Strategy

For base-d byte stream detection:

### Phase 1: Magic Byte Detection
```rust
use infer;

fn detect_compression(data: &[u8]) -> Option<CompressionFormat> {
    if let Some(kind) = infer::get(data) {
        match kind.extension() {
            "gz" => Some(CompressionFormat::Gzip),
            "bz2" => Some(CompressionFormat::Bzip2),
            "zst" => Some(CompressionFormat::Zstd),
            "lz4" => Some(CompressionFormat::Lz4),
            "xz" => Some(CompressionFormat::Xz),
            _ => None,
        }
    } else {
        None
    }
}
```

### Phase 2: Decompression
Use format-specific crates:
- **gzip/deflate:** `flate2`
- **bzip2:** `bzip2`
- **zstd:** `zstd`
- **lz4:** `lz4`
- **xz:** `xz2`
- **brotli:** `brotli` (requires explicit flag, can't auto-detect)

### Phase 3: Fallback
- If no magic bytes match, assume uncompressed
- OR provide explicit format flag option
- OR trial decompression with error handling

---

## Additional Resources

### Compression Libraries
- **flate2-rs:** https://github.com/rust-lang/flate2-rs (gzip/deflate/zlib)
- **async-compression:** https://crates.io/crates/async-compression (multi-format async)

### File Signature Detection
- **file-format crate:** https://crates.io/crates/file-format (alternative to infer)

### References
- Lib.rs compression category: https://lib.rs/compression
- LogRocket Rust compression guide: https://blog.logrocket.com/rust-compression-libraries/
- Are We Web Yet compression: https://www.arewewebyet.org/topics/compression/

---

## Gaps & Limitations

1. **Brotli:** Cannot auto-detect (no magic bytes)
2. **Raw Deflate:** Cannot auto-detect (no magic bytes, use Zlib wrapper instead)
3. **Custom formats:** Would require manual magic byte registration with `infer`

---

## Recommendation for base-d

**Primary approach:**
1. Use `infer` crate for magic byte detection
2. Support: gzip, bzip2, zstd, lz4, xz
3. Require `--format brotli` flag for Brotli input (cannot auto-detect)
4. Fallback to uncompressed if no magic bytes match

**Dependencies to add:**
```toml
[dependencies]
infer = "0.19"
flate2 = "1.0"      # gzip
bzip2 = "0.4"       # bzip2
zstd = "0.13"       # zstd
lz4 = "1.24"        # lz4
xz2 = "0.1"         # xz
brotli = "3.5"      # brotli (manual flag only)
```

This gives solid coverage of common compression formats while being honest about Brotli's limitations.
