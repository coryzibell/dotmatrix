## Fix path traversal vulnerability in config handling

**Type:** `issue`
**Labels:** `identity:smith`, `blocker`, `security`

### Context

From Construct review of `base-d` project. Cypher identified path traversal vulnerability.

**Source:** `~/.matrix/cache/construct/base-d/security-findings.md`

### Problem

`src/cli/config.rs:89` uses `shellexpand::tilde()` without validating the resolved path:

```rust
Some(fs::read(shellexpand::tilde(path).as_ref())?)
```

User-controlled config can specify paths like `~/../../../etc/shadow` to read arbitrary files.

**Attack vector:**
1. User creates malicious `~/.config/base-d/dictionaries.toml`
2. Sets `default_secret_file = "~/../../../etc/shadow"`
3. Runs `base-d --hash xxh3-64 <data>`
4. Tool reads `/etc/shadow` as xxHash secret

### Solution

Canonicalize paths and validate they stay within allowed directories.

```rust
let expanded = shellexpand::tilde(path);
let canonical = fs::canonicalize(expanded.as_ref())?;
if !canonical.starts_with(config_dir) {
    return Err("Secret file path outside allowed directory".into());
}
```

### Implementation Steps

1. Add path validation function in `src/cli/config.rs`
2. Restrict secret file paths to `~/.config/base-d/` directory
3. Return clear error for paths outside allowed directory
4. Add tests for path traversal attempts

### Acceptance Criteria

- [ ] Paths outside config directory are rejected
- [ ] Clear error message for invalid paths
- [ ] Tests cover traversal attempts (`../`, absolute paths)
- [ ] Cypher re-audits after fix

### Handoff

After Smith implements → Deus verifies → Cypher re-audits → Neo merges
