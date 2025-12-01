# ADR: base-d CLI Refactor to Subcommand Pattern

**Status:** Proposed
**Date:** 2025-12-01
**Issue:** [#117](https://github.com/coryzibell/base-d/issues/117)

## Context

The current CLI uses a flag-based pattern (`--encode`, `--decode`, `--hash`, `--detect`) with 20+ top-level flags on the `Cli` struct. This creates:

1. Complex conditional logic in `run()` (450+ lines)
2. Conflicting flag combinations requiring manual validation
3. Poor discoverability for users
4. Difficult to extend with new features

The target is a subcommand pattern that maps operations to distinct code paths.

## Decision

### 1. Commands Enum Structure

```rust
#[derive(Parser)]
#[command(name = "base-d")]
#[command(version)]
#[command(about = "Universal multi-dictionary encoder")]
pub struct Cli {
    #[command(subcommand)]
    pub command: Commands,

    // Global flags (apply to all subcommands)
    #[command(flatten)]
    pub global: GlobalArgs,
}

#[derive(Args)]
pub struct GlobalArgs {
    /// Output raw binary data
    #[arg(short = 'r', long, global = true)]
    pub raw: bool,

    /// Suppress informational notices
    #[arg(short = 'q', long, global = true)]
    pub quiet: bool,

    /// Disable colored output
    #[arg(long, global = true)]
    pub no_color: bool,

    /// Maximum input size in bytes (0 = unlimited)
    #[arg(long, global = true, default_value = "104857600")]
    pub max_size: usize,

    /// Process files exceeding --max-size limit
    #[arg(long, global = true)]
    pub force: bool,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Encode data using a dictionary
    #[command(visible_alias = "e")]
    Encode(EncodeArgs),

    /// Decode data from a dictionary
    #[command(visible_alias = "d")]
    Decode(DecodeArgs),

    /// Auto-detect dictionary and decode
    Detect(DetectArgs),

    /// Compute hash of data
    Hash(HashArgs),

    /// Query configuration and available options
    Config {
        #[command(subcommand)]
        action: ConfigAction,
    },

    /// Matrix mode: streaming visual effect
    Neo(NeoArgs),
}

// --- Subcommand Arguments ---

#[derive(Args)]
pub struct EncodeArgs {
    /// Dictionary to use for encoding
    pub dictionary: String,

    /// Input file (reads from stdin if not provided)
    pub file: Option<PathBuf>,

    /// Compress before encoding
    #[arg(short = 'c', long, value_name = "ALG")]
    pub compress: Option<Option<String>>,

    /// Compression level
    #[arg(long)]
    pub level: Option<u32>,

    /// Compute hash of input data
    #[arg(long, value_name = "ALG")]
    pub hash: Option<String>,

    /// Output file (writes to stdout if not provided)
    #[arg(short = 'o', long)]
    pub output: Option<PathBuf>,

    /// Use streaming mode for large files
    #[arg(short = 's', long)]
    pub stream: bool,
}

#[derive(Args)]
pub struct DecodeArgs {
    /// Dictionary to decode from
    pub dictionary: String,

    /// Input file (reads from stdin if not provided)
    pub file: Option<PathBuf>,

    /// Decompress after decoding
    #[arg(long, value_name = "ALG")]
    pub decompress: Option<String>,

    /// Compute hash of decoded data
    #[arg(long, value_name = "ALG")]
    pub hash: Option<String>,

    /// Output file (writes to stdout if not provided)
    #[arg(short = 'o', long)]
    pub output: Option<PathBuf>,

    /// Use streaming mode for large files
    #[arg(short = 's', long)]
    pub stream: bool,
}

#[derive(Args)]
pub struct DetectArgs {
    /// Input file (reads from stdin if not provided)
    pub file: Option<PathBuf>,

    /// Show top N candidate dictionaries
    #[arg(long, value_name = "N")]
    pub show_candidates: Option<usize>,

    /// Decompress after decoding
    #[arg(long)]
    pub decompress: Option<String>,
}

#[derive(Args)]
pub struct HashArgs {
    /// Hash algorithm to use
    pub algorithm: String,

    /// Input file (reads from stdin if not provided)
    pub file: Option<PathBuf>,

    /// Seed for xxHash algorithms
    #[arg(long)]
    pub seed: Option<u64>,

    /// Encode hash output using dictionary
    #[arg(long, value_name = "DICT")]
    pub encode: Option<String>,

    /// Read XXH3 secret from stdin
    #[arg(long)]
    pub secret_stdin: bool,
}

#[derive(Subcommand)]
pub enum ConfigAction {
    /// List available options
    List {
        /// What to list: dictionaries, algorithms, hashes
        #[arg(value_name = "TYPE")]
        category: Option<ConfigCategory>,

        /// Output as JSON
        #[arg(long)]
        json: bool,
    },

    /// Show details for a specific dictionary
    Show {
        /// Dictionary name
        dictionary: String,
    },
}

#[derive(Clone, ValueEnum)]
pub enum ConfigCategory {
    Dictionaries,
    Algorithms,
    Hashes,
}

#[derive(Args)]
pub struct NeoArgs {
    /// Dictionary to use (default: base256_matrix)
    #[arg(long, value_name = "DICT")]
    pub dictionary: Option<String>,

    /// Use random dictionary
    #[arg(long)]
    pub dejavu: bool,

    /// Cycle through all dictionaries
    #[arg(long)]
    pub cycle: bool,

    /// Random dictionary switching
    #[arg(long)]
    pub random: bool,

    /// Switch interval (e.g., "5s", "500ms", "line")
    #[arg(long, value_name = "INTERVAL")]
    pub interval: Option<String>,

    /// Remove speed limit
    #[arg(long)]
    pub superman: bool,
}
```

### 2. Module Layout

```
src/cli/
├── mod.rs              # Cli struct, Commands enum, parse + dispatch
├── args.rs             # All Args structs (EncodeArgs, DecodeArgs, etc.)
├── global.rs           # GlobalArgs, color/size helpers
└── handlers/
    ├── mod.rs          # pub use all handlers
    ├── encode.rs       # handle_encode(args, global, config)
    ├── decode.rs       # handle_decode(args, global, config)
    ├── detect.rs       # handle_detect(args, global, config)
    ├── hash.rs         # handle_hash(args, global, config)
    ├── config.rs       # handle_config(action, global, config)
    └── neo.rs          # handle_neo(args, global, config)
```

**Rationale:**
- `args.rs` keeps all argument structs together (easy to see the full interface)
- `handlers/` mirrors the Commands enum (one handler per subcommand)
- Existing `config.rs` helpers (`create_dictionary`, `get_compression_level`, `load_xxhash_config`) can remain as utility module or move to `src/cli/util.rs`

### 3. Handler Dispatch Pattern

```rust
// src/cli/mod.rs

pub fn run() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();
    let config = DictionaryRegistry::load_with_overrides()?;

    match cli.command {
        Commands::Encode(args) => handlers::encode::handle(args, &cli.global, &config),
        Commands::Decode(args) => handlers::decode::handle(args, &cli.global, &config),
        Commands::Detect(args) => handlers::detect::handle(args, &cli.global, &config),
        Commands::Hash(args) => handlers::hash::handle(args, &cli.global, &config),
        Commands::Config { action } => handlers::config::handle(action, &cli.global, &config),
        Commands::Neo(args) => handlers::neo::handle(args, &cli.global, &config),
    }
}
```

Each handler is a pure function: `(Args, &GlobalArgs, &DictionaryRegistry) -> Result<()>`

### 4. Design Decisions

| Decision | Rationale |
|----------|-----------|
| `global = true` on shared flags | clap propagates these to all subcommands automatically |
| `visible_alias = "e"` | Shows alias in help, cleaner than separate enum variant |
| Nested `Config { action }` | Two-level subcommand (`config list`, `config show`) |
| `Option<Option<String>>` for compress | Distinguishes "not provided" vs "provided without value" (random selection) |
| Positional dictionary first | `base-d encode base64` is more intuitive than `base-d encode --dict base64` |
| No `--dejavu` on encode/decode | Removed ambiguity; use `detect` for unknown input, explicit dict for encode |
| `--output` flag | Future-proofing for file output without shell redirection |

### 5. Tradeoffs

**Removed features:**
- `--dejavu` on encode: Ambiguous UX. If you want random, use `config list dictionaries` and pick one.
- Combined `--encode` + `--decode` in single invocation: Edge case, rarely used. Can decode then pipe to encode if needed.

**Preserved features:**
- `--hash` on both encode and decode (per issue spec)
- Streaming mode (`--stream`)
- All Matrix mode options

**Breaking changes:**
- `base-d -e base64` becomes `base-d encode base64` (or `base-d e base64`)
- `base-d --detect` becomes `base-d detect`
- `base-d config --dictionaries` becomes `base-d config list dictionaries`

## Migration Checklist

### Phase 1: Scaffold New Structure
1. Create `src/cli/args.rs` with all new Args structs
2. Create `src/cli/global.rs` with GlobalArgs
3. Create `src/cli/handlers/` directory structure
4. Update `src/cli/mod.rs` with new Commands enum (keep old code commented)

### Phase 2: Implement Handlers (one at a time)
5. `handlers/encode.rs` - extract encode logic from run()
6. `handlers/decode.rs` - extract decode logic
7. `handlers/detect.rs` - wrap existing detect_mode()
8. `handlers/hash.rs` - extract hash logic
9. `handlers/config.rs` - adapt existing handle_config()
10. `handlers/neo.rs` - wrap existing matrix_mode()

### Phase 3: Wire Up Dispatch
11. Replace `run()` body with match dispatch
12. Remove old Cli struct and flag-based code

### Phase 4: Test Migration
13. Update CLI tests to use new syntax
14. Pattern: `["--encode", "base64"]` -> `["encode", "base64"]`
15. Pattern: `["config", "--dictionaries"]` -> `["config", "list", "dictionaries"]`
16. Run full test suite, fix edge cases

### Phase 5: Documentation
17. Update README examples
18. Update `--help` descriptions
19. Add CHANGELOG entry for v3.0.0

## Test Migration Examples

```rust
// Before
base_d().args(["--encode", "base64"]).write_stdin("hello")

// After
base_d().args(["encode", "base64"]).write_stdin("hello")

// Before
base_d().args(["config", "--dictionaries"])

// After
base_d().args(["config", "list", "dictionaries"])

// Before
base_d().args(["--detect", "--show-candidates", "3"])

// After
base_d().args(["detect", "--show-candidates", "3"])
```

## Implementation Order

Suggested order for Smith to implement:

1. **args.rs + global.rs** - Define the interface first
2. **Commands enum** - Wire up parsing
3. **handlers/config.rs** - Simplest, good test of pattern
4. **handlers/hash.rs** - Standalone, no encode/decode deps
5. **handlers/detect.rs** - Wraps existing function
6. **handlers/encode.rs** - Core functionality
7. **handlers/decode.rs** - Core functionality
8. **handlers/neo.rs** - Wraps existing matrix_mode()
9. **Test migration** - Batch update all 30 tests
10. **Cleanup** - Remove old code, update docs

## Consequences

**Positive:**
- Clear separation of concerns
- Each subcommand is independently testable
- Help output is organized by operation
- Adding new commands is trivial
- Reduced cognitive load in main dispatch

**Negative:**
- Breaking change requires major version bump
- Users must update scripts/aliases
- Slightly more typing for simple cases (`encode` vs `-e`)

**Mitigated by:**
- `visible_alias` provides short forms
- Clear migration guide in release notes
