# Base-d Custom Dictionary/Alphabet Options - Research Report

## Summary
Base-d supports custom dictionaries at **runtime via configuration files** (no compile-time customization needed). There is **NO direct CLI flag for custom alphabet strings**, but you can define them in TOML and reference by name.

---

## CLI Options Available

### 1. Encode/Decode with Named Dictionary
- **Flags:** `-e <name>`, `--encode <name>`, `-d <name>`, `--decode <name>`
- **Type:** Reference by dictionary name
- **Runtime:** Yes - dictionaries are loaded from config at runtime
- **Example:** `base-d --encode base64 input.txt`

### 2. Random Dictionary Selection
- **Flag:** `--dejavu`
- **Behavior:** Randomly selects from dictionaries marked `common=true`
- **Note:** Can combine with compression, hashing, etc.
- **Example:** `base-d --dejavu input.txt`

### 3. Query Available Dictionaries
- **Command:** `base-d config --dictionaries`
- **Format:** Comma-separated list
- **JSON mode:** `base-d config --json` (includes all options)

### No Direct Alphabet String Support
- There is **NO** `--alphabet` or `--dictionary-string` flag
- You **cannot** pass a custom alphabet directly via CLI
- You **must** define dictionaries in TOML files instead

---

## Configuration: How Dictionaries Are Loaded

### Load Priority (from `DictionaryRegistry::load_with_overrides()`)
1. **Built-in dictionaries** - embedded in binary from `src/dictionaries.toml`
2. **User config** - `~/.config/base-d/dictionaries.toml` (overrides #1)
3. **Project local** - `./dictionaries.toml` (overrides #1 & #2)

### Key Methods
- `load_default()` - Built-in dictionaries only
- `load_from_file(path)` - Load specific file
- `load_with_overrides()` - Used by CLI, applies full hierarchy
- `merge()` - Later configs override earlier ones by name

---

## Dictionary Definition Format (TOML)

### Basic Structure
```toml
[dictionaries.my_custom]
chars = "ABC123!@#"           # Explicit character list
mode = "base_conversion"       # Or "chunked" or "byte_range"
padding = "="                  # Optional (for chunked mode)
common = true                  # Include in --dejavu selection (default: true)
```

### Three Definition Methods

#### 1. Explicit Characters (Most Common)
```toml
[dictionaries.custom_hex]
chars = "0123456789abcdef"
mode = "base_conversion"
```

#### 2. Range-Based (Sequential Unicode)
```toml
[dictionaries.range_example]
start = "A"                    # First character
length = 26                    # How many sequential chars
mode = "base_conversion"
```

#### 3. ByteRange Mode (256 consecutive Unicode chars)
```toml
[dictionaries.base100]
mode = "byte_range"
start_codepoint = 127991      # U+1F3F7 - starting codepoint
```

### Encoding Modes
- **base_conversion** (default) - True radix: supports any alphabet size
- **chunked** - Fixed bit chunks (RFC 4648 style): requires power-of-2 size
- **byte_range** - Direct byte→char mapping: always 256 chars, zero overhead

---

## How to Use Custom Dictionaries at Runtime

### Option A: User Config (Persistent)
1. Create `~/.config/base-d/dictionaries.toml`
2. Add your custom dictionaries
3. Use immediately: `base-d --encode my_custom data.txt`

### Option B: Project Local (Per-Directory)
1. Create `./dictionaries.toml` in your working directory
2. Add custom dictionaries
3. Use when in that directory: `base-d --encode my_custom data.txt`
4. Local config overrides user config

### Option C: Override Existing by Name
```toml
# In ~/.config/base-d/dictionaries.toml
[dictionaries.base64]
chars = "CUSTOMCHARS..."      # Replaces built-in base64
```

---

## Example Custom Dictionary Scenarios

### Scenario 1: Custom Emoji Alphabet
```toml
[dictionaries.fun_emojis]
chars = "😀😁😂🤣😃😄😅😆😉😊😋😎😍😘🥰😗"
mode = "base_conversion"
```

Usage: `echo "hello" | base-d --encode fun_emojis`

### Scenario 2: Domain-Specific Alphabet
```toml
[dictionaries.dna]
chars = "ACGT"
mode = "base_conversion"

[dictionaries.proteins]
chars = "ACDEFGHIKLMNPQRSTVWY"
mode = "base_conversion"
```

Usage: `base-d --encode dna genome.bin`

### Scenario 3: Large Unicode Range (Chinese Characters)
```toml
[dictionaries.cjk_subset]
start = "中"                   # U+4E2D
length = 256
mode = "base_conversion"
```

### Scenario 4: ByteRange Mode (No Overhead)
```toml
[dictionaries.custom_256]
mode = "byte_range"
start_codepoint = 0xE000      # Private use area
```

---

## Compile-Time Dictionary Options

### Fixed at Build Time
- **Embedded TOML:** `src/dictionaries.toml` (included via `include_str!()`)
- **To add compile-time dicts:** Edit source TOML → rebuild binary
- **No conditional compilation flags** for dictionaries

### Not Recommended at Compile-Time
- Adding dictionaries requires code changes + rebuild
- Runtime config files are more flexible and practical

---

## Key Findings

| Aspect | Details |
|--------|---------|
| **Direct Alphabet String Flag** | ❌ Does not exist |
| **Named Dictionary Selection** | ✅ `-e/-d <name>` |
| **Custom Dictionary Support** | ✅ TOML config files |
| **Runtime Customization** | ✅ Via `~/.config/base-d/` or local `dictionaries.toml` |
| **Compile-Time Customization** | ⚠️ Possible but requires source edit + rebuild |
| **Dictionary Override** | ✅ Later configs override by name |
| **Random Dictionary** | ✅ `--dejavu` flag (common dicts only) |
| **Mode Auto-Detection** | ✅ Based on alphabet size (power-of-2 → chunked) |

---

## CLI Examples

```bash
# Use built-in base64
base-d --encode base64 file.bin

# Use custom dictionary from config
base-d --encode my_emoji file.bin

# Random dictionary (marked common=true)
base-d --dejavu file.bin

# List all available
base-d config --dictionaries

# Show full config as JSON
base-d config --json

# Decode and auto-detect dictionary
base-d --detect --show-candidates 5 encoded.txt

# Streaming mode with custom dict
base-d --stream --encode my_custom input.bin
```

---

## Code References

### Key Files
- **CLI args:** `src/cli/mod.rs` (lines 20-26: `--encode`/`--decode`)
- **Dictionary loading:** `src/core/config.rs` (lines 230-268: `load_with_overrides()`)
- **Config structure:** `src/core/config.rs` (lines 28-53: `DictionaryConfig`)
- **Config helper:** `src/cli/config.rs` (lines 31-75: `create_dictionary()`)
- **Validation:** `src/cli/config.rs` (lines 10-28: path safety checks)

### Load Hierarchy Implementation
```rust
// From src/core/config.rs::load_with_overrides()
1. Load built-in (include_str!("../../dictionaries.toml"))
2. If ~/.config/base-d/dictionaries.toml exists → merge
3. If ./dictionaries.toml exists → merge (highest priority)
4. Return merged config
```

---

## Recommendations for kautau

1. **For quick testing:** Use local `./dictionaries.toml` - no installation needed
2. **For persistent custom dicts:** Place in `~/.config/base-d/dictionaries.toml`
3. **For complex alphabets:** Use range-based definition (`start` + `length`)
4. **For zero-overhead encoding:** Use `mode = "byte_range"` with 256-char ranges
5. **For random selection:** Mark custom dicts with `common = true` (default)

---

## Caveats

- Custom alphabets **cannot be passed as CLI strings** - must use TOML files
- `--alphabet` or `--custom` flags don't exist
- Path traversal is blocked for security (only `~/.config/base-d/` allowed via CLI validation)
- ByteRange mode is always exactly 256 characters (no flexibility)

