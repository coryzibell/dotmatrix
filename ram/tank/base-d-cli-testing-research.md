# base-d CLI Testing Research

**Issue**: #79 - Add CLI test coverage
**Location**: https://github.com/coryzibell/base-d
**Date**: 2025-11-29

## Issue Requirements

From Construct/Deus quality review:

### Critical Gap
The CLI layer has zero test coverage despite being the primary user interface.

### Untested Functions
- `parse_interval()` - time parsing ("5s", "500ms", "line")
- `select_random_dictionary()` - random selection from common dictionaries
- File I/O operations
- Configuration loading
- Error handling paths

### Acceptance Criteria
- `parse_interval()` fully tested (4 tests: valid, invalid, edge cases)
- Random selection tested (3 tests)
- File operations tested (4 tests)
- Config loading tested
- Integration tests for common workflows
- Target: 20-30 CLI tests total
- Coverage report shows CLI module improvement

## Current Test State

### Existing Test Infrastructure
- **Shell script**: `/home/w3surf/work/personal/code/base-d/test_cli.sh`
  - 8 basic smoke tests (help, list, encode/decode, file I/O, binary data)
  - Uses bash assertions, not integrated with Cargo
  - No coverage tracking

### Missing Infrastructure
- No `tests/` directory
- No integration tests in Rust
- No `assert_cmd` in dev-dependencies
- No unit tests for CLI module functions

## CLI Structure Analysis

### Main Entry Point
**File**: `/home/w3surf/work/personal/code/base-d/src/cli/mod.rs` (530 lines)

### Key Functions to Test

1. **`parse_interval()`** (line 23)
   - Input: String like "5s", "500ms", "3m", "line"
   - Output: `Result<SwitchInterval, Box<dyn std::error::Error>>`
   - Edge cases:
     - Valid: "5s", "500ms", "3m", "line"
     - Invalid: empty string, no unit, unknown unit, negative numbers
     - Boundary: "0s", very large numbers

2. **`select_random_dictionary()`** (line 54)
   - Input: `DictionaryRegistry`, `bool` (print_message flag)
   - Output: `Result<String, Box<dyn std::error::Error>>`
   - Only selects from `common=true` dictionaries
   - Tests needed:
     - Returns valid dictionary name
     - Only returns common dictionaries
     - Handles empty registry
     - Print message flag (currently unused but reserved)

3. **`should_disable_color()`** (line 137)
   - Tests: cli flag, NO_COLOR env var, both, neither

4. **`contains_control_chars()`** (line 145)
   - Tests: valid strings, control chars, tabs/newlines (allowed)

5. **`output_encoded()`** (line 151)
   - Tests: valid output, control char detection, error formatting

### CLI Commands to Test

**Main flags** (from `--help`):
- `-e, --encode <ENCODE>` - Encode using dictionary
- `-d, --decode <DECODE>` - Decode from dictionary
- `-c, --compress [<ALGORITHM>]` - Compress before encoding (optional random)
- `--decompress <DECOMPRESS>` - Decompress after decoding
- `--level <LEVEL>` - Compression level
- `--hash [<ALGORITHM>]` - Compute hash (optional random)
- `--hash-seed <HASH_SEED>` - xxHash seed
- `--hash-secret-stdin` - Read XXH3 secret from stdin
- `-r, --raw` - Output raw binary
- `--detect` - Auto-detect dictionary
- `--show-candidates <N>` - Show top N candidates with detect
- `-l, --list` - List available dictionaries
- `-s, --stream` - Streaming mode
- `--neo [<DICTIONARY>]` - Matrix mode
- `--dejavu` - Random dictionary encoding
- `--cycle` - Cycle through dictionaries (requires --neo --dejavu)
- `--random` - Random dictionary switching (requires --neo --dejavu)
- `--interval <INTERVAL>` - Switch interval
- `--max-size <BYTES>` - Max input size (default 100MB)
- `--force` - Process files exceeding max-size
- `--no-color` - Disable colored output

**Subcommands**:
- `config --compression` - List compression algorithms
- `config --dictionaries` - List dictionaries
- `config --hash` - List hash algorithms
- `config --json` - JSON output

## assert_cmd Crate

### Installation
```toml
[dev-dependencies]
assert_cmd = "2.0"
predicates = "3.0"  # For flexible matching
assert_fs = "1.0"   # For temp files
```

### Basic Usage Pattern
```rust
use assert_cmd::Command;

#[test]
fn test_help() {
    Command::cargo_bin("base-d")
        .unwrap()
        .arg("--help")
        .assert()
        .success();
}

#[test]
fn test_encode_decode() {
    Command::cargo_bin("base-d")
        .unwrap()
        .arg("--encode")
        .arg("cards")
        .write_stdin("Hello")
        .assert()
        .success()
        .stdout(predicates::str::contains("Hello"));
}
```

### Advanced Features
- **stdin**: `.write_stdin("data")`
- **assertions**: `.success()`, `.failure()`, `.code(42)`
- **output**: `.stdout("exact match")`, `.stderr("")`
- **predicates**: `predicates::str::contains()`, `is_match()` (regex)
- **raw output**: `.get_output().clone()` for custom checks

### Related Crates
- `assert_fs` - Temporary file/directory creation for testing
- `predicates` - Flexible output matching (regex, contains, etc.)
- `escargot` - More control over binary configuration

## Recommended Test Structure

### Unit Tests (in `src/cli/mod.rs` and `src/cli/commands.rs`)

Add `#[cfg(test)]` modules at end of each file:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_interval_seconds() {
        let result = parse_interval("5s").unwrap();
        match result {
            SwitchInterval::Time(d) => assert_eq!(d.as_secs(), 5),
            _ => panic!("Expected Time variant"),
        }
    }

    #[test]
    fn test_parse_interval_line() {
        let result = parse_interval("line").unwrap();
        assert!(matches!(result, SwitchInterval::PerLine));
    }

    #[test]
    fn test_parse_interval_invalid() {
        assert!(parse_interval("").is_err());
        assert!(parse_interval("5").is_err());
        assert!(parse_interval("5x").is_err());
    }

    // ... more unit tests
}
```

### Integration Tests (in `tests/cli_integration.rs`)

```rust
use assert_cmd::Command;
use assert_fs::prelude::*;
use predicates::prelude::*;

#[test]
fn help_displays() {
    Command::cargo_bin("base-d")
        .unwrap()
        .arg("--help")
        .assert()
        .success()
        .stdout(predicate::str::contains("Universal multi-dictionary encoder"));
}

#[test]
fn encode_decode_roundtrip() {
    let mut cmd = Command::cargo_bin("base-d").unwrap();
    let encoded = cmd
        .arg("--encode")
        .arg("cards")
        .write_stdin("Test data")
        .assert()
        .success()
        .get_output()
        .stdout
        .clone();

    Command::cargo_bin("base-d")
        .unwrap()
        .arg("--decode")
        .arg("cards")
        .write_stdin(String::from_utf8(encoded).unwrap())
        .assert()
        .success()
        .stdout("Test data");
}

#[test]
fn file_input_output() {
    let temp = assert_fs::TempDir::new().unwrap();
    let input_file = temp.child("input.txt");
    input_file.write_str("File content").unwrap();

    Command::cargo_bin("base-d")
        .unwrap()
        .arg("--encode")
        .arg("binary")
        .arg(input_file.path())
        .assert()
        .success()
        .stdout(predicate::str::is_empty().not());
}

// ... more integration tests
```

## Test Coverage Plan

### Unit Tests (11 tests)
1. `parse_interval()` - 6 tests
   - Valid: "5s", "500ms", "3m", "line"
   - Invalid: empty, no unit, unknown unit
   - Edge: "0s"
2. `select_random_dictionary()` - 2 tests
   - Returns common dictionary
   - Non-empty result
3. `should_disable_color()` - 2 tests
   - CLI flag true
   - NO_COLOR env var set
4. `contains_control_chars()` - 1 test
   - Valid vs invalid chars

### Integration Tests (15-20 tests)
1. **Basic commands** (4 tests)
   - `--help` succeeds
   - `--version` succeeds
   - `--list` shows dictionaries
   - `config --json` outputs JSON
2. **Encode/decode workflows** (5 tests)
   - Round-trip with default dictionary
   - Round-trip with specified dictionary
   - Binary data preservation
   - File input
   - Stdin input
3. **Compression** (3 tests)
   - Compress + encode
   - Decode + decompress
   - Random compression flag
4. **Error handling** (4 tests)
   - Invalid dictionary name
   - File not found
   - Conflicting flags
   - Max size exceeded
5. **Advanced features** (4 tests)
   - `--detect` mode
   - `--dejavu` random encoding
   - `--hash` computation
   - `--streaming` mode

**Total**: 26-31 tests (meets target of 20-30)

## Sources
- [Testing - Command Line Applications in Rust](https://rust-cli.github.io/book/tutorial/testing.html)
- [assert_cmd - crates.io](https://crates.io/crates/assert_cmd)
- [How I test Rust command-line apps with assert_cmd](https://alexwlchan.net/2025/testing-rust-cli-apps-with-assert-cmd/)
- [assert_cmd - Rust docs](https://docs.rs/assert_cmd)
- [GitHub - assert-rs/assert_cmd](https://github.com/assert-rs/assert_cmd)

## Next Steps (for implementation)

1. Add dev-dependencies to Cargo.toml
2. Create `tests/` directory structure
3. Add unit tests to `src/cli/mod.rs` and `src/cli/commands.rs`
4. Create integration tests in `tests/cli_integration.rs`
5. Run `cargo test` to verify
6. Run `cargo tarpaulin` or `cargo llvm-cov` for coverage report
7. Update CI to enforce coverage thresholds
