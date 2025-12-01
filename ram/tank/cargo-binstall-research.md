# cargo-binstall Integration Research

**Date:** 2025-12-01
**Target Projects:** base-d, mx

## 1. Required Metadata

cargo-binstall uses `[package.metadata.binstall]` section in Cargo.toml.

### Key Configuration Fields

- **pkg-url**: Template for download URL (defaults auto-detect GitHub/GitLab/etc)
- **bin-dir**: Path within archive where binary is located
- **pkg-fmt**: Archive format (tgz, zip, etc.)
- **disabled-strategies**: Disable fallback methods like compile

### Template Variables Available

- `{name}` - package name
- `{version}` - version number
- `{target}` - Rust target triple
- `{bin}` - binary name
- `{archive-suffix}` - format extension (.tar.gz, .zip)
- `{binary-ext}` - .exe on Windows, empty otherwise

## 2. Current Release Asset Naming

### base-d (v3.0.0)
```
base-d-freebsd-x86_64.tar.gz
base-d-linux-aarch64-musl.tar.gz
base-d-linux-aarch64.tar.gz
base-d-linux-x86_64-musl.tar.gz
base-d-linux-x86_64.tar.gz
base-d-macos-aarch64.tar.gz
base-d-macos-x86_64.tar.gz
base-d-windows-aarch64.zip
base-d-windows-x86_64.zip
```

### mx (v0.1.24)
```
mx-freebsd-x86_64.tar.gz
mx-linux-aarch64-musl.tar.gz
mx-linux-aarch64.tar.gz
mx-linux-x86_64-musl.tar.gz
mx-linux-x86_64.tar.gz
mx-macos-aarch64.tar.gz
mx-macos-x86_64.tar.gz
mx-windows-aarch64.zip
mx-windows-x86_64.zip
```

**Pattern:** `{name}-{os}-{arch}[-musl]{archive-suffix}`

## 3. Issues with Current Naming

cargo-binstall expects Rust target triples like:
- `x86_64-unknown-linux-gnu`
- `x86_64-unknown-linux-musl`
- `x86_64-apple-darwin`
- `x86_64-pc-windows-msvc`
- `aarch64-unknown-linux-gnu`

Our current naming uses simplified patterns:
- `linux` instead of `unknown-linux-gnu`
- `macos` instead of `apple-darwin`
- `windows` instead of `pc-windows-msvc`

## 4. Required Changes

### Option A: Keep Current Naming (Custom Mapping)

Add explicit `pkg-url` mapping to handle non-standard names:

```toml
[package.metadata.binstall]
pkg-url = "{ repo }/releases/download/v{ version }/{ name }-{ target }{ archive-suffix }"

[package.metadata.binstall.overrides.x86_64-unknown-linux-gnu]
pkg-url = "{ repo }/releases/download/v{ version }/{ name }-linux-x86_64.tar.gz"

[package.metadata.binstall.overrides.x86_64-unknown-linux-musl]
pkg-url = "{ repo }/releases/download/v{ version }/{ name }-linux-x86_64-musl.tar.gz"

[package.metadata.binstall.overrides.aarch64-unknown-linux-gnu]
pkg-url = "{ repo }/releases/download/v{ version }/{ name }-linux-aarch64.tar.gz"

[package.metadata.binstall.overrides.aarch64-unknown-linux-musl]
pkg-url = "{ repo }/releases/download/v{ version }/{ name }-linux-aarch64-musl.tar.gz"

[package.metadata.binstall.overrides.x86_64-apple-darwin]
pkg-url = "{ repo }/releases/download/v{ version }/{ name }-macos-x86_64.tar.gz"

[package.metadata.binstall.overrides.aarch64-apple-darwin]
pkg-url = "{ repo }/releases/download/v{ version }/{ name }-macos-aarch64.tar.gz"

[package.metadata.binstall.overrides.x86_64-pc-windows-msvc]
pkg-url = "{ repo }/releases/download/v{ version }/{ name }-windows-x86_64.zip"

[package.metadata.binstall.overrides.aarch64-pc-windows-msvc]
pkg-url = "{ repo }/releases/download/v{ version }/{ name }-windows-aarch64.zip"

[package.metadata.binstall.overrides.x86_64-unknown-freebsd]
pkg-url = "{ repo }/releases/download/v{ version }/{ name }-freebsd-x86_64.tar.gz"
```

### Option B: Change Release Naming (Align with Rust Targets)

Update cargo-dist or build process to use full target triples in asset names. Then simple config works:

```toml
[package.metadata.binstall]
pkg-url = "{ repo }/releases/download/v{ version }/{ name }-{ target }{ archive-suffix }"
bin-dir = "{ bin }{ binary-ext }"
```

## 5. Recommended Approach

**Option A** - Keep current naming, use overrides.

Pros:
- No changes to release pipeline
- Human-readable asset names
- Works immediately

Cons:
- Verbose Cargo.toml
- Maintenance burden if adding targets

## Testing

Test locally before publish:
```bash
cargo binstall --manifest-path=/path/to/Cargo.toml --force <package>
```
