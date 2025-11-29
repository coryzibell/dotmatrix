# CI/CD Pipeline Review: base-d

**Reviewed:** 2025-11-28
**Repository:** github.com/coryzibell/base-d
**Current Version:** 0.2.1
**Reviewer:** Niobe

---

## Executive Summary

The base-d pipeline is **solid but inefficient**. You've got comprehensive coverage - multi-platform builds, quality gates, automated releases - but the architecture has redundancy and wasteful patterns. The workflows fire successfully (confirmed via recent runs), but you're burning CI minutes and developer time unnecessarily.

**Key Strengths:**
- Comprehensive multi-platform build matrix (9 targets)
- Proper quality gates (fmt, clippy, tests)
- Auto-versioning on main merges
- Draft PR filtering (smart)

**Critical Issues:**
- No caching in Release workflow (rebuilding from scratch for 9 targets)
- Redundant test execution across workflows
- Inefficient cross-compilation setup (installing cross on every run)
- No benchmark tracking in CI
- Missing security checks (cargo-audit, SBOM generation)

**Bottom Line:** Works, but tighter spots exist. You can thread this needle better.

---

## Workflow Architecture

### 1. PR Checks (`pr-checks.yml`)

**Trigger:** PR to main (opened, sync, reopened, ready_for_review)

**Jobs:**
```
check-should-run → (test || fmt || clippy)
```

**What's Working:**
- Draft PR filtering prevents wasted runs on WIP
- Parallel job execution (test, fmt, clippy run independently)
- Multi-platform testing matrix (Linux, Windows)
- Cargo caching implemented (registry, index, build)

**What's Not:**
- macOS testing disabled (ARM64 SIMD bug #59)
- Cache keys are OS-specific only - no Rust version differentiation
- No cache compression or size monitoring
- Clippy runs on all-targets all-features but tests don't
- Building release artifacts in test job (unnecessary)

**Cache Effectiveness:**
```yaml
# Current approach
key: ${{ runner.os }}-cargo-registry-${{ hashFiles('**/Cargo.lock') }}
restore-keys: |
  ${{ runner.os }}-cargo-registry-
```

This is basic but functional. However:
- No Rust version in key (cache survives toolchain updates)
- No target differentiation in build cache
- Separate caches per job type (test vs clippy) reduces hit rate

---

### 2. Prepare Release (`auto-release.yml`)

**Trigger:** Push to main

**Jobs:**
```
bump-version → format-check → test → create-tag
```

**What's Working:**
- Smart version detection (skips if manually bumped)
- Automated semver patch bumping
- Sequential quality gates before tagging
- Uses PAT_TOKEN for tag push (triggers Release workflow)

**What's Not:**
- **Duplicate test execution** - just ran in PR checks
- Format check runs again (already validated in PR)
- No mechanism for major/minor bumps (manual only)
- Commits to main in a push workflow (race condition risk)
- No protection against concurrent runs

**Critical Path:**
```
~2m bump + ~1m format + ~3m test = ~6m before tag creation
```

All of this already passed in PR checks. Wasteful.

---

### 3. Release (`release.yml`)

**Trigger:** Tag push (`v*`)

**Jobs:**
```
build (9 targets in parallel) → release (aggregate + create GitHub release)
```

**Build Matrix:**
| Target | OS | Cross-Compile | Tool |
|--------|-----|---------------|------|
| x86_64-unknown-linux-gnu | ubuntu | No | cargo |
| aarch64-unknown-linux-gnu | ubuntu | Yes | cross |
| x86_64-unknown-linux-musl | ubuntu | Yes | cross |
| aarch64-unknown-linux-musl | ubuntu | Yes | cross |
| x86_64-unknown-freebsd | ubuntu | Yes | cross |
| x86_64-pc-windows-msvc | windows | No | cargo |
| aarch64-pc-windows-msvc | windows | No | cargo |
| x86_64-apple-darwin | macos | No | cargo |
| aarch64-apple-darwin | macos | No | cargo |

**What's Working:**
- Comprehensive platform coverage
- Proper artifact packaging (tar.gz for *nix, zip for Windows)
- Auto-generated release notes
- Idempotent release creation (checks if exists)

**What's Not:**
- **ZERO caching** - every build starts from scratch
- **Installing cross on every run** - should be cached or use pre-built image
- **Individual build steps per target** - massive YAML duplication
- No build matrix validation (cross may fail silently)
- No checksum generation for release assets
- ARM Windows build (aarch64-pc-windows-msvc) rarely tested - may be broken
- FreeBSD build via cross may be outdated/broken

**Build Time Estimate:**
```
~5-8 minutes per target × 9 targets = 45-70 minutes wall time (parallelized)
```

With caching: Could be 2-3 minutes per target.

---

### 4. Publish Crate (`publish-crate.yml`)

**Trigger:** Release workflow completion (success)

**What's Working:**
- Triggered only on successful Release
- Simple, focused, single job
- Uses CARGO_REGISTRY_TOKEN secret

**What's Not:**
- No dry-run validation
- No version verification (could publish wrong version)
- No rollback mechanism
- No publish verification/smoke test

**Risk:**
- If Release workflow succeeds but artifacts are broken, you publish a broken crate
- No way to republish if crates.io publish fails partway

---

## Caching Analysis

### Current Implementation

**PR Checks:**
```yaml
# Registry cache
~/.cargo/registry → ${{ runner.os }}-cargo-registry-${{ hashFiles('**/Cargo.lock') }}

# Git dependencies
~/.cargo/git → ${{ runner.os }}-cargo-git-${{ hashFiles('**/Cargo.lock') }}

# Build artifacts
target → ${{ runner.os }}-cargo-build-${{ hashFiles('**/Cargo.lock') }}
```

**Release Workflow:**
- None

### Problems

1. **Cache Key Fragility**
   - Cargo.lock changes = cache miss
   - Rust toolchain update = cache hit with wrong artifacts
   - No fallback to previous Cargo.lock versions

2. **Cache Isolation**
   - Test job and Clippy job maintain separate caches
   - No sharing between PR and main workflows
   - Release builds never benefit from PR build cache

3. **Missing Caches**
   - `cross` binary installation (fetched from git every time)
   - Rust toolchain installation (could use rust-cache action)
   - Target-specific build artifacts

### Recommended Approach

**Use `Swatinem/rust-cache@v2`:**
```yaml
- uses: Swatinem/rust-cache@v2
  with:
    shared-key: "base-d"
    cache-on-failure: true
```

This handles:
- Automatic Rust version in key
- Target-specific caching
- Incremental build caching
- Registry and git dep caching
- Cross-workflow cache sharing

**Estimated Improvement:**
- PR checks: 6m → 2-3m (first run), ~1m (cached)
- Release builds: 45-70m → 15-20m (with warm cache from main)

---

## Quality Gates

### Current Gates

**Pre-Merge (PR Checks):**
1. ✅ rustfmt --check
2. ✅ clippy --all-targets --all-features -D warnings
3. ✅ cargo test (Linux, Windows)
4. ✅ cargo build --release (Linux, Windows)

**Pre-Release (auto-release):**
1. ✅ Format check (duplicate)
2. ✅ Tests (duplicate)

### Missing Gates

1. **Security Auditing**
   - No `cargo-audit` check for vulnerable dependencies
   - No SBOM (Software Bill of Materials) generation
   - No supply chain verification

2. **Benchmark Regression**
   - Has `criterion` benches but no CI tracking
   - No performance regression detection

3. **Coverage Tracking**
   - No test coverage measurement
   - No coverage trend reporting

4. **Documentation**
   - No `cargo doc` build validation
   - No doc test execution tracking
   - No link checking

5. **Release Validation**
   - No smoke test after publish
   - No version consistency check (Cargo.toml vs git tag)
   - No changelog generation/validation

### Recommended Additions

```yaml
# Security check (should fail PR)
- name: Security audit
  run: |
    cargo install --locked cargo-audit
    cargo audit

# Benchmark tracking (informational)
- name: Run benchmarks
  run: cargo bench --no-fail-fast

# Coverage (informational, could gate later)
- name: Code coverage
  uses: taiki-e/install-action@v2
  with:
    tool: cargo-tarpaulin
- run: cargo tarpaulin --out Xml
```

---

## Release Automation

### Current Flow

```
main merge → auto-release:
  1. Bump patch version
  2. Commit version to main
  3. Run tests (duplicate)
  4. Create tag

tag push → release:
  1. Build 9 platform binaries
  2. Package artifacts
  3. Create GitHub release
  4. Upload assets

release success → publish-crate:
  1. Publish to crates.io
```

### Issues

1. **Race Condition Risk**
   - auto-release commits to main during workflow
   - If two PRs merge simultaneously → conflict
   - No queue/lock mechanism

2. **No Manual Release Path**
   - Can't do minor/major bumps via workflow
   - Can't skip auto-release for docs-only changes

3. **No Changelog**
   - Uses `--generate-notes` (GitHub auto-gen)
   - No conventional commits enforcement
   - No CHANGELOG.md maintenance

4. **Version Synchronization**
   - Cargo.toml version bumped in auto-release
   - No verification that tag matches Cargo.toml
   - Could theoretically drift

### Recommendations

**1. Use `release-please` or `semantic-release`**
- Handles version bumping based on conventional commits
- Generates changelogs automatically
- Creates release PR instead of direct commits
- Supports major/minor/patch via commit messages

**2. Skip Auto-Release for Specific Commits**
```yaml
# Check commit message for [skip-release]
if: "!contains(github.event.head_commit.message, '[skip-release]')"
```

**3. Add Version Validation**
```yaml
- name: Validate version consistency
  run: |
    TAG_VERSION=${GITHUB_REF_NAME#v}
    CARGO_VERSION=$(grep '^version = ' Cargo.toml | head -1 | cut -d'"' -f2)
    if [ "$TAG_VERSION" != "$CARGO_VERSION" ]; then
      echo "Version mismatch: tag=$TAG_VERSION cargo=$CARGO_VERSION"
      exit 1
    fi
```

---

## Pipeline Efficiency

### Metrics

**PR Checks:**
- Duration: ~6-8 minutes (first run), ~4-5 minutes (cached)
- Jobs: 3 parallel (test, fmt, clippy)
- Platforms: 2 (Linux, Windows)
- Caching: Partial (cargo registry/index/build)

**Auto-Release:**
- Duration: ~6-8 minutes
- Jobs: 4 sequential
- Duplicate work: ~80% (tests already ran in PR)

**Release Build:**
- Duration: ~45-70 minutes (9 parallel builds)
- Caching: None
- Cross-compilation: 5/9 targets

**Total PR-to-Publish Time:**
- PR checks: ~6m
- Auto-release: ~6m (wasteful)
- Release build: ~60m
- Publish: ~1m
- **Total: ~73 minutes**

### Optimization Targets

1. **Eliminate duplicate testing in auto-release**
   - Skip tests if PR was just merged
   - Trust PR checks (they just passed)
   - **Savings: ~5 minutes per main merge**

2. **Add caching to Release workflow**
   - Use rust-cache with shared key
   - Cache cross binary
   - **Savings: ~50% build time = ~30 minutes**

3. **Consolidate build steps**
   - Use matrix-driven conditionals instead of individual steps
   - Reduce YAML duplication
   - **Savings: maintainability, not time**

**Post-Optimization Total:** ~38 minutes (48% improvement)

---

## Security Considerations

### Current State

- ✅ PAT_TOKEN used for tag creation (allows workflow triggering)
- ✅ CARGO_REGISTRY_TOKEN stored as secret
- ✅ Minimal permissions (`contents: read` on publish, `contents: write` on release)
- ❌ No dependency audit
- ❌ No SBOM generation
- ❌ No provenance/attestation (SLSA framework)
- ❌ No signature verification on releases

### Recommendations

**1. Add cargo-audit to PR checks**
```yaml
- name: Security audit
  run: |
    cargo install --locked cargo-audit
    cargo audit
```

**2. Generate SBOM for releases**
```yaml
- name: Generate SBOM
  run: |
    cargo install cargo-sbom
    cargo sbom > sbom.json
- name: Upload SBOM
  uses: actions/upload-artifact@v4
  with:
    name: sbom
    path: sbom.json
```

**3. Sign release artifacts (optional, advanced)**
```yaml
- name: Sign artifacts
  uses: sigstore/cosign-installer@main
- run: |
    cosign sign-blob \
      --bundle bundle.json \
      artifacts/*
```

---

## Cross-Compilation Review

### Current Approach

**Tool Selection:**
- Native builds: `cargo build` (4/9 targets)
- Cross-compilation: `cross` from git HEAD (5/9 targets)

**Cross Targets:**
- aarch64-unknown-linux-gnu
- x86_64-unknown-linux-musl
- aarch64-unknown-linux-musl
- x86_64-unknown-freebsd

**Issues:**

1. **Installing from git HEAD**
```yaml
run: cargo install cross --git https://github.com/cross-rs/cross
```
- Not pinned to version/commit
- Could break on cross updates
- Slow (builds from source every time)

2. **No validation**
- Cross may fail to build target
- No smoke test of produced binary
- ARM64 builds untested (no actual ARM64 runner)

3. **FreeBSD target questionable**
- Cross support for FreeBSD is community-maintained
- May be outdated or broken
- No way to test it

### Recommendations

**1. Pin cross version**
```yaml
run: cargo install cross --git https://github.com/cross-rs/cross --rev abc123
```

**2. Cache cross binary**
```yaml
- name: Cache cross
  uses: actions/cache@v4
  with:
    path: ~/.cargo/bin/cross
    key: cross-${{ env.CROSS_VERSION }}
```

**3. Add smoke tests**
```yaml
- name: Verify binary
  run: |
    file target/${{ matrix.target }}/release/base-d
    # For native targets:
    target/${{ matrix.target }}/release/base-d --version
```

**4. Consider dropping FreeBSD**
- No test coverage
- Unclear user demand
- Cross support questionable
- Could build on-demand vs every release

---

## Workflow Triggers & Concurrency

### Current Triggers

**pr-checks.yml:**
```yaml
on:
  pull_request:
    branches: [ main ]
    types: [ opened, synchronize, reopened, ready_for_review ]
```
✅ Appropriate - runs on all relevant PR events

**auto-release.yml:**
```yaml
on:
  push:
    branches:
      - main
```
❌ No concurrency control - multiple merges = race condition

**release.yml:**
```yaml
on:
  push:
    tags:
      - 'v*'
```
✅ Appropriate

**publish-crate.yml:**
```yaml
on:
  workflow_run:
    workflows: ["Release"]
    types: [completed]
```
✅ Appropriate

### Missing Concurrency Controls

**Problem:** If two PRs merge to main in rapid succession:
1. First auto-release starts, bumps version to 0.2.2
2. Second auto-release starts (before first commits), also tries to bump to 0.2.2
3. First commits successfully
4. Second tries to commit → conflict or duplicate version

**Solution:**
```yaml
concurrency:
  group: release-${{ github.ref }}
  cancel-in-progress: false  # queue, don't cancel
```

---

## Recommendations Summary

### High Priority (Do First)

1. **Add rust-cache to all workflows**
   - Use `Swatinem/rust-cache@v2`
   - Share cache key across workflows
   - **Impact:** 40-60% build time reduction

2. **Add concurrency control to auto-release**
   - Prevent race conditions on rapid merges
   - **Impact:** Eliminates version bump conflicts

3. **Remove duplicate testing from auto-release**
   - Trust PR checks
   - **Impact:** 5 minutes saved per merge, reduced CI cost

4. **Add cargo-audit to PR checks**
   - Catch vulnerable dependencies pre-merge
   - **Impact:** Security posture, supply chain safety

### Medium Priority (Next)

5. **Pin cross version**
   - Use specific commit/tag
   - Cache the binary
   - **Impact:** Build reliability, ~2 min per cross build saved

6. **Add version consistency validation**
   - Verify tag matches Cargo.toml
   - **Impact:** Prevents version drift

7. **Generate and attach SBOM**
   - Transparency for users
   - **Impact:** Compliance, security visibility

8. **Add smoke tests to release builds**
   - Verify binaries actually work
   - **Impact:** Catch broken builds pre-publish

### Low Priority (Future)

9. **Migrate to release-please**
   - Better version/changelog management
   - **Impact:** Developer experience, changelog quality

10. **Add benchmark tracking**
    - Detect performance regressions
    - **Impact:** Performance visibility

11. **Add coverage tracking**
    - Measure test quality
    - **Impact:** Code quality visibility

12. **Consider dropping FreeBSD target**
    - Unless there's proven demand
    - **Impact:** Reduced build time, simpler maintenance

---

## Detailed Workflow Configurations

### Optimized PR Checks

```yaml
name: PR Checks

on:
  pull_request:
    branches: [ main ]
    types: [ opened, synchronize, reopened, ready_for_review ]

env:
  CARGO_TERM_COLOR: always
  RUST_BACKTRACE: 1

jobs:
  check-should-run:
    name: Check if CI should run
    runs-on: ubuntu-latest
    outputs:
      should_run: ${{ steps.check.outputs.should_run }}
    steps:
      - name: Determine if checks should run
        id: check
        run: |
          if [ "${{ github.event.pull_request.draft }}" == "false" ]; then
            echo "should_run=true" >> $GITHUB_OUTPUT
          else
            echo "should_run=false" >> $GITHUB_OUTPUT
          fi

  security:
    name: Security Audit
    needs: check-should-run
    if: needs.check-should-run.outputs.should_run == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
        with:
          shared-key: "base-d"
      - name: Install cargo-audit
        run: cargo install --locked cargo-audit
      - name: Run security audit
        run: cargo audit

  test:
    name: Test
    needs: check-should-run
    if: needs.check-should-run.outputs.should_run == 'true'
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - os: ubuntu-latest
            target: x86_64-unknown-linux-gnu
          - os: windows-latest
            target: x86_64-pc-windows-msvc

    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}
      - uses: Swatinem/rust-cache@v2
        with:
          shared-key: "base-d"
          key: ${{ matrix.target }}

      - name: Run tests
        run: cargo test --all-features --verbose

      - name: Build release
        run: cargo build --release --verbose

  fmt:
    name: Format Check
    needs: check-should-run
    if: needs.check-should-run.outputs.should_run == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt
      - run: cargo fmt --all -- --check

  clippy:
    name: Clippy
    needs: check-should-run
    if: needs.check-should-run.outputs.should_run == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy
      - uses: Swatinem/rust-cache@v2
        with:
          shared-key: "base-d"
      - run: cargo clippy --all-targets --all-features -- -D warnings
```

### Optimized Auto-Release

```yaml
name: Prepare Release

on:
  push:
    branches:
      - main

permissions:
  contents: write

# Prevent concurrent releases
concurrency:
  group: release-${{ github.ref }}
  cancel-in-progress: false

jobs:
  bump-version:
    name: Bump Version and Tag
    runs-on: ubuntu-latest
    # Skip if commit message contains [skip-release]
    if: "!contains(github.event.head_commit.message, '[skip-release]')"
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.PAT_TOKEN }}

      - name: Bump patch version
        id: bump
        run: |
          # Check if version changed in the last commit
          CURRENT_VERSION=$(grep '^version = ' Cargo.toml | head -1 | cut -d'"' -f2)
          PREVIOUS_VERSION=$(git show HEAD~1:Cargo.toml | grep '^version = ' | head -1 | cut -d'"' -f2)

          if [ "$CURRENT_VERSION" != "$PREVIOUS_VERSION" ]; then
            echo "Version was manually updated from $PREVIOUS_VERSION to $CURRENT_VERSION"
            echo "version=$CURRENT_VERSION" >> $GITHUB_OUTPUT
            echo "skip_bump=true" >> $GITHUB_OUTPUT
          else
            # Increment patch
            MAJOR=$(echo $CURRENT_VERSION | cut -d'.' -f1)
            MINOR=$(echo $CURRENT_VERSION | cut -d'.' -f2)
            PATCH=$(echo $CURRENT_VERSION | cut -d'.' -f3)
            NEW_PATCH=$((PATCH + 1))
            NEW_VERSION="${MAJOR}.${MINOR}.${NEW_PATCH}"

            # Update Cargo.toml
            sed -i "s/^version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" Cargo.toml

            echo "Bumped version from $CURRENT_VERSION to $NEW_VERSION"
            echo "version=$NEW_VERSION" >> $GITHUB_OUTPUT
            echo "skip_bump=false" >> $GITHUB_OUTPUT
          fi

      - name: Commit version bump
        if: steps.bump.outputs.skip_bump != 'true'
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add Cargo.toml
          git commit -m "Bump version to ${{ steps.bump.outputs.version }}"
          git push origin main

      - name: Create and push tag
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

          VERSION="v${{ steps.bump.outputs.version }}"

          # Check if tag already exists
          if git rev-parse "$VERSION" >/dev/null 2>&1; then
            echo "Tag $VERSION already exists, skipping"
            exit 0
          fi

          # Pull latest (in case we just pushed version bump)
          git pull --rebase origin main

          # Create and push tag
          git tag -a "$VERSION" -m "Release $VERSION"
          git push origin "$VERSION"
```

### Optimized Release Build

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write

jobs:
  build:
    name: Build ${{ matrix.target }}
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        include:
          - os: ubuntu-latest
            target: x86_64-unknown-linux-gnu
            artifact_name: base-d
            asset_name: base-d-linux-x86_64
            use_cross: false
          - os: ubuntu-latest
            target: aarch64-unknown-linux-gnu
            artifact_name: base-d
            asset_name: base-d-linux-aarch64
            use_cross: true
          - os: ubuntu-latest
            target: x86_64-unknown-linux-musl
            artifact_name: base-d
            asset_name: base-d-linux-x86_64-musl
            use_cross: true
          - os: ubuntu-latest
            target: aarch64-unknown-linux-musl
            artifact_name: base-d
            asset_name: base-d-linux-aarch64-musl
            use_cross: true
          - os: windows-latest
            target: x86_64-pc-windows-msvc
            artifact_name: base-d.exe
            asset_name: base-d-windows-x86_64.exe
            use_cross: false
          - os: windows-latest
            target: aarch64-pc-windows-msvc
            artifact_name: base-d.exe
            asset_name: base-d-windows-aarch64.exe
            use_cross: false
          - os: macos-latest
            target: x86_64-apple-darwin
            artifact_name: base-d
            asset_name: base-d-macos-x86_64
            use_cross: false
          - os: macos-latest
            target: aarch64-apple-darwin
            artifact_name: base-d
            asset_name: base-d-macos-aarch64
            use_cross: false

    steps:
      - uses: actions/checkout@v4

      - uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}

      - uses: Swatinem/rust-cache@v2
        with:
          shared-key: "base-d-release"
          key: ${{ matrix.target }}

      # Cache cross binary (Linux only)
      - name: Cache cross
        if: matrix.use_cross
        uses: actions/cache@v4
        with:
          path: ~/.cargo/bin/cross
          key: cross-v0.2.5  # Pin version

      - name: Install cross
        if: matrix.use_cross
        run: |
          if [ ! -f ~/.cargo/bin/cross ]; then
            cargo install cross --git https://github.com/cross-rs/cross --rev 19be83481fd3e50ea103d800d72e0f8eddb1c90c
          fi

      - name: Build with cargo
        if: "!matrix.use_cross"
        run: cargo build --release --target ${{ matrix.target }}

      - name: Build with cross
        if: matrix.use_cross
        run: cross build --release --target ${{ matrix.target }}

      # Smoke test (native targets only)
      - name: Test binary
        if: "!matrix.use_cross"
        run: |
          target/${{ matrix.target }}/release/${{ matrix.artifact_name }} --version

      - name: Package binary (Unix)
        if: runner.os != 'Windows'
        run: |
          cd target/${{ matrix.target }}/release
          tar -czf ../../../${{ matrix.asset_name }}.tar.gz ${{ matrix.artifact_name }}

      - name: Package binary (Windows)
        if: runner.os == 'Windows'
        shell: pwsh
        run: |
          Compress-Archive -Path target/${{ matrix.target }}/release/${{ matrix.artifact_name }} -DestinationPath ${{ matrix.asset_name }}.zip

      - name: Generate checksum (Unix)
        if: runner.os != 'Windows'
        run: |
          sha256sum ${{ matrix.asset_name }}.tar.gz > ${{ matrix.asset_name }}.tar.gz.sha256

      - name: Generate checksum (Windows)
        if: runner.os == 'Windows'
        shell: pwsh
        run: |
          $hash = (Get-FileHash ${{ matrix.asset_name }}.zip -Algorithm SHA256).Hash
          "$hash  ${{ matrix.asset_name }}.zip" | Out-File -FilePath ${{ matrix.asset_name }}.zip.sha256

      - name: Upload artifact (Unix)
        if: runner.os != 'Windows'
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.asset_name }}-packaged
          path: |
            ${{ matrix.asset_name }}.tar.gz
            ${{ matrix.asset_name }}.tar.gz.sha256

      - name: Upload artifact (Windows)
        if: runner.os == 'Windows'
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.asset_name }}-packaged
          path: |
            ${{ matrix.asset_name }}.zip
            ${{ matrix.asset_name }}.zip.sha256

  release:
    name: Create Release
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download all artifacts
        uses: actions/download-artifact@v4
        with:
          path: artifacts

      - name: Create Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          VERSION="${GITHUB_REF_NAME}"

          if gh release view "$VERSION" >/dev/null 2>&1; then
            echo "Release $VERSION already exists, skipping"
            exit 0
          fi

          gh release create "$VERSION" \
            --title "Release $VERSION" \
            --generate-notes

          # Upload all packaged binaries and checksums
          for dir in artifacts/*-packaged/; do
            if [ -d "$dir" ]; then
              for file in "$dir"*.tar.gz "$dir"*.zip "$dir"*.sha256; do
                if [ -f "$file" ]; then
                  gh release upload "$VERSION" "$file"
                fi
              done
            fi
          done
```

---

## Performance Benchmarks (Estimated)

| Metric | Current | Optimized | Improvement |
|--------|---------|-----------|-------------|
| PR Check (first) | 6-8 min | 4-5 min | ~30% |
| PR Check (cached) | 4-5 min | 1-2 min | ~60% |
| Auto-Release | 6-8 min | 1-2 min | ~75% |
| Release Build | 45-70 min | 20-30 min | ~50% |
| Total PR→Publish | ~73 min | ~35 min | ~52% |

**CI Minutes Saved per Release:** ~38 minutes
**CI Cost Reduction (estimated):** ~50%

---

## Final Assessment

**Current Grade:** B+

The pipeline works. It's comprehensive, covers the critical paths, and successfully ships working releases. You've thought through multi-platform builds, quality gates, and automation.

But it's not tight. There's waste - duplicate tests, missing caches, inefficient cross-compilation setup. You're burning time and compute where you don't need to.

**With Optimizations:** A-

Implementing the high-priority recommendations would put this in the "tight and efficient" category. You'd ship faster, waste less CI time, catch security issues earlier, and have better release artifact verification.

Some things in this world never change - you need to build, test, and ship. But some things do - and right now, your pipeline could thread a tighter needle.

---

## Files Referenced

- `/home/w3surf/work/personal/code/base-d/.github/workflows/pr-checks.yml`
- `/home/w3surf/work/personal/code/base-d/.github/workflows/auto-release.yml`
- `/home/w3surf/work/personal/code/base-d/.github/workflows/release.yml`
- `/home/w3surf/work/personal/code/base-d/.github/workflows/publish-crate.yml`
- `/home/w3surf/work/personal/code/base-d/Cargo.toml`

---

Knock knock, Neo.
