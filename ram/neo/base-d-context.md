# base-d Context

**Repo:** `~/work/personal/code/base-d`
**Status:** Active development

## Recent Work (2025-12-03)

Fiche array flattening overhaul (pushed to main):
- Arrays now flatten to indexed paths: `field჻0჻subfield` instead of JSON strings
- Added `჻` (Georgian comma U+10FB) as nested path separator
- `[]` markers in schema enable round-trip fidelity
- Empty arrays preserved via markers with no indexed fields
- Nested arrays inside array elements work correctly
- Cold parse tested: both Sonnet and Haiku parse fiche without format explanation

carrier98 docs updated to fiche spec v1.4:
- New delimiter table with `჻`
- Array flattening section replaces circled numbers approach
- Complex nesting example (YouTube-style 4-level deep structure)

## Previous Work (2025-12-02)

PR #139 merged - fiche header metadata annotations (#137):
- Extract scalar fields as metadata when JSON has scalar + array pattern
- Format: `@root[key=val,key2=val2]┃field:type`
- Extended IR with `metadata: Option<HashMap<String, String>>`
- Haiku cold-parsed complex nested data (10 users, nested objects) at parity with JSON

Issue #138 open - markdown table → IR parser:
- Parse GFM tables back to fiche IR
- Enables round-trip: model outputs markdown → parse → emit fiche/JSON

## Previous Work (2025-12-01)

PR #124 merged - Ascon and KangarooTwelve hash algorithms:
- Added `ascon-hash` and `k12` crates
- CLI: `--hash ascon`, `--hash k12`, `--hash kangarootwelve`
- Streaming and non-streaming support
- Docs updated (README, HASHING.md)
- Issue #108 closed

## Previous Work (2025-11-30)

PR #118 merged - Full aarch64/NEON support:
- Specialized codecs (Base64/32/16/256): Full parity
- SmallLutCodec, Base64LutCodec: Full parity
- GappedSequentialCodec: Encode SIMD, decode scalar (both archs)
- GenericSimdCodec: Full NEON port

## Open Issues

- #119: SIMD decode for GappedSequentialCodec (low priority optimization)
  - Current decode is scalar LUT lookup in blocks
  - Could use `_mm_shuffle_epi8` (SSSE3) / `vqtbl1q_u8` (NEON) for parallel lookup

## Key Patterns

- `#[target_feature(enable = "...")]` requires explicit `unsafe {}` blocks in Rust 2024
- Cross-target clippy needs C cross-compiler for compression deps (lz4-sys, lzma-sys, zstd-sys)
- CI handles cross-platform linting

## Commands

```bash
cargo clippy --all-targets -- -D warnings  # Local lint
cargo test                                   # Full test suite
mx commit "message" -p                       # Commit and push
mx pr merge <number>                         # Merge PR
```
