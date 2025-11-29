# cargo-husky Setup

Quick reference for setting up cargo-husky Git hooks in Rust projects.

## Basic Setup

Add to `Cargo.toml`:

```toml
[dev-dependencies]
cargo-husky = "1"
```

Run `cargo test` to generate hooks. Default behavior: creates `.git/hooks/pre-push` running `cargo test`.

## Pre-Push with fmt + clippy

For pre-push hooks running `cargo fmt --check` and `cargo clippy`:

```toml
[dev-dependencies.cargo-husky]
version = "1"
default-features = false
features = ["prepush-hook", "run-cargo-fmt", "run-cargo-clippy"]
```

Available features:
- `prepush-hook` - Creates `.git/hooks/pre-push`
- `precommit-hook` - Creates `.git/hooks/pre-commit`
- `run-cargo-fmt` - Runs `cargo fmt --check`
- `run-cargo-clippy` - Runs `cargo clippy`
- `run-cargo-test` - Runs `cargo test`

## Custom Hooks (Advanced)

If built-in features aren't enough:

1. Create `.cargo-husky/hooks/` directory
2. Add executable hook files (`pre-push`, `pre-commit`, etc.)
3. Use `features = ["user-hooks"]` in Cargo.toml
4. Run `cargo test` to install

## Uninstall

1. Remove from `Cargo.toml`
2. Delete hooks from `.git/hooks/`

## Source

Research from: https://github.com/rhysd/cargo-husky
