# Issue #76: Input Size Limits Research

## Issue Description

**Title:** [BLOCKER] No input size limits - DoS possible

**Source:** Construct review via Cypher's security audit (`~/.matrix/cache/construct/base-d/security-audit.md`)

**Problem:**
No limits on input size. Malicious input could exhaust memory:
- Multi-gigabyte stdin input
- Huge file inputs
- Memory allocation attacks

**Impact:**
- Denial of service
- System instability
- Resource exhaustion

**Proposed Solution:**
Add configurable limits with:
- Default size limit (100MB suggested)
- `--max-size` flag to override
- Streaming mode for large files (no memory limit)
- Clear error message when limit exceeded

**Acceptance Criteria:**
- [ ] Default size limit (100MB suggested)
- [ ] `--max-size` flag to override
- [ ] Streaming mode for large files (no memory limit)
- [ ] Clear error message when limit exceeded

---

## Current Input Handling Code

### Entry Points - CLI Main (`src/cli/mod.rs`)

**Lines 314-324:** Main input reading (non-streaming mode)
```rust
// Read input data
let input_data = if let Some(file_path) = &cli.file {
    if cli.decode.is_some() {
        fs::read_to_string(file_path)?.into_bytes()
    } else {
        fs::read(file_path)?
    }
} else {
    let mut buffer = Vec::new();
    io::stdin().read_to_end(&mut buffer)?;
    buffer
};
```

**Issue:** Unbounded `read_to_end()` and `fs::read()` calls - will allocate whatever size the input is.

### Detect Mode (`src/cli/commands.rs`)

**Lines 305-311:** Detect mode input reading
```rust
// Read input
let input = if let Some(file_path) = file {
    fs::read_to_string(file_path)?
} else {
    let mut buffer = String::new();
    io::stdin().read_to_string(&mut buffer)?;
    buffer
};
```

**Issue:** Same - unbounded `read_to_string()` calls.

### Hash Secret Reading (`src/cli/config.rs`)

**Lines 109-118:** XXHash secret reading
```rust
let secret = if cli_hash_secret_stdin {
    let mut buf = Vec::new();
    io::stdin().read_to_end(&mut buf)?;
    Some(buf)
} else if let Some(ref path) = config.settings.xxhash.default_secret_file {
    let validated_path = validate_config_path(path)?;
    Some(fs::read(validated_path)?)
} else {
    None
};
```

**Issue:** Secret file has documented minimum (136 bytes for XXH3), but no maximum. Less critical since it's config-driven, but still vulnerable.

### Streaming Mode (Already Safe)

**Lines 369-426 (decode) and 428-480 (encode):** Streaming implementations use `StreamingDecoder` and `StreamingEncoder` which process in chunks. These are already memory-safe.

---

## Error Handling Infrastructure

### Current Error Type (`src/encoders/algorithms/math.rs`)

```rust
#[derive(Debug, PartialEq, Eq)]
pub enum DecodeError {
    /// The input contains a character not in the dictionary
    InvalidCharacter(char),
    /// The input string is empty
    EmptyInput,
    /// The padding is malformed or incorrect
    InvalidPadding,
}
```

**Location:** `src/encoders/algorithms/mod.rs` re-exports this as the public `DecodeError`.

**Need:** Add new variant for input size violations.

---

## Proposed Implementation Plan

### 1. Add Error Variant

**File:** `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/math.rs`

Add to `DecodeError` enum:
```rust
/// The input exceeds the maximum allowed size
InputTooLarge { size: usize, max: usize },
```

Update `Display` implementation to format this error.

### 2. Add CLI Flag

**File:** `/home/w3surf/work/personal/code/base-d/src/cli/mod.rs`

Add to `Cli` struct around line 68:
```rust
/// Maximum input size in bytes (default: 100MB, 0 = unlimited)
#[arg(long, default_value = "104857600", value_name = "BYTES")]
max_size: usize,
```

Or using Option for cleaner semantics:
```rust
/// Maximum input size in bytes (default: 100MB)
#[arg(long, value_name = "BYTES")]
max_size: Option<usize>,
```

### 3. Implement Size Checks

**File:** `/home/w3surf/work/personal/code/base-d/src/cli/mod.rs`

**Location 1 - Main input (after line 324):**
```rust
// Read input data
let input_data = if let Some(file_path) = &cli.file {
    if cli.decode.is_some() {
        fs::read_to_string(file_path)?.into_bytes()
    } else {
        fs::read(file_path)?
    }
} else {
    let mut buffer = Vec::new();
    io::stdin().read_to_end(&mut buffer)?;
    buffer
};

// NEW: Check size limit (skip if streaming or max_size is 0)
const DEFAULT_MAX_INPUT: usize = 100 * 1024 * 1024; // 100MB
let max_input_size = cli.max_size.unwrap_or(DEFAULT_MAX_INPUT);
if max_input_size > 0 && input_data.len() > max_input_size {
    return Err(format!(
        "Input size ({} bytes) exceeds maximum allowed size ({} bytes). Use --max-size to override or --stream for large files.",
        input_data.len(),
        max_input_size
    ).into());
}
```

**File:** `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs`

**Location 2 - Detect mode (after line 311):**
```rust
// Read input
let input = if let Some(file_path) = file {
    fs::read_to_string(file_path)?
} else {
    let mut buffer = String::new();
    io::stdin().read_to_string(&mut buffer)?;
    buffer
};

// NEW: Size check needed here too (pass max_size param to detect_mode)
```

### 4. Alternative: Safer Read Pattern

Instead of read-then-check, use a limited reader:
```rust
use std::io::Read;

fn read_with_limit<R: Read>(
    reader: &mut R,
    limit: usize
) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
    let mut buffer = Vec::new();
    let mut limited_reader = reader.take(limit as u64 + 1);
    limited_reader.read_to_end(&mut buffer)?;

    if buffer.len() > limit {
        return Err(format!(
            "Input size exceeds maximum of {} bytes",
            limit
        ).into());
    }

    Ok(buffer)
}
```

This prevents allocating the full malicious input before checking.

---

## Locations Requiring Changes

### Primary Changes (Required)

1. **`/home/w3surf/work/personal/code/base-d/src/cli/mod.rs`**
   - Add `--max-size` CLI flag (around line 68)
   - Add size check after line 324 (main input reading)
   - Pass max_size to detect_mode call (line 206-211)

2. **`/home/w3surf/work/personal/code/base-d/src/cli/commands.rs`**
   - Update `detect_mode()` signature to accept max_size parameter
   - Add size check after line 311 (detect mode input reading)

3. **`/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/math.rs`**
   - Add `InputTooLarge` variant to `DecodeError` enum
   - Update `Display` implementation

### Secondary/Optional Changes

4. **`/home/w3surf/work/personal/code/base-d/src/cli/config.rs`**
   - Consider limit on hash secret file size (currently unbounded)
   - Less critical since it's config-driven, not user input

---

## Testing Considerations

1. **Normal operation:** Ensure files under 100MB work normally
2. **Over limit:** Test that >100MB input is rejected with clear error
3. **Custom limit:** Test `--max-size` flag overrides default
4. **Unlimited:** Test `--max-size 0` disables limit
5. **Streaming bypass:** Verify `--stream` mode bypasses size limits (as it should)
6. **Error message:** Verify error message suggests using `--stream` for large files

---

## Streaming Mode Notes

The streaming implementations (`streaming_encode` and `streaming_decode`) are **already safe**:
- They use `StreamingEncoder` and `StreamingDecoder` from the library
- Process input in chunks
- No need to limit streaming mode - it's the recommended approach for large files

The issue is **only with non-streaming modes** that use `fs::read()`, `read_to_end()`, and `read_to_string()`.

---

## Summary for Implementation

**What limits are needed:**
- Default 100MB limit on non-streaming input
- Configurable via `--max-size` flag
- Set to 0 for unlimited (risky but may be needed)

**Where checks should go:**
1. Main CLI input reading (mod.rs line ~324) - after reading, before processing
2. Detect mode input reading (commands.rs line ~311) - same pattern
3. Optionally: Hash secret reading (config.rs line ~111) - less critical

**What error should be returned:**
- Option 1: Add `InputTooLarge { size, max }` to `DecodeError` enum
- Option 2: Use `Box<dyn std::error::Error>` with formatted string (simpler, already used in CLI)

**Preferred approach:** Use existing `Box<dyn std::error::Error>` pattern in CLI code, add proper error variant to library if needed for API consumers.
