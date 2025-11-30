# base-d Context

**Repo:** `~/work/personal/code/base-d`
**Status:** SIMD parity complete

## Recent Work (2025-11-30)

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
