# base-d CLI Structure Research

**Date:** 2025-12-01
**Project:** `/home/w3surf/work/personal/code/base-d`

## Summary

base-d already uses clap with derive macros and has one subcommand (`config`). The CLI is well-organized in a `src/cli/` module with separate files for commands and config helpers.

## 1. Current CLI Parsing

### Crate
- **clap 4.5** with `derive` feature
- Uses `#[derive(Parser)]` and `#[derive(Subcommand)]` derive macros

### Entry Point
- **`src/main.rs`** (lines 1-8): Minimal, just calls `cli::run()`
- **`src/cli/mod.rs`** (lines 1-503): Contains the `Cli` struct, `Commands` enum, and `run()` function

### Parser Location
- `/home/w3surf/work/personal/code/base-d/src/cli/mod.rs` - lines 12-116

## 2. Current Flag Structure

### Top-level Flags (all in mod.rs lines 21-116)

| Flag | Short | Long | Type | Description |
|------|-------|------|------|-------------|
| encode | `-e` | `--encode` | `Option<String>` | Encode using this dictionary |
| decode | `-d` | `--decode` | `Option<String>` | Decode from this dictionary |
| compress | `-c` | `--compress` | `Option<Option<String>>` | Compress (optional algorithm) |
| decompress | | `--decompress` | `Option<String>` | Decompress after decoding |
| level | | `--level` | `Option<u32>` | Compression level |
| hash | | `--hash` | `Option<Option<String>>` | Compute hash (optional algorithm) |
| hash_seed | | `--hash-seed` | `Option<u64>` | xxHash seed |
| hash_secret_stdin | | `--hash-secret-stdin` | `bool` | Read XXH3 secret from stdin |
| raw | `-r` | `--raw` | `bool` | Output raw binary |
| detect | | `--detect` | `bool` | Auto-detect dictionary |
| show_candidates | | `--show-candidates` | `Option<usize>` | Show top N candidates |
| file | | positional | `Option<PathBuf>` | File to process |
| stream | `-s` | `--stream` | `bool` | Streaming mode |
| neo | | `--neo` | `Option<Option<String>>` | Matrix mode |
| dejavu | | `--dejavu` | `bool` | Random dictionary |
| cycle | | `--cycle` | `bool` | Cycle dictionaries (Matrix) |
| random | | `--random` | `bool` | Random switching (Matrix) |
| interval | | `--interval` | `Option<String>` | Switch interval |
| max_size | | `--max-size` | `usize` | Max input size (default 100MB) |
| force | | `--force` | `bool` | Process files exceeding limit |
| no_color | | `--no-color` | `bool` | Disable colors |
| quiet | `-q` | `--quiet` | `bool` | Suppress notices |
| superman | | `--superman` | `bool` | Remove Matrix speed limit |

### Existing Subcommand: `config` (lines 118-138)

```rust
#[derive(Subcommand)]
enum Commands {
    Config {
        #[arg(long)]
        compression: bool,
        #[arg(long)]
        dictionaries: bool,
        #[arg(long)]
        hash: bool,
        #[arg(long)]
        json: bool,
    },
}
```

Usage: `base-d config --dictionaries`, `base-d config --compression --json`, etc.

## 3. Code Organization

```
src/
  main.rs           # Entry point (8 lines)
  lib.rs            # Library exports
  cli/
    mod.rs          # Cli struct, Commands enum, run(), handle_config()
    commands.rs     # matrix_mode(), detect_mode(), streaming_encode/decode(), etc.
    config.rs       # create_dictionary(), get_compression_level(), load_xxhash_config()
  core/
    mod.rs
    config.rs       # DictionaryRegistry, DictionaryConfig, etc.
    dictionary.rs   # Dictionary struct
  encoders/
    mod.rs
    algorithms/     # radix.rs, chunked.rs, byte_range.rs, errors.rs
    streaming/      # encoder.rs, decoder.rs, hasher.rs
  features/
    mod.rs
    compression.rs
    detection.rs
    hashing.rs
  simd/             # SIMD implementations
```

## 4. Existing Subcommand Pattern

Yes, there's already a subcommand pattern in place:

```rust
#[derive(Parser)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,
    // ... other flags
}

#[derive(Subcommand)]
enum Commands {
    Config { ... },
}
```

The current design allows the subcommand to be **optional** (`Option<Commands>`), so top-level flags still work:
- `base-d -e base64` works (no subcommand)
- `base-d config --dictionaries` works (subcommand)

## 5. Considerations for Refactor

### Strengths
1. **Already using clap derive** - No migration needed
2. **Already has subcommand infrastructure** - Just need to add more
3. **Clean separation** - CLI code already in `src/cli/` module
4. **commands.rs exists** - Logical place for subcommand handlers

### Obstacles/Considerations
1. **Backward compatibility** - Current users use `--encode`/`--decode` as flags. A subcommand-based design (`base-d encode`, `base-d decode`) would break scripts.
2. **Optional vs required subcommand** - Currently optional. If made required, need migration path.
3. **Flag conflicts** - Some flags are context-dependent:
   - `--decompress` only makes sense with decode
   - `--compress` only makes sense with encode
   - `--neo`, `--dejavu`, `--cycle`, `--random`, `--interval`, `--superman` are Matrix-specific
4. **Testing** - `/home/w3surf/work/personal/code/base-d/tests/cli.rs` has integration tests that would need updating

### Suggested Subcommand Structure

```
base-d encode [OPTIONS] [FILE]      # Current: base-d -e <dict> [FILE]
base-d decode [OPTIONS] [FILE]      # Current: base-d -d <dict> [FILE]
base-d config [OPTIONS]             # Already exists
base-d detect [OPTIONS] [FILE]      # Current: base-d --detect [FILE]
base-d matrix [OPTIONS]             # Current: base-d --neo [OPTIONS]
```

### Key Files to Modify

1. `/home/w3surf/work/personal/code/base-d/src/cli/mod.rs` - Main CLI definition
2. `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs` - Command implementations
3. `/home/w3surf/work/personal/code/base-d/tests/cli.rs` - Update tests
