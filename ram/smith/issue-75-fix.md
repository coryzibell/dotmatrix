# Issue #75 Fix: Path Traversal Vulnerability

**Status:** Complete

**Vulnerability:** Path traversal in xxHash secret file loading allowed reading arbitrary files via config like:
```toml
[settings.xxhash]
default_secret_file = "../../../../etc/passwd"
```

## Changes Made

**File:** `/home/w3surf/work/personal/code/base-d/src/cli/config.rs`

1. Added import: `use std::path::PathBuf;`

2. Implemented `validate_config_path()` function (lines 6-28):
   - Expands tilde notation
   - Canonicalizes path (resolves symlinks, relative paths)
   - Validates path is within `~/.config/base-d/`
   - Returns clear error if path escapes allowed directory

3. Applied validation in `load_xxhash_config()` (lines 114-115):
   ```rust
   let validated_path = validate_config_path(path)?;
   Some(fs::read(validated_path)?)
   ```

## Attack Surface Reduced

**Before:** User config could read any file on system via path traversal
**After:** Only files within `~/.config/base-d/` (and subdirectories) can be loaded

## Verification

- `cargo check`: Passed (0.73s)
- No other instances of vulnerable pattern found in codebase
- Only location loading files from user-provided paths was the xxHash secret file

## Edge Cases Handled

1. Symlinks resolved via canonicalization
2. Relative paths normalized before validation
3. Tilde expansion occurs before validation
4. Clear error messages for invalid paths
5. File existence checked during canonicalization (returns error if nonexistent)
