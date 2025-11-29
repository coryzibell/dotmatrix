# Zstd Small Data Compression Research

## Research Date
2025-11-29

## Question
Why does zstd compressed output sometimes equal or exceed input size for small data?

---

## Key Findings

### 1. Frame Overhead

**Minimum frame structure:**
- Magic number: 4 bytes (0xFD2FB528)
- Frame header descriptor: 1 byte (minimum)
- Frame header (variable): 2-14 bytes total
- Block header: 3 bytes per block
- Content checksum: 4 bytes (optional)

**Practical overhead:**
- Absolute minimum: 5 bytes (magic + header descriptor)
- Typical minimum: 12 bytes (includes content size + checksum)
- Maximum header: 22 bytes (all optional fields enabled)

**Comparison to zlib:**
- Zlib header: 6 bytes total
- Zstd is 2x heavier for small payloads (12 vs 6 bytes)

### 2. Compression Threshold

**Performance characteristics:**
- Files < 4KB: zstd often performs worse than zlib
- Sweet spot: Files > 4KB show zstd advantages
- Very small data (< 256 bytes): High likelihood of size increase

**Why compression fails on small data:**
> "The smaller the amount of data to compress, the more difficult it is to compress.
> Compression algorithms learn from past data how to compress future data. But at
> the beginning of a new data set, there is no 'past' to build upon."

### 3. When Compressed Size >= Input Size

**Causes:**
1. **Overhead exceeds savings**: 12-byte frame + 3-byte block header = 15 bytes minimum
2. **Incompressible data**: Random or already-compressed data
3. **Insufficient pattern repetition**: Small datasets lack redundancy
4. **No compression dictionary**: Without pre-shared patterns, no baseline exists

**Example scenario:**
- Input: 20 bytes of semi-random data
- Frame overhead: 12 bytes
- Block overhead: 3 bytes
- Best case savings: 5-10 bytes
- Result: Compressed size ≈ input size or larger

### 4. Dictionary Compression Solution

**For small data patterns:**
- Train dictionary on sample dataset
- Pre-shared dictionary provides "past" data
- Compression ratio improvement: 2.8x → 6.9x (example from Meta)
- Most effective in first few KB
- Requires correlation between samples

**Example from Meta Engineering:**
> "Each user is a bit under 1 KB... Naively applying zstd individually to each
> file cuts this down to just over 300 KB. But if we create a one-time,
> pre-shared dictionary, with zstd the size drops to 122 KB"

### 5. Recommendations

**Do NOT use zstd compression when:**
- Input size < 4KB (without dictionary)
- Data is already compressed
- High-volume small records where 12-byte overhead matters
- Diverse data with no pattern correlation

**DO use zstd compression when:**
- Input size > 4KB
- Training dictionary is feasible for small correlated data
- Speed is priority over absolute minimum size
- Working with structured/repetitive data

---

## Sources

- [Zstd Compression Format Spec](https://github.com/facebook/zstd/blob/dev/doc/zstd_compression_format.md)
- [RFC 8878 - Zstandard Media Type](https://datatracker.ietf.org/doc/html/rfc8878)
- [Meta Engineering: Smaller and faster data compression](https://engineering.fb.com/2016/08/31/core-infra/smaller-and-faster-data-compression-with-zstandard/)
- [GitHub Issue #1134: Compression ratio worse than zlib for small blobs](https://github.com/facebook/zstd/issues/1134)
- [Gregory Szorc: Better Compression with Zstandard](https://gregoryszorc.com/blog/2017/03/07/better-compression-with-zstandard/)
- [Zstd Manual](https://facebook.github.io/zstd/zstd_manual.html)

---

## Technical Details

### Frame Header Structure (2-14 bytes)
```
┌─────────────────────────┐
│ Frame_Header_Descriptor │ 1 byte (mandatory)
├─────────────────────────┤
│ Window_Descriptor       │ 0-1 byte (optional)
├─────────────────────────┤
│ Dictionary_ID           │ 0-4 bytes (optional)
├─────────────────────────┤
│ Frame_Content_Size      │ 0-8 bytes (optional)
└─────────────────────────┘
```

### Complete Frame Structure
```
┌─────────────────────────┐
│ Magic_Number            │ 4 bytes (0xFD2FB528)
├─────────────────────────┤
│ Frame_Header            │ 2-14 bytes
├─────────────────────────┤
│ Block_Header            │ 3 bytes per block
│ Block_Content           │ variable
│ (repeat blocks...)      │
├─────────────────────────┤
│ Content_Checksum        │ 4 bytes (optional)
└─────────────────────────┘
```

### Block Header (3 bytes)
- Last_Block flag: 1 bit
- Block_Type: 2 bits (Raw/RLE/Compressed/Reserved)
- Block_Size: 21 bits (max 128KB or Window_Size)
