# Technical Debt Report: base-d

**Project:** base-d - Universal base encoder
**Version:** 0.2.1
**Review Date:** 2025-11-28
**Codebase Size:** ~4,707 lines of Rust
**Repository:** https://github.com/coryzibell/base-d

---

## Executive Summary

base-d is an actively developed project (191 commits in the last 6 months) with solid foundations but accumulating technical debt as new features are added. The codebase shows good engineering practices (comprehensive tests, benchmarks, CI/CD) alongside areas needing attention: incomplete SIMD implementations, remainder handling gaps, and dependency version conflicts.

**Priority Areas:**
1. **Critical**: SIMD implementation gaps (base16 decode broken, ARM64 disabled)
2. **High**: Remainder handling in SIMD paths (data loss potential)
3. **Medium**: Duplicate dependencies, mise.toml version mismatch
4. **Low**: TODO comments, UTF-8 encoding limitations

---

## 1. Critical Issues

### 1.1 Disabled ARM64 SIMD Support

**Location:** `.github/workflows/pr-checks.yml:39-41`

```yaml
# Disabled until ARM64 SIMD bug #59 is fixed
# - os: macos-latest
#   target: aarch64-apple-darwin
```

**Impact:** No CI coverage for ARM64 (Apple Silicon, AWS Graviton). SIMD bugs on ARM64 could go undetected.

**Root Cause:** Known bug #59 preventing macOS ARM64 builds from passing tests.

**Recommendation:**
- Prioritize fixing issue #59 to re-enable ARM64 CI
- Consider adding ARM64 Linux runner as alternative
- Add feature flag to disable SIMD on ARM64 until fixed

---

### 1.2 Base16 SIMD Decode Disabled

**Location:** `src/simd/mod.rs:570-572`

```rust
// NOTE: Standard base16 decode has a known issue and is temporarily disabled
// Custom base16 (via GenericSimdCodec) works correctly
// TODO: Fix specialized base16 decode implementation
```

**Impact:** SIMD base16 decode test is `#[ignore]`d. Performance loss for hex decoding.

**Affected Code:**
- `src/simd/x86_64/specialized/base16.rs` - x86_64 implementation
- `src/simd/aarch64/mod.rs:88,114` - ARM64 stubs with TODO comments

**Recommendation:**
- Debug specialized base16 decode implementation
- Either fix or remove specialized path (keep generic fallback)
- Add test coverage before re-enabling

---

### 1.3 Missing NEON Implementations

**Location:** `src/simd/aarch64/mod.rs`

```rust
// TODO: Implement NEON base16 encoding (line 88)
// TODO: Implement NEON base16 decoding (line 114)
```

**Impact:** ARM64 systems fall back to scalar code for base16, losing 4x+ performance gains.

**Recommendation:**
- Implement NEON base16 encode/decode to match x86_64 parity
- Or document that ARM64 SIMD only supports base32/base64/base256

---

## 2. High Priority Issues

### 2.1 SIMD Remainder Handling Gaps

**Scope:** 24 TODO comments across SIMD modules

**Locations:**
- `src/simd/generic/mod.rs`: 17 instances
- `src/simd/aarch64/generic.rs`: 7 instances

**Example:**
```rust
// TODO: Handle remainder with scalar code (line 211)
if simd_bytes < data.len() {
    // For now, we don't handle remainder
    // This will be improved in future iterations
}
```

**Impact:** Data loss when input size doesn't align with SIMD block boundaries. Silent truncation could corrupt encodings.

**Affected Bases:**
- Base64, Base32, Base16, Base256, Base58, Base85, Base62, etc.

**Recommendation:**
- Add scalar fallback for remainders in all SIMD paths
- Add tests with non-aligned input sizes (e.g., 13 bytes for base64)
- Consider returning error instead of silent truncation

---

### 2.2 Large LUT Decode Failure

**Location:** `src/simd/lut/large.rs:2565`

```rust
// TODO: Debug decode failure for large inputs with 4+ range dictionaries
// #[test]
// fn test_multi_range_base64_all_byte_values() { ... }
```

**Impact:** Commented-out test indicates broken functionality for complex dictionaries.

**Recommendation:**
- Debug why 4+ range dictionaries fail on large inputs
- Either fix or document limitation in Dictionary API
- Consider splitting test into smaller cases to isolate failure

---

### 2.3 UTF-8 Encoding Limitations

**Location:** `src/simd/generic/mod.rs:1504,1521`

```rust
// Note: For base256 with chars > 0x7F, we need proper UTF-8 handling
// TODO: Implement proper UTF-8 encoding for chars > 0x7F
```

**Impact:** SIMD encoders only work with ASCII-range dictionaries (< 0x80). Limits usefulness for Unicode dictionaries like hieroglyphs, emoji.

**Recommendation:**
- Add UTF-8 encoding support in SIMD paths
- Or document that SIMD requires ASCII dictionaries
- Fall back to scalar for Unicode dictionaries

---

### 2.4 BaseConversion Streaming Limitation

**Location:** `src/encoders/streaming/encoder.rs:63-65`

```rust
/// Note: BaseConversion mode requires reading the entire input at once
/// due to the mathematical nature of the algorithm. For truly streaming
/// behavior, use Chunked or ByteRange modes.
```

**Impact:** Users expecting streaming mode to handle multi-GB files may hit OOM with BaseConversion dictionaries.

**Recommendation:**
- Add validation to reject `--stream` with BaseConversion dictionaries
- Or implement chunked BigInt approach for streaming BaseConversion
- Document streaming compatibility per encoding mode

---

## 3. Medium Priority Issues

### 3.1 Duplicate Dependencies

**Location:** `Cargo.lock`

```
dirs v5.0.1 (used by base-d directly)
dirs v6.0.0 (via shellexpand v3.1.1)

dirs-sys v0.4.1 (via dirs v5.0.1)
dirs-sys v0.5.0 (via dirs v6.0.0)
```

**Impact:**
- Increased binary size (two versions of same crate)
- Potential for inconsistent behavior

**Recommendation:**
- Upgrade `dirs` from 5.0 → 6.0 in `Cargo.toml:23`
- Verify shellexpand compatibility (unlikely to break)

---

### 3.2 mise.toml Version Mismatch

**Location:** `mise.toml:2`

```toml
"cargo:base-d" = "0.1.85"
```

**Current version:** 0.2.1 (per `Cargo.toml:3`)

**Impact:** Recurring `mise WARN missing: cargo:base-d@0.1.85` warnings. Confusion about installed version.

**Recommendation:**
- Update to `"cargo:base-d" = "0.2.1"`
- Or remove mise.toml if not using mise for this project
- Add mise.toml to .gitignore if it's personal tooling

---

### 3.3 Error Handling Patterns

**Finding:** 557 instances of `unwrap()`/`expect()`/`panic!()` across 26 files

**Notable locations:**
- `src/simd/lut/large.rs`: 239 occurrences
- `src/simd/generic/mod.rs`: 44 occurrences
- `src/tests.rs`: 25 occurrences (acceptable in tests)

**Impact:**
- Test code: Fine (most are in `#[cfg(test)]` blocks)
- Library code: Potential panics in production

**Recommendation:**
- Audit library code for unwraps (exclude tests)
- Replace with `?` operator and proper error propagation
- Document invariants where unwrap is intentional

---

### 3.4 Unsafe Code Surface

**Finding:** 181 `unsafe` blocks across 13 SIMD files

**Impact:**
- Required for SIMD intrinsics (expected)
- Increased maintenance burden
- Potential for UB if invariants violated

**Recommendation:**
- Ensure all SIMD code has safety comments
- Add Miri testing for unsafe code validation
- Consider higher-level SIMD abstractions (e.g., `std::simd`)

---

## 4. Low Priority Issues

### 4.1 TODO Comments Inventory

**Total:** 40+ TODO comments across codebase

**Categories:**

**SIMD Remainder Handling (17):**
- Fall back to scalar for small inputs
- Handle remainder bytes

**SIMD Implementation Gaps (5):**
- NEON base16 encode/decode
- Fix specialized base16 decode
- Add multi-range decode support

**Feature Completions (4):**
- UTF-8 encoding for Unicode dictionaries
- Streaming compression/hashing docs

**Documentation (1):**
- `.github/copilot-instructions.md:103` - Add streaming docs

**Recommendation:**
- Convert high-priority TODOs to GitHub issues
- Remove stale TODOs or complete them
- Add deadlines/milestones to feature TODOs

---

### 4.2 Roadmap Completion Status

**Location:** `docs/ROADMAP.md`

**Phase 4 (v0.4.0) - IN PROGRESS:**
- ✅ Performance optimizations (mostly complete)
- ⚠️ Streaming support (partial - missing progress reporting)
- ✅ Enhanced validation (complete)
- ⚠️ Config file support (partial - missing user directories)
- ❌ WASM support (not started)

**Phase 5 (v1.0.0) - NOT STARTED:**
- Documentation gaps
- API stabilization needed
- Examples/tutorials missing

**Recommendation:**
- Update ROADMAP.md with realistic timelines
- Mark SIMD issues as blockers for v0.4.0
- Consider v0.3.x patch releases for urgent fixes

---

### 4.3 Feature Parity Matrix

| Feature | x86_64 | ARM64 | Scalar |
|---------|--------|-------|--------|
| Base64 encode | ✅ SIMD | ✅ NEON | ✅ |
| Base64 decode | ✅ SIMD | ✅ NEON | ✅ |
| Base32 encode | ✅ SIMD | ✅ NEON | ✅ |
| Base32 decode | ✅ SIMD | ✅ NEON | ✅ |
| Base16 encode | ✅ SIMD | ❌ TODO | ✅ |
| Base16 decode | ❌ Disabled | ❌ TODO | ✅ |
| Base256 encode | ✅ SIMD | ✅ NEON | ✅ |
| Base256 decode | ✅ SIMD | ✅ NEON | ✅ |

**Recommendation:**
- Document feature parity in README
- Add runtime feature detection warnings
- Consider feature flags to disable incomplete SIMD paths

---

## 5. Build & CI Configuration

### 5.1 GitHub Actions

**Status:** Good overall

**Observations:**
- Using `actions/checkout@v4` (latest)
- Rust toolchain via `dtolnay/rust-toolchain@stable`
- Cargo caching configured
- Clippy runs with `-D warnings` (strict)

**Gaps:**
- No `cargo-audit` for security vulnerabilities
- No `cargo-outdated` check
- No Miri for unsafe code validation
- No coverage reporting

**Recommendation:**
- Add security audit step
- Add dependabot for automatic updates
- Add Miri test job for SIMD validation
- Consider codecov integration

---

### 5.2 Dependency Freshness

**Unable to verify:** `cargo-outdated` not installed

**Known Issues:**
- `dirs` crate duplication (see 3.1)

**Recommendation:**
- Run `cargo outdated` manually
- Consider automated dependency updates
- Pin major versions, allow minor/patch updates

---

## 6. Code Quality Metrics

### 6.1 Test Coverage

**Test Distribution:**
- 24 test modules with `#[cfg(test)]`
- Comprehensive unit tests
- Integration tests via examples
- Benchmarks using Criterion

**Gaps:**
- Missing tests for SIMD remainders
- Ignored test for base16 SIMD
- Commented-out test for large LUT decode

**Recommendation:**
- Achieve 80%+ coverage for non-SIMD paths
- Add property-based testing (quickcheck/proptest)
- Enable disabled tests or remove

---

### 6.2 Documentation Quality

**API Docs:** Good (comprehensive rustdoc comments)

**External Docs:**
- ✅ README.md - Excellent, well-structured
- ✅ PERFORMANCE.md - Detailed benchmarks
- ✅ COMPRESSION_FEATURE.md - Implementation notes
- ✅ STREAMING_COMPRESSION_HASHING.md - Design doc
- ✅ docs/HASHING.md - Hash algorithm guide
- ⚠️ docs/ROADMAP.md - Needs updates
- ❌ Architecture overview - Missing
- ❌ Contributing guide - Missing

**Recommendation:**
- Add ARCHITECTURE.md explaining encoding modes
- Add CONTRIBUTING.md for new contributors
- Update ROADMAP.md with current status

---

## 7. Refactoring Opportunities

### 7.1 SIMD Module Structure

**Current:** Separate `generic`, `x86_64`, `aarch64` modules

**Issue:** Code duplication for remainder handling, LUT construction

**Recommendation:**
- Extract common SIMD utilities to `simd::common`
- Create trait for platform-specific implementations
- Share remainder handling logic

---

### 7.2 Streaming Encoder/Decoder

**Current:** Separate `StreamingEncoder` and `StreamingDecoder` classes

**Observation:** Significant code duplication in compression/hashing setup

**Recommendation:**
- Extract compression/hashing traits
- Share pipeline logic between encoder/decoder
- Consider builder pattern for configuration

---

### 7.3 Error Types

**Current:** Generic `String` errors in many places

**Recommendation:**
- Define `base_d::Error` enum with variants
- Implement `std::error::Error` and `Display`
- Provide context with error chains

---

## 8. Migration Path Recommendations

### Immediate Actions (Sprint 1-2 weeks)

1. **Fix mise.toml version** (5 min)
2. **Upgrade dirs dependency** (15 min)
3. **Add safety documentation to unsafe blocks** (2 hours)
4. **Create GitHub issues for critical TODOs** (1 hour)

### Short Term (Next Release - v0.2.2)

1. **Implement SIMD remainder handling** (3-5 days)
2. **Fix or remove base16 SIMD decode** (2-3 days)
3. **Add validation for streaming + BaseConversion** (1 day)
4. **Document SIMD feature parity** (1 day)

### Medium Term (v0.3.0)

1. **Resolve ARM64 SIMD bug #59** (1 week)
2. **Implement NEON base16** (3-5 days)
3. **Fix large LUT decode for 4+ ranges** (1 week)
4. **Add UTF-8 support to SIMD encoders** (1-2 weeks)

### Long Term (v0.4.0+)

1. **Refactor SIMD module structure** (2-3 weeks)
2. **Implement proper error types** (1 week)
3. **Add Miri/fuzzing to CI** (1 week)
4. **Complete WASM support** (2-3 weeks)

---

## 9. Dependency Health

### Current Dependencies (41 total)

**Core:**
- `num-bigint`, `num-traits`, `num-integer` - Mathematical encoding
- `serde`, `serde_json`, `toml` - Configuration
- `clap` - CLI argument parsing

**Compression (6 algorithms):**
- `flate2`, `brotli`, `zstd`, `lz4`, `snap`, `xz2`

**Hashing (multiple algorithms):**
- `sha2`, `sha3`, `blake2`, `blake3`, `md-5`, `twox-hash`, `crc`

**CLI/UX:**
- `crossterm`, `terminal_size`, `dirs`, `shellexpand`

**Build/Test:**
- `criterion` (benchmarks)
- `rand` (test data)

**Concerns:**
- Large dependency count (41) increases attack surface
- Compression crates all maintained (good)
- `dirs` duplication (see 3.1)
- `shellexpand` pulls in newer `dirs` than direct dep

**Recommendation:**
- Audit if all compression algorithms are needed
- Consider feature flags for optional algorithms
- Track CVEs via `cargo-audit`

---

## 10. Performance Considerations

### SIMD Optimizations

**Current State:**
- ✅ x86_64 AVX2/SSSE3 for base64 (~4x speedup)
- ✅ ARM64 NEON for base64 (partial)
- ⚠️ Remainder handling missing (data loss)

**Opportunities:**
- Complete SIMD remainder handling
- Add AVX-512 support for modern CPUs
- Implement auto-vectorization hints for scalar fallback

---

### Memory Allocation

**Current:**
- ✅ Pre-allocation in chunked mode
- ✅ 4KB streaming buffers
- ⚠️ BaseConversion reads entire input

**Opportunities:**
- Pool allocations for repeated operations
- Zero-copy where possible
- Arena allocator for temporary buffers

---

## 11. Security Considerations

### Input Validation

**Good:**
- Dictionary validation (duplicates, invalid chars)
- Size constraints on dictionaries

**Gaps:**
- No max input size limits (DoS potential)
- SIMD code doesn't bounds-check remainders
- Compression bomb protection unclear

**Recommendation:**
- Add max input size configuration
- Validate SIMD invariants at runtime (debug mode)
- Add decompression size limits

---

### Unsafe Code Audit

**SIMD Intrinsics:**
- 181 unsafe blocks for x86/ARM intrinsics
- Most appear correct but need review

**Recommendation:**
- Run Miri on test suite
- Add fuzzing for SIMD paths
- Document safety invariants

---

## 12. Maintainability Score

| Category | Score | Notes |
|----------|-------|-------|
| Code Organization | B+ | Well-structured modules, some duplication |
| Test Coverage | B | Comprehensive but gaps in SIMD |
| Documentation | B+ | Good rustdoc, external docs need updates |
| CI/CD | B | Good basics, missing security/coverage |
| Dependency Health | B- | Many deps, one duplication issue |
| Error Handling | C+ | Generic errors, many unwraps |
| Performance | A- | Excellent optimizations, incomplete SIMD |
| **Overall** | **B** | Solid foundation, needs polish |

---

## 13. Recommendations Summary

### Do First (Critical Path)

1. **Implement SIMD remainder handling** - Prevents data corruption
2. **Fix or disable base16 SIMD decode** - Broken functionality
3. **Resolve ARM64 bug #59** - Re-enable CI coverage
4. **Add input validation** - Security hardening

### Do Soon (Quality Improvements)

5. **Upgrade dependencies** - Fix dirs duplication
6. **Document SIMD limitations** - UTF-8, feature parity
7. **Add error types** - Better error reporting
8. **Update roadmap** - Realistic timeline

### Do Eventually (Nice to Have)

9. **Refactor SIMD modules** - Reduce duplication
10. **Add Miri/fuzzing** - Unsafe code validation
11. **WASM support** - Expand platform support
12. **Complete documentation** - Architecture, contributing

---

## 14. Conclusion

base-d is a well-designed project with impressive performance optimizations and a comprehensive feature set. The codebase demonstrates good engineering practices with extensive testing and documentation. However, technical debt is accumulating in the SIMD implementation layer, with incomplete remainder handling, platform-specific gaps, and a critical ARM64 bug.

The project is at a crossroads: either invest in stabilizing the SIMD layer before adding more features (recommended), or gate SIMD behind feature flags and complete it incrementally. The current state risks shipping broken optimizations that could corrupt user data.

**Verdict:** The code that works is excellent. The code marked TODO needs urgent attention before v1.0.

---

**Report prepared by:** Rama-Kandra
**For:** Neo
**Storage:** `/home/w3surf/.matrix/cache/construct/base-d/tech-debt.md`
