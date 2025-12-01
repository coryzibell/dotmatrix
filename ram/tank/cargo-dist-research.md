# Cargo-Dist Research: base-d & mx

## Current Setup

### Architecture
- **No cargo-dist**: These projects don't use cargo-dist at all
- **Custom GitHub workflow**: Using reusable workflow from `nebuchadnezzar` repo
- **Workflow file**: `/home/w3surf/work/personal/code/nebuchadnezzar/.github/workflows/follow-the-white-rabbit.yml`

### Build Matrix (lines 34-66)

| Target | OS | Notes |
|--------|-----|-------|
| `x86_64-unknown-linux-gnu` | ubuntu-latest | Native |
| `aarch64-unknown-linux-gnu` | ubuntu-latest | cross |
| `x86_64-unknown-linux-musl` | ubuntu-latest | cross |
| `aarch64-unknown-linux-musl` | ubuntu-latest | cross |
| `x86_64-unknown-freebsd` | ubuntu-latest | cross |
| `x86_64-pc-windows-msvc` | windows-latest | Native |
| `aarch64-pc-windows-msvc` | windows-latest | Native |
| `x86_64-apple-darwin` | macos-latest | Native |
| `aarch64-apple-darwin` | macos-latest | Native |

### Current Asset Naming (lines 90-108)

The workflow uses a **custom mapping** from Rust target triples to simplified names:

```bash
x86_64-unknown-linux-gnu    -> ${BINARY_NAME}-linux-x86_64
aarch64-unknown-linux-gnu   -> ${BINARY_NAME}-linux-aarch64
x86_64-unknown-linux-musl   -> ${BINARY_NAME}-linux-x86_64-musl
aarch64-unknown-linux-musl  -> ${BINARY_NAME}-linux-aarch64-musl
x86_64-unknown-freebsd      -> ${BINARY_NAME}-freebsd-x86_64
x86_64-pc-windows-msvc      -> ${BINARY_NAME}-windows-x86_64
aarch64-pc-windows-msvc     -> ${BINARY_NAME}-windows-aarch64
x86_64-apple-darwin         -> ${BINARY_NAME}-macos-x86_64
aarch64-apple-darwin        -> ${BINARY_NAME}-macos-aarch64
*                           -> ${BINARY_NAME}-${TARGET}  # fallback
```

### Example Current Names
- `base-d-linux-x86_64.tar.gz`
- `base-d-windows-x86_64.zip`
- `mx-macos-aarch64.tar.gz`

---

## To Change to Full Target Triples

### Option 1: Simple Script Modification

Replace the "Determine asset name" step (lines 90-108) with:

```yaml
- name: Determine asset name
  id: asset
  shell: bash
  run: |
    echo "asset_name=${BINARY_NAME}-${{ matrix.target }}" >> $GITHUB_OUTPUT
```

This would produce:
- `base-d-x86_64-unknown-linux-gnu.tar.gz`
- `base-d-x86_64-pc-windows-msvc.zip`
- `mx-aarch64-apple-darwin.tar.gz`

### Option 2: cargo-dist Migration

Would require:
1. Add `[workspace.metadata.dist]` to each project's `Cargo.toml`
2. Replace custom workflow with cargo-dist's generated workflows
3. Configure targets in dist config

**Pros:**
- Industry standard tool
- Maintained by others
- Automatic installer generation
- Better release notes

**Cons:**
- Loss of mx encode-commit integration in version bumps
- Need to migrate existing workflow patterns
- Learning curve for team

---

## Recommendation

**Go with Option 1** - simplest change, maintains existing workflow infrastructure.

Change location: `/home/w3surf/work/personal/code/nebuchadnezzar/.github/workflows/follow-the-white-rabbit.yml` lines 90-108

This affects all projects using the reusable workflow:
- base-d
- mx
- (any others using nebuchadnezzar workflows)
