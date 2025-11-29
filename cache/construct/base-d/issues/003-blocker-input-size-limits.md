## Add input size limits to prevent memory exhaustion

**Type:** `issue`
**Labels:** `identity:smith`, `blocker`, `security`

### Context

From Construct review of `base-d` project. Cypher identified DoS vulnerability.

**Source:** `~/.matrix/cache/construct/base-d/security-findings.md`

### Problem

`src/cli/mod.rs:289-298` reads entire files/stdin into memory without size limits:

```rust
let input_data = if let Some(file_path) = &cli.file {
    fs::read(file_path)?  // Unbounded
} else {
    let mut buffer = Vec::new();
    io::stdin().read_to_end(&mut buffer)?;  // Unbounded
    buffer
};
```

**Attack:** `cat /dev/zero | head -c 10G | base-d -e base64` causes OOM.

### Solution

Implement configurable max input size with helpful error message.

```rust
const MAX_INPUT_SIZE: u64 = 100 * 1024 * 1024; // 100MB default

if let Some(file_path) = &cli.file {
    let metadata = fs::metadata(file_path)?;
    if metadata.len() > MAX_INPUT_SIZE {
        return Err("Input file too large, use --stream mode".into());
    }
}
```

### Implementation Steps

1. Add `--max-size` flag (default 100MB)
2. Check file size before reading
3. For stdin, read in chunks and count bytes
4. Return clear error suggesting `--stream` mode
5. Add config option for default max size

### Acceptance Criteria

- [ ] Files over limit are rejected with clear message
- [ ] Stdin over limit is rejected
- [ ] `--max-size` flag works
- [ ] Error message suggests `--stream` alternative
- [ ] Tests cover size limit enforcement

### Handoff

After Smith implements → Deus verifies → Neo merges
