# Data Review: base-d

**Repository:** `/home/w3surf/work/personal/code/base-d`
**Reviewed:** 2025-11-28
**Librarian Analysis**

---

## Executive Summary

**No database usage detected.** This is a pure CLI encoding tool with file-based configuration. All data operations are stateless transformations.

---

## Data Architecture

### Data Flow Pattern

```
Input (stdin/file) → [Optional: Compression/Hash] → Encoding → Output (stdout/file)
                                                        ↓
                                               Dictionary (in-memory)
                                                        ↑
                                               TOML Config (file-based)
```

**Type:** Stateless stream processor
**Persistence:** Configuration only (TOML files)
**State Management:** None - each invocation is independent

---

## Configuration Management

### Storage Locations (Priority Order)

1. **Built-in dictionaries** - Compiled into binary (`include_str!("../../dictionaries.toml")`)
2. **User config** - `~/.config/base-d/dictionaries.toml`
3. **Local config** - `./dictionaries.toml`

**Strategy:** Hierarchical override system. Later configs override earlier ones for matching dictionary names.

**Implementation:** `/home/w3surf/work/personal/code/base-d/src/core/config.rs:115-153`

```rust
pub fn load_with_overrides() -> Result<Self, Box<dyn std::error::Error>> {
    let mut config = Self::load_default()?;
    // Load user config, then local config, merging each
    config.merge(user_config);
    config.merge(local_config);
    Ok(config)
}
```

### Configuration Schema

**File Format:** TOML
**Primary Structure:** `DictionaryRegistry`

```rust
pub struct DictionaryRegistry {
    pub dictionaries: HashMap<String, DictionaryConfig>,
    pub compression: HashMap<String, CompressionConfig>,
    pub settings: Settings,
}
```

**Key Entities:**

- **DictionaryConfig** - Character sets, encoding mode, padding, Unicode ranges
- **CompressionConfig** - Default compression levels per algorithm
- **Settings** - Global defaults (default dictionary, xxHash seed/secret paths)

---

## Data Structures

### Runtime Data Model

**Core Structure:** `Dictionary` (`/home/w3surf/work/personal/code/base-d/src/core/dictionary.rs`)

```rust
pub struct Dictionary {
    chars: Vec<char>,                                    // Character set
    char_to_index: HashMap<char, usize>,                 // Decode lookup
    lookup_table: Option<Box<[Option<usize>; 256]>>,    // Fast ASCII lookup
    mode: EncodingMode,                                  // Encoding strategy
    padding: Option<char>,                               // Optional padding
    start_codepoint: Option<u32>,                        // For ByteRange mode
}
```

**Design Characteristics:**

1. **Dual lookup strategy** - Fast array lookup for ASCII (< 256), HashMap fallback for Unicode
2. **Immutable after construction** - Dictionary validation happens at creation time
3. **Zero persistence** - Exists only in process memory

### Encoding Modes

Three distinct strategies (no database implications):

1. **BaseConversion** - Mathematical base conversion (arbitrary base size)
2. **Chunked** - RFC 4648-style bit chunking (requires power-of-two base)
3. **ByteRange** - Direct byte-to-Unicode mapping (always 256 chars)

---

## Data Validation

### Schema Constraints

**Enforced at Dictionary creation** (`dictionary.rs:33-206`):

- **Uniqueness** - No duplicate characters in dictionary
- **Non-empty** - Dictionary must contain at least one character
- **Power-of-two** - Chunked mode requires 2/4/8/16/32/64/128/256 chars
- **Character safety** - No control chars (except \t, \n, \r), no whitespace
- **Padding uniqueness** - Padding char cannot be in dictionary
- **Unicode validity** - ByteRange mode validates all 256 codepoints

**Error handling:** Immediate validation with descriptive error messages. No partial states.

---

## File I/O Patterns

### Configuration Loading

**Read-only operations:**

- `fs::read_to_string()` for TOML files
- `include_str!()` for embedded default config
- `shellexpand::tilde()` for path resolution

**No write operations to config files.** Configuration is read-only at runtime.

### Data Processing

**Streaming model:**

- `std::io::stdin().read_to_end()` or file read
- In-memory transformation
- `std::io::stdout().write_all()` or file write

**Optional streaming mode** (`-s` flag) for large files - processes data in chunks without loading entire file.

---

## Caching & Performance

### In-Memory Optimization

**ASCII Lookup Table** (`dictionary.rs:184-196`):

```rust
let lookup_table = if chars.iter().all(|&c| (c as u32) < 256) {
    let mut table = Box::new([None; 256]);
    for (i, &c) in chars.iter().enumerate() {
        table[c as usize] = Some(i);
    }
    Some(table)
} else {
    None
};
```

**Strategy:** O(1) array lookup for ASCII dictionaries, O(log n) HashMap for Unicode.

**No persistent caching.** Each process invocation rebuilds lookup tables from config.

---

## Potential Database Concerns

### None Identified

After comprehensive review:

- **No database dependencies** in `Cargo.toml` (no sqlite, postgres, redis, etc.)
- **No SQL files** in repository
- **No persistence layer** - all state is ephemeral
- **No cache persistence** - lookup tables rebuilt per-invocation
- **No user data storage** - tool processes data, doesn't retain it

**False positives from grep:**

- "load/store" references in SIMD code are CPU instructions, not persistence
- "database" never appears in source code

---

## Data Integrity

### Validation Mechanisms

**Configuration:**

- TOML parsing with serde (type-safe deserialization)
- Dictionary validation at construction time
- Clear error messages with Unicode codepoint details

**Runtime:**

- No mutable state after dictionary creation
- Encode/decode operations are pure functions
- Optional hash verification (--hash flag) for data integrity checks

**No transactional requirements** - no multi-step operations requiring rollback.

---

## Security Considerations

### Configuration Security

**Potential concern:** XXHash secret file loading

```rust
// From cli/config.rs:88-89
} else if let Some(ref path) = config.settings.xxhash.default_secret_file {
    Some(fs::read(shellexpand::tilde(path).as_ref())?)
}
```

**Risk:** Path traversal via user config file
**Mitigation:** User controls their own config files - this is expected behavior
**No database injection risks** - no query construction, no SQL

### Data Handling

- **No plaintext password storage** (not a credential manager)
- **No PII collection** (doesn't track user data)
- **No external API calls** (pure local processing)

---

## Recommendations

### Current State: Appropriate

This tool's architecture is **correct for its purpose**:

1. **Stateless design** - CLI tools should be stateless transformers
2. **File-based config** - Standard pattern for CLI tool configuration
3. **No database needed** - No relationships, queries, or persistent state required

### If Persistence Needed (Future)

Scenarios that might require a database:

1. **Dictionary version history** - Track custom dictionary evolution
2. **Usage analytics** - Log encoding operations for analysis
3. **Shared dictionaries** - Multi-user dictionary repository
4. **Cached results** - Store expensive encoding computations

**Recommendation:** SQLite for local persistence (if needed)
- `~/.config/base-d/cache.db` for encoding cache
- `~/.config/base-d/history.db` for operation history
- Embedded schema versioning with migrations

**Not recommended:** Remote database (postgres/mysql) - unnecessary complexity for a CLI tool.

### Schema Design Notes

If adding dictionary versioning:

```sql
-- Hypothetical schema (not implemented)
CREATE TABLE dictionary_versions (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    version INTEGER NOT NULL,
    chars TEXT NOT NULL,
    mode TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    UNIQUE(name, version)
);

CREATE INDEX idx_dict_name ON dictionary_versions(name);
```

**Normalization:** Not critical - dictionary configs are small, read-heavy workloads.

---

## Files Reviewed

**Configuration:**
- `/home/w3surf/work/personal/code/base-d/src/core/config.rs` - Config schema and loading
- `/home/w3surf/work/personal/code/base-d/src/cli/config.rs` - CLI config helpers
- `/home/w3surf/work/personal/code/base-d/dictionaries.toml` - Default dictionaries

**Core Data Structures:**
- `/home/w3surf/work/personal/code/base-d/src/core/dictionary.rs` - Dictionary implementation
- `/home/w3surf/work/personal/code/base-d/Cargo.toml` - Dependency verification

**CLI Entry:**
- `/home/w3surf/work/personal/code/base-d/src/main.rs` - Program entry
- `/home/w3surf/work/personal/code/base-d/src/cli/mod.rs` - CLI argument parsing

---

## Conclusion

**Status:** ✓ No database concerns
**Pattern:** File-based configuration with in-memory processing
**Recommendation:** Current architecture is appropriate - no database required

This tool correctly avoids database complexity. It's a stateless transformer, as CLI encoding tools should be. Configuration via TOML files is the right choice for this use case.

If future requirements demand persistence (usage tracking, dictionary versioning, encoding cache), SQLite would be the appropriate choice - but current design needs no changes.

---

**Knock knock, Neo.**
