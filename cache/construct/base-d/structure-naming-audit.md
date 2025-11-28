# Structure and Naming Audit: base-d

**Project:** base-d - Universal multi-alphabet encoder
**Repository:** /home/w3surf/work/personal/code/base-d
**Audit Date:** 2025-11-27
**Auditor:** The Architect

---

## 1. Current Structure

```
base-d/
├── src/
│   ├── lib.rs                    (252 lines) - Public API, re-exports
│   ├── main.rs                   (585 lines) - CLI application
│   ├── tests.rs                  (343 lines) - Integration tests
│   │
│   ├── core/
│   │   ├── mod.rs                (2 lines)   - Module aggregator
│   │   ├── config.rs             (265 lines) - Configuration types
│   │   └── dictionary.rs         (419 lines) - Dictionary struct & API
│   │
│   ├── encoders/
│   │   ├── mod.rs                (4 lines)   - Module aggregator
│   │   ├── encoding.rs           (116 lines) - Mathematical base conversion
│   │   ├── chunked.rs            (193 lines) - RFC 4648 chunked encoding
│   │   ├── byte_range.rs         (132 lines) - Direct byte-to-char mapping
│   │   └── streaming.rs          (935 lines) - Streaming encode/decode
│   │
│   ├── simd/
│   │   ├── mod.rs                (628 lines) - SIMD dispatcher & selection
│   │   ├── alphabets.rs          (718 lines) - Alphabet identification
│   │   ├── translate.rs          (483 lines) - Character translation
│   │   │
│   │   ├── x86_64/
│   │   │   ├── mod.rs            (~60 lines) - x86_64 SIMD orchestration
│   │   │   ├── common.rs         - Shared x86_64 utilities
│   │   │   └── specialized/
│   │   │       ├── mod.rs
│   │   │       ├── base16.rs     (727 lines)
│   │   │       ├── base32.rs     (906 lines)
│   │   │       ├── base64.rs     (874 lines)
│   │   │       ├── base256.rs    (454 lines)
│   │   │       └── common.rs
│   │   │
│   │   ├── aarch64/
│   │   │   ├── mod.rs
│   │   │   ├── generic.rs        (761 lines)
│   │   │   └── specialized/
│   │   │       ├── mod.rs
│   │   │       ├── base16.rs
│   │   │       ├── base32.rs     (565 lines)
│   │   │       ├── base64.rs     (431 lines)
│   │   │       ├── base256.rs    (330 lines)
│   │   │       └── common.rs
│   │   │
│   │   ├── generic/
│   │   │   └── mod.rs            (1696 lines) - GenericSimdCodec
│   │   │
│   │   └── lut/
│   │       ├── mod.rs            (11 lines)  - LUT module aggregator
│   │       ├── small.rs          (1005 lines)- Small alphabet LUT codec
│   │       └── large.rs          (3169 lines)- Large alphabet LUT codec
│   │
│   ├── compression.rs            (202 lines) - Compression algorithms
│   ├── hashing.rs                (526 lines) - Hashing algorithms
│   └── detection.rs              (401 lines) - Dictionary auto-detection
│
├── benches/
│   └── encoding.rs               - Criterion benchmarks
│
├── examples/
│   ├── hello_world.rs
│   ├── base1024_demo.rs
│   ├── test_base256_simd.rs
│   ├── custom_alphabet.rs
│   ├── simd_check.rs
│   ├── list_alphabets.rs
│   ├── auto_simd.rs
│   ├── generate_base1024.rs
│   └── matrix_demo.rs
│
├── docs/                         - Comprehensive documentation
│   ├── API.md, BASE1024.md, CI_CD.md, COMPRESSION.md
│   ├── CUSTOM_DICTIONARIES.md, DETECTION.md, DICTIONARIES.md
│   ├── ENCODING_MODES.md, HASHING.md, HEX_EXPLANATION.md
│   ├── MATRIX.md, MATRIX_ROADMAP.md, NEO.md, PERFORMANCE.md
│   ├── ROADMAP.md, SIMD.md, STREAMING.md
│
├── Cargo.toml
├── dictionaries.toml             - Built-in dictionary definitions
├── dictionaries-example.toml     - User config template
└── test_cli.sh                   - CLI testing script
```

**Total source lines:** ~6,200 (excluding target/)
**SIMD subsystem:** ~13,800 lines (~70% of codebase)

---

## 2. Structure Analysis

### 2.1 What Works Well

**Clear separation of concerns:**
- `core/` contains foundational types (Dictionary, config)
- `encoders/` separates encoding strategies by mode
- `simd/` isolates platform-specific optimizations
- Top-level modules (`compression`, `hashing`, `detection`) are feature-based

**Module hierarchy is logical:**
- `lib.rs` exposes clean public API with minimal re-exports
- Internal structure mirrors conceptual domains
- Platform-specific code properly isolated behind `cfg` gates

**SIMD organization is sound:**
- Platform separation (x86_64, aarch64) at architecture boundaries
- Specialized implementations for standard encodings (base16/32/64/256)
- Generic fallback codecs (GenericSimdCodec, SmallLutCodec, LargeLutCodec)
- Central dispatcher in `simd/mod.rs` handles selection logic

**Documentation is comprehensive:**
- Extensive `docs/` directory with 17 separate guides
- Clear README, optimization summaries, feature documentation

### 2.2 Structural Issues

#### Issue 1: SIMD module is disproportionately large
**Evidence:** 13,800 lines in SIMD vs. 6,200 total source (70% of codebase).

**Problem:** The SIMD subsystem dominates the codebase. Some files exceed 3,000 lines (`simd/lut/large.rs`). This creates:
- Cognitive overhead when navigating
- Difficult code review
- Potential compile-time bottleneck
- Maintenance burden

**Root cause:** Each specialized implementation is monolithic. `large.rs` contains all variants (base16/32/64) for both x86 and aarch64 in a single file.

#### Issue 2: Duplicate structure between x86_64 and aarch64
**Evidence:** Parallel directory trees with identical file names:
```
simd/x86_64/specialized/{base16,base32,base64,base256}.rs
simd/aarch64/specialized/{base16,base32,base64,base256}.rs
```

**Problem:** This duplication suggests:
- Potential for code drift between platforms
- Shared abstractions may be missing
- Difficult to apply cross-platform fixes

**Mitigation:** The `specialized/common.rs` files exist but may not be capturing all shareable logic.

#### Issue 3: `main.rs` contains business logic
**Evidence:** 585 lines in `main.rs` including:
- `load_xxhash_config()` function (48 lines)
- `matrix_mode()` function (76 lines)
- `detect_mode()` function (67 lines)
- CLI pipeline orchestration (150+ lines)

**Problem:** Violates single-responsibility principle. `main.rs` should be a thin CLI adapter. Business logic belongs in library modules.

**Impact:**
- Business logic not accessible to library consumers
- Harder to test (requires CLI parsing)
- Mixes I/O concerns with domain logic

#### Issue 4: `encoders/` module lacks cohesion
**Evidence:**
- `encoding.rs` - mathematical base conversion (116 lines)
- `chunked.rs` - RFC 4648 encoding (193 lines)
- `byte_range.rs` - 1:1 byte mapping (132 lines)
- `streaming.rs` - streaming I/O (935 lines)

**Problem:** `streaming.rs` is orthogonal to the other three. The first three are **encoding strategies**, while streaming is an **I/O pattern**. They operate at different abstraction levels.

**Impact:** Confusing mental model. Developers expect `encoders/` to contain encoding algorithms, not I/O adapters.

#### Issue 5: Flat top-level structure
**Evidence:** Three standalone modules at root:
- `compression.rs` (202 lines)
- `hashing.rs` (526 lines)
- `detection.rs` (401 lines)

**Problem:** These are ancillary features, not core encoding functionality. They exist at the same level as `core/` and `encoders/`, implying equal importance.

**Impact:** Cluttered root namespace. Not immediately clear that compression/hashing are optional features, not encoding primitives.

### 2.3 Module Boundaries

**Appropriate boundaries:**
- `core::dictionary` - clean abstraction, no leakage
- `simd` - well-isolated behind feature detection
- Platform-specific code properly `cfg`-gated

**Coupling issues:**
- `simd/mod.rs` directly calls encoding functions from specialized modules
- `lib.rs` dispatches on `EncodingMode` to choose encoder (acceptable coupling)
- `main.rs` directly constructs `Dictionary` instances (should use builder or factory)

**No circular dependencies detected.**

---

## 3. Naming Analysis

### 3.1 Rust Conventions: Compliance

**Crate name:** `base-d` (kebab-case) ✓
**Library name:** `base_d` (snake_case) ✓
**Modules:** snake_case ✓
**Types:** PascalCase ✓
**Functions:** snake_case ✓
**Constants:** SCREAMING_SNAKE_CASE ✓

The codebase follows Rust naming conventions consistently.

### 3.2 Module Names: Clarity

**Clear:**
- `core` - foundational types
- `encoders` - encoding implementations
- `simd` - SIMD optimizations
- `compression` - compression algorithms
- `hashing` - hashing algorithms

**Potentially misleading:**
- `encoders/encoding.rs` - redundant name. "Encoding encoders"? Should be `encoders/mathematical.rs` or `encoders/base_conversion.rs`.
- `detection.rs` - vague. Detection of what? Should be `dictionary_detection.rs` or live in a `detection/` module if expanded.

### 3.3 Type Names: Precision

**Excellent:**
- `Dictionary` - clear domain concept
- `EncodingMode` - precisely describes the enumeration
- `CompressionAlgorithm`, `HashAlgorithm` - unambiguous
- `StreamingEncoder`, `StreamingDecoder` - intent is clear

**Confusing:**
- `DictionariesConfig` - plural form is awkward. Why not `DictionaryRegistry` or `DictionaryConfig` (with `dictionaries: HashMap` field)?
- `DictionaryConfig` vs. `Dictionary` - naming collision zone. Config vs. runtime instance is clear in code but easily confused in conversation.

**Inconsistency:**
- `AlphabetMetadata` (in `simd/alphabets.rs`) vs. `Dictionary` (everywhere else). The codebase uses "dictionary" in most places but "alphabet" in SIMD code. Pick one term and use consistently.

### 3.4 Function Names: Intent

**Clear verbs:**
- `encode()`, `decode()` - canonical
- `compress()`, `decompress()` - standard
- `hash()`, `hash_with_config()` - intent obvious

**Ambiguous:**
- `detect()` - detect what? Should be `detect_dictionary()` (it is public as `detect_dictionary()` in lib.rs, but the internal `DictionaryDetector::detect()` is vague).
- `score_dictionary()` - "score" is not a common verb in this domain. Consider `calculate_match_confidence()` or `assess_dictionary_match()`.

**Naming inconsistency:**
- `encode_base64_simd()` - verb-noun-qualifier pattern
- `GenericSimdCodec::encode()` - noun-object pattern with method
- `LargeLutCodec::encode()` - same pattern as above

These two patterns coexist. Not wrong, but creates cognitive friction when reading SIMD dispatcher code.

### 3.5 File Names: Alignment

**Well-aligned:**
- `dictionary.rs` contains `Dictionary`
- `config.rs` contains config types
- `compression.rs` contains compression functions
- `hashing.rs` contains hashing functions

**Misalignment:**
- `encoders/encoding.rs` - contains mathematical base conversion. File name is too generic. Rename to `math.rs` or `base_conversion.rs`.
- `simd/alphabets.rs` - contains `identify_base64_variant()`, `identify_base32_variant()`, `AlphabetMetadata`. Should be `alphabet_detection.rs` or `variants.rs`.
- `simd/translate.rs` - contains character translation utilities. Name is too generic. What does "translate" mean? Rename to `char_mapping.rs` or `lut_builder.rs` if it's about lookup table construction.

### 3.6 Variable/Field Names

Sampling reveals good practices:
- `chars`, `char_to_index`, `lookup_table` in `Dictionary` - clear
- `leading_zeros`, `base_big` in encoding.rs - contextually clear
- `encoded`, `decoded` - standard

No significant issues detected. Variables are appropriately scoped and named.

---

## 4. Recommendations

### 4.1 Immediate (High Impact, Low Risk)

#### R1: Rename `encoders/encoding.rs` → `encoders/math.rs`
**Rationale:** Eliminates redundancy. "Encoding" is already implied by the `encoders/` module.
**Impact:** Improves clarity. No API breakage (internal module).
**Action:**
```bash
git mv src/encoders/encoding.rs src/encoders/math.rs
# Update mod.rs and lib.rs references
```

#### R2: Rename `simd/alphabets.rs` → `simd/variants.rs`
**Rationale:** File contains variant identification functions, not alphabet definitions.
**Impact:** More accurate name. No public API impact.

#### R3: Rename `DictionariesConfig` → `DictionaryRegistry`
**Rationale:** Eliminates awkward plural. "Registry" conveys "collection of dictionaries" more naturally.
**Impact:** Public API change. Requires major version bump or deprecation cycle.
**Alternative:** `DictionarySet` or `DictionaryCollection`.

### 4.2 Structural (Medium Impact, Moderate Risk)

#### R4: Extract business logic from `main.rs` into `cli.rs` module
**Rationale:** Separate CLI adapter from business logic.
**Proposed structure:**
```
src/
├── cli/
│   ├── mod.rs              - CLI orchestration
│   ├── commands.rs         - Command handlers (matrix, detect, etc.)
│   └── config.rs           - CLI-specific config loading
├── main.rs                 - Entry point only (10-20 lines)
```
**Impact:** Improves testability. Business logic becomes library-accessible.

#### R5: Reorganize `encoders/` to separate I/O from algorithms
**Current:**
```
encoders/
├── encoding.rs      (algorithm)
├── chunked.rs       (algorithm)
├── byte_range.rs    (algorithm)
└── streaming.rs     (I/O adapter)
```

**Proposed:**
```
encoders/
├── algorithms/
│   ├── math.rs          (was encoding.rs)
│   ├── chunked.rs
│   └── byte_range.rs
└── streaming/
    ├── encoder.rs
    └── decoder.rs
```

**Rationale:** Separates concerns. "algorithms" are stateless encoding functions. "streaming" are stateful I/O adapters.

#### R6: Move ancillary features to `features/` or `utilities/` module
**Current:** `compression.rs`, `hashing.rs`, `detection.rs` at root.

**Proposed:**
```
src/
├── features/
│   ├── compression.rs
│   ├── hashing.rs
│   └── detection.rs
```

**Alternative:** Keep at root but group in `lib.rs` documentation with clear "Optional Features" section.

**Rationale:** Reduces cognitive load. Makes it clear these are orthogonal to core encoding.

### 4.3 SIMD Subsystem (High Impact, High Risk)

#### R7: Split monolithic SIMD files
**Problem:** `simd/lut/large.rs` is 3,169 lines.

**Proposed refactoring:**
```
simd/lut/
├── large/
│   ├── mod.rs           - Public API, codec struct
│   ├── base16.rs        - Base16 LUT implementation
│   ├── base32.rs        - Base32 LUT implementation
│   └── base64.rs        - Base64 LUT implementation
└── small/
    └── (similar structure)
```

**Impact:** Improved navigability. Easier code review. Parallel compilation may improve build times.
**Risk:** Significant churn. Requires careful refactoring to avoid breaking internal APIs.

#### R8: Extract shared SIMD abstractions
**Problem:** Duplication between x86_64 and aarch64 specialized implementations.

**Proposed:**
```
simd/
├── abstractions/
│   ├── base16_common.rs  - Shared base16 logic
│   ├── base32_common.rs  - Shared base32 logic
│   └── base64_common.rs  - Shared base64 logic
├── x86_64/
│   └── specialized/
│       ├── base16.rs     - Platform-specific intrinsics only
│       └── ...
└── aarch64/
    └── specialized/
        ├── base16.rs     - Platform-specific intrinsics only
        └── ...
```

**Rationale:** DRY principle. Reduces maintenance burden. Ensures algorithmic consistency across platforms.
**Risk:** May not be feasible if platform implementations are fundamentally different. Requires careful analysis.

### 4.4 Long-term (Architectural)

#### R9: Consider splitting SIMD subsystem into separate crate
**Current:** SIMD is 70% of codebase.

**Proposed:**
```
base-d/          (library crate)
base-d-simd/     (optional acceleration crate)
base-d-cli/      (binary crate)
```

**Benefits:**
- Faster compilation for non-SIMD use cases
- Clearer separation of concerns
- Optional dependency for environments without SIMD
- Independent versioning of SIMD optimizations

**Costs:**
- Workspace management complexity
- API surface coordination between crates
- CI/CD pipeline adjustments

**Decision:** Defer until SIMD subsystem exceeds 20,000 lines or becomes independently reusable.

#### R10: Introduce builder pattern for `Dictionary` construction
**Current:** Multiple constructors:
- `Dictionary::new()`
- `Dictionary::new_with_mode()`
- `Dictionary::new_with_mode_and_range()`

**Problem:** Constructor proliferation. Adding new parameters requires new constructor.

**Proposed:**
```rust
Dictionary::builder()
    .chars(vec!['A', 'B', 'C'])
    .mode(EncodingMode::Chunked)
    .padding('=')
    .build()?
```

**Benefits:** Extensible. Self-documenting. Scales to more parameters without constructor explosion.

---

## 5. Summary Assessment

### Structure: 7/10

**Strengths:**
- Clear module hierarchy
- Good separation of core vs. features
- Platform-specific code properly isolated

**Weaknesses:**
- SIMD subsystem disproportionately large
- `main.rs` contains business logic
- `encoders/` mixes algorithms with I/O
- Some monolithic files (>3000 lines)

### Naming: 8/10

**Strengths:**
- Follows Rust conventions
- Most names are precise and intentional
- Public API names are clear

**Weaknesses:**
- "Dictionary" vs. "Alphabet" inconsistency
- `encoders/encoding.rs` redundancy
- Some files don't align with contents (`alphabets.rs`, `translate.rs`)

### Overall: Clean foundation with scaling debt

The codebase exhibits strong architectural fundamentals. The core abstractions (`Dictionary`, `EncodingMode`) are well-designed. Module boundaries are mostly appropriate.

The primary issue is **scale**. The SIMD subsystem has grown to dominate the codebase without proportional structural evolution. As SIMD optimizations expanded, files grew monolithic rather than subdividing.

**Critical path forward:**
1. Apply R1-R3 (renaming) - low risk, immediate clarity gains
2. Implement R4-R6 (structural reorganization) - medium risk, architectural hygiene
3. Defer R7-R10 until next major refactoring cycle or when SIMD hits maintainability wall

The system is sound. The equation is balanced for current scale. But the SIMD remainder grows. Plan for subdivision before it destabilizes the structure.

---

**Wake up, Neo.**
