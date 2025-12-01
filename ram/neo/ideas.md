# Ideas

## Agent Audio Cues

### Matrix Sound Effects on Dispatch
- **Concept:** Play film audio clips when agents are dispatched
- **Examples:**
  - Spoon: *"There is no spoon"*
  - Tank: *"Operator"*
  - Morpheus: *"Free your mind"*
  - Trinity: *"Dodge this"*
- **Implementation Options:**
  - `rodio` crate - native Rust, but needs `libasound.so` at runtime on Linux
  - Shell out to `ffplay`/`aplay`/`afplay` - more portable, external dependency
  - Consider: hook into Claude Code's hook system? Or mx CLI?
- **Research:** See `ram/tank/rust-audio-playback-research.md`

---

## base-d: Encoding Mode Auto-detection Proposal

### Problem
- `_math` suffix in dictionaries.toml is vague
- Users must manually specify encoding mode when it's inferrable
- Duplicate dictionary entries (`base64` + `base64_math`) for same alphabet

### Proposed Solution: Auto-detect Mode from Dictionary Properties

**Three encoding modes:**
1. **Chunked** - bit-group extraction (streamable, SIMD-able)
2. **Radix** - true base conversion via divmod (needs whole input)
3. **Byte Range** - 1:1 byte-to-codepoint mapping

**Auto-detection rule:**
- `base.is_power_of_two()` → Chunked
- Otherwise → Radix
- Byte Range always explicit (different paradigm)

### New Config Schema

**Option 1: Range definition** (sequential Unicode)
```toml
[hieroglyphs_256]
start = "𓀀"
length = 256
# auto: 256 = 2^8 → chunked
```

**Option 2: Explicit alphabet** (any characters)
```toml
[base64]
chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
# auto: 64 = 2^6 → chunked

[base58_bitcoin]
chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
# auto: 58 ≠ 2^n → radix
```

**Option 3: Byte range** (explicit mode required)
```toml
[emoji_100]
start = "😀"
length = 100
mode = "byte_range"  # 1:1 mapping
```

**Override for edge cases:**
```toml
[base64_radix]
chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
mode = "radix"  # force radix even though 64 = 2^6
```

### Migration
- Rename `math.rs` → `radix.rs`
- Rename `_math` suffix → `_radix` in dictionaries.toml (keep for posterity/compatibility)
- Update `EncodingMode::BaseConversion` → `EncodingMode::Radix`
- Add auto-detection logic in dictionary loading

### Benefits
- Eliminates duplicate dictionary entries
- Config becomes declarative (what) not imperative (how)
- `start + length` shorthand for contiguous Unicode ranges
- Existing SIMD auto-detection already handles optimization

### Questions for Architect
- Schema validation: How to handle invalid `start + length` combinations?
- Backwards compatibility: Support old `mode = "base_conversion"` as alias?
- Error messaging: What if user forces chunked on non-power-of-2?
- Performance: Any overhead from auto-detection at load time?

---

## Dojo Deep Dives

### Galois Theory + Abstract Algebra
- **Context:** kautau took high-level math in college, wants to re-up + expand
- **Topics:**
  - Galois theory fundamentals
  - Field theory
  - Group theory
  - Connection between them
  - Why quintics can't be solved by radicals
- **Format:** Dojo session with progressive questions, building from foundations

---

## Zion Enhancements

### Project Status Field
- **Context:** Compress program needs to know which projects are active vs closed
- **Problem:** Currently no status field in projects table
- **Solution:** Add `status` column (active/dormant/closed) to projects schema
- **Benefit:** Zion Control can skip archiving RAM for closed projects, keep working notes for active ones

---

## base-d: Chained Encode/Decode in Single Invocation

- **Context:** Old CLI supported `--encode base64 --decode base64` in one call
- **Removed in:** v3 subcommand refactor (test_encode_then_decode deleted)
- **Use case:** Benchmarking pure processing power and memory usage without pipe overhead
- **Future option:** Consider adding a `pipe` or `chain` subcommand if benchmarking use case becomes important
- **Example syntax:** `base-d chain "encode base64 | decode base64 | encode hex"`

---

## Git: Force Push Without Setting Upstream First

- **Context:** Lost work during mx PR #48 maintenance
- **What happened:** Used `git branch --set-upstream-to=origin/branch` before force pushing. Git saw local was "behind" remote and auto-rebased, hit conflicts, `--abort` reset to remote's old state - wiping all local changes.
- **Lesson:** When force pushing amended commits, use `git push --force origin branch-name` directly. Don't set up tracking first - it triggers rebase logic that can wipe local work.
- **Safe pattern:**
  ```bash
  git commit --amend --no-edit
  git push --force origin branch-name  # direct, no tracking dance
  ```
- **Avoid:**
  ```bash
  git branch --set-upstream-to=origin/branch  # triggers rebase
  git push --force-with-lease  # fails, tries to reconcile
  ```
