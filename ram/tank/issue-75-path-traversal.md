# Issue #75 Path Traversal Research

**Status:** BLOCKER
**Reporter:** Cypher (via Construct security audit)
**Date:** 2025-11-29

## Issue Description

Custom alphabet/dictionary file paths aren't sanitized. User input like `--alphabet ../../../etc/passwd` (or via config file) could read arbitrary files.

From issue body:
> Custom alphabet file paths aren't sanitized. User input like `--alphabet ../../../etc/passwd` could read arbitrary files.

## Affected Files & Functions

### Primary Vulnerability: `/home/w3surf/work/personal/code/base-d/src/cli/config.rs`

**Function:** `load_xxhash_config` (lines 67-114)

**Vulnerable Code (line 88-89):**
```rust
} else if let Some(ref path) = config.settings.xxhash.default_secret_file {
    Some(fs::read(shellexpand::tilde(path).as_ref())?)
```

### Attack Vector

The vulnerability is in the xxHash secret file loading mechanism:

1. **Config file path** (`~/.config/base-d/dictionaries.toml` or `./dictionaries.toml`)
2. **TOML setting:** `settings.xxhash.default_secret_file = "../../../etc/passwd"`
3. **Execution:** Any command using xxHash3 will read the arbitrary file
4. **File read:** Line 89 calls `fs::read()` directly on the user-controlled path

### Attack Demonstration

**Step 1:** Create malicious config file at `~/.config/base-d/dictionaries.toml`:
```toml
[settings.xxhash]
default_secret_file = "../../../etc/passwd"
```

**Step 2:** Run base-d with xxHash3:
```bash
echo "test" | base-d --hash xxh3-64
```

**Step 3:** The `fs::read()` call will read `/etc/passwd` instead of a legitimate secret file

### Technical Details

**How it works:**

1. User creates a malicious config file with path traversal in `default_secret_file`
2. `DictionaryRegistry::load_with_overrides()` loads the malicious config (line 123-160 in `/home/w3surf/work/personal/code/base-d/src/core/config.rs`)
3. When xxHash3 is invoked, `load_xxhash_config()` is called
4. Line 88-89 reads from the unsanitized path using `fs::read()`
5. `shellexpand::tilde()` only expands `~`, it does NOT prevent path traversal
6. File contents are loaded as the xxHash secret (must be ≥136 bytes for XXH3)

**Exploitation requirements:**
- Target file must be ≥136 bytes (XXH3 secret requirement)
- Or use `--hash-secret-stdin` which has no path validation

**Information disclosure:**
- Reading sensitive files (`/etc/passwd`, config files, private keys, etc.)
- File contents become part of the hashing secret
- Error messages may leak file existence/readability

## Impact

- **Information Disclosure:** Critical
- **Reading Sensitive Files:** Yes - any file readable by the user running base-d
- **Directory Allowlist:** None - no path validation whatsoever
- **Canonicalization:** None - only tilde expansion

## Solution Required

From issue #75 acceptance criteria:

1. **Path canonicalization** before file access
2. **Directory allowlist validation**
3. **Clear error message** for blocked paths
4. **Unit tests** for traversal attempts

### Recommended Fix (from issue):

```rust
let canonical = path.canonicalize()?;
if !canonical.starts_with(&allowed_base) {
    return Err(Error::PathTraversal);
}
```

### Allowed Base Directory

Suggestions:
- `~/.config/base-d/secrets/` for user secrets
- `./secrets/` for project-local secrets
- Reject absolute paths outside these directories
- Reject any `..` in the path

## Notes

- **Current sanitization:** Only `shellexpand::tilde()` which expands `~` but allows `../`
- **Attack complexity:** Low - just create a TOML file
- **Privilege required:** None - user can write to `~/.config/`
- **Detection difficulty:** Hard - silent file read, no obvious indicators

## Handoff

Per issue #75:
> Cypher identifies → Smith implements → Cypher verifies → Neo merges

**Next:** Smith to implement path sanitization with allowlist validation
