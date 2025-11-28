# base-d Entropy Mode Design

## Problem

Currently, base-d has several disconnected features:
- `--dejavu` picks a random dictionary for encoding
- `--hash <algo>` requires an explicit algorithm
- `--compress <algo>` requires an explicit algorithm
- These don't compose cleanly (compress + dejavu outputs hex instead of encoded)

We want **maximum entropy by default** when randomization is requested, and clean composition of all features.

## Proposal: Unified Randomization

### 1. Config-Driven Defaults (dictionaries.toml)

```toml
[settings]
default_dictionary = "cards"

# Optional: if set, --hash without argument uses this
# If not set, --hash without argument randomizes
# default_hash = "sha256"

# Optional: if set, --compress without argument uses this
# If not set, --compress without argument randomizes
# default_compress = "zstd"
```

### 2. Flag Behavior Changes

| Flag | Current | Proposed |
|------|---------|----------|
| `--dejavu` | Random dictionary | Random dictionary (unchanged) |
| `--hash sha256` | Use sha256 | Use sha256 (unchanged) |
| `--hash` (no arg) | Error | Random from [md5, sha256, sha512, blake3, xxh64, xxh3] OR config default |
| `--compress zstd` | Use zstd | Use zstd (unchanged) |
| `--compress` (no arg) | Error | Random from [gzip, zstd, brotli, lz4] OR config default |

### 3. Composition Rules

When multiple flags combine, they should chain properly:

```
input → compress → hash → encode → output
```

Examples:
- `--compress --hash --dejavu`: Random compress → random hash → random encode
- `--compress gzip --dejavu`: gzip compress → random encode
- `--hash --dejavu`: Random hash → random encode
- `--compress --hash sha256 -e base64`: Random compress → sha256 → base64

### 4. Neo Mode Integration

Neo mode (`--neo`) streams data with Matrix-style output. It should support:

```bash
# Stream random data, compressed, as Matrix rain
base-d --neo --compress

# Stream hashed random data as Matrix rain
base-d --neo --hash

# Full entropy: random compress, hash, dictionary
base-d --neo --compress --hash --dejavu
```

For streaming mode, compress/hash would apply to each chunk before display.

### 5. Implementation Phases

**Phase 1: Fix composition bug** ← DO NOW
- Ensure compress + dejavu actually encodes (not hex output)
- Chain: compress → encode with selected dictionary
- Same for hash + dejavu when no explicit encode

**Phase 2: Remove default dictionary**
- Delete `default_dictionary` from dictionaries.toml
- Remove `default_dictionary()` fallback function
- When no dictionary specified and no dejavu: error or pick random?
  - Decision: require explicit `-e` or `--dejavu`

**Phase 3: Optional arguments for --hash and --compress**
- Use `clap`'s optional value syntax
- `--hash` alone = random algorithm
- `--compress` alone = random algorithm
- Add `select_random_hash()` and `select_random_compress()` functions

**Phase 4: Neo mode integration** (Future)
- Apply compress/hash to streaming chunks
- Maintain visual output while processing

**Phase 5: `--entropy` flag** (Future)
- Meta-randomization as described above

## Code Locations

Based on Tank's intel:

- **CLI parsing**: `src/cli/mod.rs`
- **Compress + encode logic**: `src/cli/mod.rs` ~lines 291-329
- **Hash + encode logic**: `src/cli/mod.rs` ~lines 266-288
- **Config/settings**: `src/core/config.rs`
- **Random dictionary selection**: `src/cli/commands.rs` `select_random_dictionary()`

## New Functions Needed

```rust
// In src/cli/commands.rs

pub fn select_random_hash() -> &'static str {
    const HASH_ALGOS: &[&str] = &["md5", "sha256", "sha512", "blake3", "xxh64", "xxh3"];
    use rand::seq::SliceRandom;
    HASH_ALGOS.choose(&mut rand::thread_rng()).unwrap()
}

pub fn select_random_compress() -> &'static str {
    const COMPRESS_ALGOS: &[&str] = &["gzip", "zstd", "brotli", "lz4"];
    use rand::seq::SliceRandom;
    COMPRESS_ALGOS.choose(&mut rand::thread_rng()).unwrap()
}
```

## Decisions

1. **No default dictionary in config** - Embrace entropy. Remove `default_dictionary` from toml. Everything randomizes unless explicitly specified.

2. **Neo mode hashing** - Hash each line separately for now. (See Future: streaming blockchain visualization)

3. **`--entropy` flag** - Future feature, complex behavior (see below)

## Upload Commit Use Case

With this design, the upload script simplifies to:

```bash
# Title: random hash, random encode
git diff --staged | base-d --hash --dejavu

# Body: random compress, random encode
echo "$message" | base-d --compress --dejavu
```

No Python randomization needed - base-d handles it all.

---

## Future Ideas

### Neo Mode Streaming Blockchain

*Watching a tiny blockchain in realtime.*

When using `--neo --hash`, each line gets hashed separately. Visual effect: Matrix rain where each falling column is a hash of that moment's data. A blockchain forming in real-time down your terminal.

Could extend to show hash chaining - each line's hash includes previous line's hash. True streaming blockchain visualization.

### `--entropy` Flag (Complex)

A meta-randomization flag that works with or without `--neo`:

**Behavior:**
1. Randomly decide WHETHER to hash (coin flip)
2. If hashing, randomly pick algorithm
3. Randomly decide WHETHER to compress (coin flip)
4. If compressing, randomly pick algorithm
5. Randomly pick dictionary OR output raw bytes (true entropy)

**With streaming (`--neo --entropy`):**
- Constantly changing parameters mid-stream
- Each chunk gets different random decisions
- Pipe through SIMD for performance
- Could pull from `/dev/random` and transform it through shifting algorithms
- Output: pure chaos, but deterministic if you know the seed

**Use case:** Entropy enhancement tool. Feed it `/dev/random`, get transformed entropy out. Each byte has been through a randomly-selected gauntlet of transforms.

```bash
# Entropy amplifier
cat /dev/random | base-d --neo --entropy --seed $RANDOM

# Visual chaos
base-d --neo --entropy
```

This is genuinely useful for:
- Visual entropy testing
- Generating unpredictable output for seeds
- Art/visualization
- Stress testing decoders
