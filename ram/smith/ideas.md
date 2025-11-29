# Smith's Work Log

## Issue #83: Random Selection Warnings (2025-11-29)

**Implemented warning system for random algorithm selection in base-d.**

Changes:
1. Added `--quiet` flag to Cli struct (`/home/w3surf/work/personal/code/base-d/src/cli/mod.rs:114-115`)
2. Updated `select_random_compress()` to accept `quiet: bool` param, emits warning to stderr
3. Updated `select_random_hash()` to accept `quiet: bool` param, emits warning to stderr
4. Updated `select_random_dictionary()` to use `print_message` flag for warning
5. Threaded `cli.quiet` through all call sites in `mod.rs` (lines 282, 303, 308, 401)

Warning format:
```
Note: Using randomly selected <type> '<name>' (use --<flag>=<name> to fix)
```

Examples:
- `Note: Using randomly selected compression 'gzip' (use --compress=gzip to fix)`
- `Note: Using randomly selected hash 'xxh3' (use --hash=xxh3 to fix)`
- `Note: Using randomly selected dictionary 'base32hex' (use --encode=base32hex to fix)`

Tested: All warnings emit correctly, `--quiet` suppresses as expected.

Build: Clean compilation, no errors.
