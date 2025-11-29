# base-d Dependency Audit
**Date:** 2025-11-29
**Project:** /home/w3surf/work/personal/code/base-d
**Rust:** 1.91.1
**Edition:** 2024 (target)

## Security Status
✅ **CLEAN** - No CVEs detected by cargo-audit

---

## Direct Dependencies Analysis

### MAJOR VERSION BUMPS (Breaking Changes Expected)

#### brotli: 7.0.0 → 8.0.2
- **Current:** 7.0.0
- **Latest:** 8.0.2
- **Risk:** HIGH - Major version bump
- **Used for:** Brotli compression support
- **Action Required:** Research breaking changes

#### criterion: 0.5.1 → 0.7.0 (dev)
- **Current:** 0.5.1
- **Latest:** 0.7.0
- **Risk:** HIGH - Major version bump (dev dep)
- **Used for:** Benchmarking
- **Action Required:** Research breaking changes

#### crossterm: 0.28.1 → 0.29.0
- **Current:** 0.28.1
- **Latest:** 0.29.0
- **Risk:** MEDIUM - Minor looks major but crossterm uses 0.x semver
- **Used for:** Terminal control
- **Action Required:** Check changelog

#### dirs: 5.0.1 → 6.0.0
- **Current:** 5.0.1
- **Latest:** 6.0.0
- **Risk:** HIGH - Major version bump
- **Used for:** Standard directory paths
- **Action Required:** Research breaking changes

#### rand: 0.8.5 → 0.9.2
- **Current:** 0.8.5
- **Latest:** 0.9.2
- **Risk:** MEDIUM - Major version bump, but rand is stable
- **Used for:** Random number generation
- **Action Required:** Research breaking changes

---

### MINOR/PATCH VERSION BUMPS (Low Risk)

#### terminal_size: 0.3.0 → 0.4.3
- **Current:** 0.3.0
- **Latest:** 0.4.3
- **Risk:** LOW - Minor bump
- **Used for:** Terminal size detection
- **Action Required:** Review changelog, likely safe

---

### PATCH BUMPS (Safe to Apply)

**Build dependencies:**
- cc: 1.2.47 → 1.2.48 (indirect via blake3, lz4-sys, lzma-sys, zstd-sys)

**WASM dependencies (indirect):**
- wasm-bindgen: 0.2.105 → 0.2.106
- js-sys: 0.3.82 → 0.3.83
- web-sys: 0.3.82 → 0.3.83

**Note:** All other outdated dependencies are transitive (pulled in by direct deps above).

---

## Transitive Dependency Chain Notes

Major transitive updates to be aware of:
- **rustix:** 0.38.44 → 1.1.2 (via crossterm, terminal_size) - MAJOR bump
- **windows-sys:** Various versions consolidating to newer releases
- **thiserror:** 1.0.69 → 2.0.17 (via redox_users) - MAJOR bump
- **itertools:** 0.10.5 → 0.13.0 (via criterion) - MAJOR bump

These will be pulled in when updating the direct dependencies above.

---

## Recommendations

1. **Start with patch bumps** - Update cc, wasm-bindgen ecosystem (low risk)
2. **Research major bumps** - Check migration guides for:
   - brotli 7→8
   - dirs 5→6
   - rand 0.8→0.9
   - criterion 0.5→0.7 (dev only, lower priority)
3. **Test terminal deps** - crossterm and terminal_size changes together
4. **Edition 2024 compatibility** - Verify all updates work with Edition 2024

---

## Migration Guides Needed

Checking cache: `~/.matrix/artifacts/cycles/rust/dependencies/`

- [ ] brotli/7.0.0-to-8.0.2.md
- [ ] dirs/5.0.1-to-6.0.0.md
- [ ] rand/0.8.5-to-0.9.2.md
- [ ] crossterm/0.28.1-to-0.29.0.md
- [ ] criterion/0.5.1-to-0.7.0.md (dev dep)
- [ ] terminal_size/0.3.0-to-0.4.3.md

