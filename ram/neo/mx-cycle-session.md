# mx Cycle Session - 2025-12-01

## Status: PR #48 Pending CI

## Completed
- Removed unused deps: `notify`, `pulldown-cmark`
- Upgraded: `dirs` 5→6, `rusqlite` 0.32→0.37, `jsonwebtoken` 9→10, `base-d` 2→3
- Added `pem` crate for jsonwebtoken 10 PEM→DER conversion
- Fixed `env::remove_var` unsafe wrapper for Edition 2024
- Bumped to Edition 2024
- All tests passing (60 pass, 3 ignored)

## PR
- https://github.com/coryzibell/mx/pull/48
- Closes issue #47

## Earlier Session Work (same day)
- base-d v3.0.0 CLI refactor merged (PR #123)
  - Subcommand pattern: encode, decode, detect, hash, config, neo
  - Handler architecture in src/cli/handlers/
  - 24 tests migrated
- Fixed nebuchadnezzar wake-up.yml: mx encode-commit parsing
- Published mx v0.1.22 to crates.io
- Closed base-d issue #115 (library API ergonomics)
