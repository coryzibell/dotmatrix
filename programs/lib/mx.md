# mx - Matrix CLI

Rust CLI for Matrix workflows.

## Finding mx

1. `which mx` or `command -v mx`
2. `mise where mx` (if installed via mise)
3. `~/.cargo/bin/mx` (if installed via cargo)
4. Source: `cargo run --manifest-path ~/work/personal/code/mx/Cargo.toml --`

## Dependencies

- `base-d` - For encoding/decoding (`cargo install base-d`)
- `git` - For commit operations
