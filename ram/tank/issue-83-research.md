# Issue #83 Research: Random Behavior Flags Warning

**Issue URL:** https://github.com/coryzibell/base-d/issues/83
**Status:** Open

## Issue Description

From Construct review of `base-d` project. Persephone identified UX issue.

### Problem

`--compress` and `--hash` without arguments randomly select an algorithm. This is intentional but undiscoverable - users don't know output will vary.

### Solution

Print a notice to stderr when random selection occurs:

```
Note: Using randomly selected algorithm 'zstd' (use --compress=zstd to fix)
```

## Acceptance Criteria

- [ ] Random selection prints notice to stderr
- [ ] Notice includes the selected algorithm
- [ ] Notice shows how to make it deterministic
- [ ] `--quiet` suppresses the notice

## Flags with Random Behavior

### 1. `--compress` (optional value)

**Location:** `/home/w3surf/work/personal/code/base-d/src/cli/mod.rs`

**Definition (lines 28-31):**
```rust
/// Compress data before encoding (gzip, zstd, brotli, lz4)
/// If no algorithm specified, picks randomly
#[arg(short = 'c', long, value_name = "ALGORITHM")]
compress: Option<Option<String>>,
```

**Random selection sites:**

1. **Non-streaming mode (lines 274-281):**
```rust
// Parse compression algorithm - if flag present but no value, pick random
let compress_algo = match &cli.compress {
    Some(Some(algo)) => Some(base_d::CompressionAlgorithm::from_str(algo)?),
    Some(None) => Some(base_d::CompressionAlgorithm::from_str(
        commands::select_random_compress(),
    )?),
    None => None,
};
```

2. **Streaming mode (lines 302-306):**
```rust
let resolved_compress = match &cli.compress {
    Some(Some(name)) => Some(name.clone()),
    Some(None) => Some(commands::select_random_compress().to_string()),
    None => None,
};
```

**Random selection function:** `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs` (lines 82-95)
```rust
/// Available compression algorithms for random selection
pub const COMPRESS_ALGORITHMS: &[&str] = &["gzip", "zstd", "brotli", "lz4"];

/// Select a random compression algorithm
pub fn select_random_compress() -> &'static str {
    use rand::seq::SliceRandom;
    COMPRESS_ALGORITHMS.choose(&mut rand::thread_rng()).unwrap()
}
```

### 2. `--hash` (optional value)

**Location:** `/home/w3surf/work/personal/code/base-d/src/cli/mod.rs`

**Definition (lines 41-44):**
```rust
/// Compute hash of input data (md5, sha256, sha512, blake3, etc.)
/// If no algorithm specified, picks randomly
#[arg(long, value_name = "ALGORITHM")]
hash: Option<Option<String>>,
```

**Random selection sites:**

1. **Non-streaming mode (lines 394-398):**
```rust
if let Some(hash_opt) = &cli.hash {
    let hash_name = match hash_opt {
        Some(name) => name.clone(),
        None => commands::select_random_hash().to_string(),
    };
```

2. **Streaming mode (lines 297-301):**
```rust
let resolved_hash = match &cli.hash {
    Some(Some(name)) => Some(name.clone()),
    Some(None) => Some(commands::select_random_hash().to_string()),
    None => None,
};
```

**Random selection function:** `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs` (lines 79-89)
```rust
/// Available hash algorithms for random selection
pub const HASH_ALGORITHMS: &[&str] = &["md5", "sha256", "sha512", "blake3", "xxh64", "xxh3"];

/// Select a random hash algorithm
pub fn select_random_hash() -> &'static str {
    use rand::seq::SliceRandom;
    HASH_ALGORITHMS.choose(&mut rand::thread_rng()).unwrap()
}
```

### 3. `--dejavu` flag

**Location:** `/home/w3surf/work/personal/code/base-d/src/cli/mod.rs`

**Definition (lines 84-87):**
```rust
/// Random dictionary encoding: Pick a random dictionary and encode with it
/// When combined with --neo, uses random dictionary for Matrix mode
#[arg(long, conflicts_with = "encode")]
dejavu: bool,
```

**Random selection sites:**

1. **Matrix mode with --neo (lines 211-219):**
```rust
// If --dejavu is set and no explicit dictionary, pick random
let initial_dictionary = if cli.dejavu && dictionary_opt.is_none() {
    // Silently select - the puzzle is figuring out which dictionary was used
    commands::select_random_dictionary(&config, false)?
} else {
    dictionary_opt
        .as_deref()
        .unwrap_or("base256_matrix")
        .to_string()
};
```

2. **Hash output encoding (lines 408-418):**
```rust
let dict_name = if let Some(encode_name) = &cli.encode {
    encode_name.clone()
} else if cli.dejavu {
    commands::select_random_dictionary(&config, false)?
} else if let Some(default) = &config.settings.default_dictionary {
    default.clone()
} else {
    // No default configured - use random
    commands::select_random_dictionary(&config, false)?
};
```

3. **Main encoding (lines 435-440):**
```rust
} else if cli.dejavu {
    // Random dictionary encoding
    let random_dict = commands::select_random_dictionary(&config, true)?;
    let encode_dictionary = create_dictionary(&config, &random_dict)?;
    let encoded = encode(&data, &encode_dictionary);
    output_encoded(&encoded, &random_dict)?;
```

**Random selection function:** `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs` (lines 50-77)
```rust
/// Select a random dictionary from the registry.
/// Only selects from dictionaries with `common=true` (renders consistently across platforms).
/// Optionally prints a "dejavu: ..." message to stderr based on the `print_message` flag.
/// Returns the dictionary name.
pub fn select_random_dictionary(
    config: &DictionaryRegistry,
    print_message: bool,
) -> Result<String, Box<dyn std::error::Error>> {
    use rand::seq::SliceRandom;
    let mut rng = rand::thread_rng();

    // Filter to only common dictionaries (those that render consistently across platforms)
    let dict_names: Vec<&String> = config
        .dictionaries
        .iter()
        .filter(|(_, cfg)| cfg.common)
        .map(|(name, _)| name)
        .collect();

    let random_dict = dict_names
        .choose(&mut rng)
        .ok_or("No common dictionaries available")?;

    // Silently select - the puzzle is figuring out which dictionary was used
    let _ = print_message; // Reserved for future verbose mode

    Ok(random_dict.to_string())
}
```

## Warning Implementation Points

### Where Warnings Should Be Added

1. **`select_random_compress()` function** - immediately after selection, before returning
   - Location: `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs` (line 92)
   - Message: `Note: Using randomly selected compression algorithm '{selected}' (use --compress={selected} to fix)`

2. **`select_random_hash()` function** - immediately after selection, before returning
   - Location: `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs` (line 88)
   - Message: `Note: Using randomly selected hash algorithm '{selected}' (use --hash={selected} to fix)`

3. **`select_random_dictionary()` function** - when `print_message` is true
   - Location: `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs` (line 74)
   - Message: `Note: Using randomly selected dictionary '{selected}' (use --encode={selected} to fix)`

### Quiet Flag Consideration

**Current issue:** No `--quiet` flag exists in the CLI.

**Options:**
1. Add a `--quiet` flag to the `Cli` struct
2. Respect the existing `--no-color` flag as a proxy for quiet mode
3. Check for standard environment variable like `QUIET=1`

The issue acceptance criteria mentions `--quiet` should suppress notices, so this flag needs to be added.

## Suggested Warning Format

```
Note: Using randomly selected <type> '<algorithm>' (use --<flag>=<algorithm> to fix)
```

Examples:
- `Note: Using randomly selected compression algorithm 'zstd' (use --compress=zstd to fix)`
- `Note: Using randomly selected hash algorithm 'blake3' (use --hash=blake3 to fix)`
- `Note: Using randomly selected dictionary 'base85' (use --encode=base85 to fix)`

## Implementation Strategy

1. Add `--quiet` flag to `Cli` struct
2. Pass quiet flag to selection functions (or make it available via context)
3. Modify selection functions to print to stderr unless quiet is true
4. Ensure warnings go to stderr (not stdout) so they don't interfere with data pipeline

## Handoff Notes

- Persephone designs message → Smith implements → Neo merges
- All code locations identified and documented
- Message format consistent across all random selections
- Need to handle both streaming and non-streaming modes
