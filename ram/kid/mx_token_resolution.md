# MX GitHub Token Path Resolution

## Summary
The mx CLI resolves the GitHub personal access token from `~/.claude.json` using the `dirs` crate's `home_dir()` function.

## Key Details

### Token Path Resolution
- **File:** `/home/w3surf/work/personal/code/mx/src/sync/github/auth.rs`
- **Function:** `claude_config_path()` (lines 31-35)
- **Resolution Method:** `dirs::home_dir()` - NOT hardcoded

```rust
fn claude_config_path() -> PathBuf {
    dirs::home_dir()
        .expect("Could not determine home directory")
        .join(".claude.json")
}
```

### Token Location in Config
The token is read from `~/.claude.json` at the path:
```
projects.<project>.mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN
```

### Crate Information
- **Crate:** `dirs` version 5 (from Cargo.toml line 40)
- The `dirs` crate is a cross-platform home directory resolver that uses OS-specific APIs:
  - **Linux/macOS:** Environment variable `HOME`
  - **Windows:** `USERPROFILE` or `HOMEDRIVE`/`HOMEPATH`

### Implementation Details
1. `dirs::home_dir()` is called in `claude_config_path()` function
2. If home directory cannot be determined, it panics with `expect()`
3. Then joins with `.claude.json` to create the full path
4. The `get_github_token()` function (lines 48-73) reads and parses the JSON
5. It searches through all projects for a github MCP server config

### No Hardcoding
The token path is **NOT hardcoded** - it uses proper home directory resolution via the `dirs` crate, which respects the user's actual home directory regardless of the user running the command.

## File Reference
- Full code: `/home/w3surf/work/personal/code/mx/src/sync/github/auth.rs`
