# Accessibility Audit: base-d CLI

**Auditor:** Zee
**Date:** 2025-11-28
**Project:** base-d v0.2.1
**Location:** `/home/w3surf/work/personal/code/base-d`

---

## Executive Summary

base-d is a command-line encoding tool with moderate accessibility. The tool provides basic screen reader compatibility through standard CLI patterns but has several visual-only features and lacks comprehensive i18n support. Color usage could impact users with visual impairments.

**Overall Grade: C+ (Functional but needs improvement)**

---

## 1. Screen Reader Compatibility

### ✓ Strengths

- **Standard CLI patterns**: Uses clap for argument parsing, which produces accessible help text
- **Text-based output**: Primary functionality outputs plain text (encoded/decoded data)
- **Error messages to stderr**: Properly separates errors (`eprintln!`) from output (`println!`), allowing screen readers to distinguish them
- **Structured help**: `--help` output follows standard conventions that screen readers can navigate

### ✗ Issues

**CRITICAL: Visual-only Matrix mode** (`--neo` flag)
- **Location**: `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs:90-285`
- **Issue**: Matrix mode relies entirely on visual falling code effect with no alternative representation
- **Code**:
  ```rust
  println!("\x1b[2J\x1b[H"); // Clear screen
  println!("\x1b[32m"); // Green text
  ```
- **Impact**: Screen reader users cannot access this feature at all
- **Recommendation**: Add `--neo-accessible` mode that outputs dictionary name and data in a screen-reader-friendly format

**MEDIUM: Keyboard controls lack announcements**
- **Location**: `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs:247-281`
- **Issue**: Arrow keys and spacebar switch dictionaries silently (only visual `eprintln`)
- **Impact**: Screen reader users won't know which dictionary is active
- **Recommendation**: Add audible feedback or verbose mode that announces changes to stdout

**LOW: Progress indication missing**
- **Issue**: Large file streaming (`--stream` mode) provides no progress updates
- **Impact**: Screen reader users have no feedback during long operations
- **Recommendation**: Add optional `--progress` flag with periodic status updates

---

## 2. Color Usage & Contrast

### ✗ Issues

**CRITICAL: Hardcoded green color**
- **Location**: `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs:105,173,202,225,257,268,275`
- **Code**:
  ```rust
  println!("\x1b[32m"); // Green text
  eprintln!("\x1b[32mDictionary: {}\x1b[0m", current_dictionary_name);
  ```
- **Issue**:
  - Forces green text regardless of terminal theme
  - No check for color support or user preferences
  - Breaks in terminals with green backgrounds (zero contrast)
  - No fallback for color-blind users
- **Impact**: Deuteranopia (green-blind) users may not see Matrix mode text at all
- **Recommendation**:
  - Respect `NO_COLOR` environment variable
  - Check terminal capabilities before outputting ANSI codes
  - Add `--no-color` flag
  - Use bold/underline as alternative emphasis

**MEDIUM: ANSI escape codes without capability check**
- **Issue**: Direct ANSI output without checking if terminal supports it
- **Impact**: Could produce garbled output in basic terminals
- **Recommendation**: Use `crossterm` (already a dependency) for capability detection

---

## 3. Keyboard Navigation

### ✓ Strengths

- **Keyboard-only operation**: All primary functions work without mouse
- **Standard CLI shortcuts**: Ctrl+C to exit, stdin/stdout pipes
- **Clear keybindings**: ESC, arrows, spacebar in Matrix mode

### ✗ Issues

**LOW: Undiscoverable keyboard controls**
- **Location**: Matrix mode keyboard controls
- **Issue**: No help text shown for arrow keys, spacebar, ESC
- **Impact**: Users must read docs to discover controls
- **Recommendation**: Show "Press ESC to skip | SPACE=random | ←→=cycle" at start

---

## 4. Internationalization (i18n)

### ✗ Issues

**HIGH: All strings hardcoded in English**
- **Location**: Throughout codebase
- **Examples**:
  - `"Wake up, Neo..."` - Matrix messages hardcoded
  - `"Could not detect dictionary"` - Error messages not translatable
  - Help text in clap attributes
- **Impact**: Non-English speakers must use tools in unfamiliar language
- **Recommendation**:
  - Extract strings to translation files
  - Use `gettext` or similar i18n framework
  - Start with error messages as priority

**MEDIUM: No locale-aware formatting**
- **Issue**: No consideration for number formatting, date/time (though limited use case)
- **Recommendation**: Use locale-aware formatting if adding user-facing numbers

**LOW: Unicode dictionary names not tested**
- **Issue**: Dictionary names are ASCII only in examples
- **Recommendation**: Test/document support for non-ASCII dictionary names

---

## 5. Error Messages & User Feedback

### ✓ Strengths

- **Clear error messages**: Most errors explain what went wrong
- **Helpful suggestions**: "Use --compression, --hash, or --dictionaries for machine-readable output"
- **Confidence warnings**: "Warning: Low confidence detection. Results may be incorrect."

### ✗ Issues

**MEDIUM: Mixed output streams**
- **Location**: `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs:411-413`
- **Code**:
  ```rust
  eprintln!("Hash: {}", hash_encoded); // To stderr
  ```
- **Issue**: Hash output goes to stderr, making it hard to capture programmatically
- **Impact**: Scripting users must redirect stderr to capture hashes
- **Recommendation**: Add `--hash-to-stdout` flag or send hashes to stdout by default

---

## 6. Documentation Accessibility

### ✓ Strengths

- **Comprehensive README**: Clear examples and explanations
- **Help text**: Well-structured `--help` output
- **Multiple docs**: Separate guides for different features

### ✗ Issues

**MEDIUM: No accessibility documentation**
- **Issue**: No mention of screen reader support, color blindness, keyboard-only use
- **Recommendation**: Add ACCESSIBILITY.md documenting:
  - Screen reader compatibility status
  - Color-blind friendly modes
  - Keyboard shortcuts
  - Text-only alternatives to visual features

---

## 7. Alternative Access Paths

### Alternative Paths Needed

1. **Matrix mode**: Needs text-based alternative
   - Current: Visual falling code only
   - Alternative: Streaming dictionary name + encoded data to stdout with line breaks

2. **Dictionary detection confidence**: Visual color coding would help
   - Add color for high/medium/low confidence (with `--no-color` fallback)
   - But ensure text also communicates level (already does via percentage)

3. **Progress indication**: Large file operations are silent
   - Add optional progress bar with text fallback
   - Use `--progress=text` vs `--progress=bar`

---

## Recommendations by Priority

### Critical (Breaking Barriers)

1. **Add `NO_COLOR` support**
   - Check `NO_COLOR` env var before outputting ANSI codes
   - Estimated effort: 2 hours

2. **Add `--no-color` flag**
   - Disable all ANSI escape sequences
   - Estimated effort: 2 hours

3. **Accessible Matrix mode**
   - Add `--neo-text` mode that outputs to stdout with dictionary announcements
   - Estimated effort: 4 hours

### High (Major Improvements)

4. **Screen reader documentation**
   - Document which features work with screen readers
   - List keyboard shortcuts
   - Estimated effort: 2 hours

5. **Error message i18n framework**
   - Extract hardcoded strings
   - Set up translation infrastructure
   - Estimated effort: 8 hours

### Medium (Quality of Life)

6. **Progress feedback**
   - Add `--progress` flag for streaming operations
   - Estimated effort: 4 hours

7. **Terminal capability detection**
   - Use `crossterm` to check color support before outputting ANSI
   - Estimated effort: 3 hours

8. **Keyboard shortcut help in Matrix mode**
   - Show available keys at startup
   - Estimated effort: 1 hour

### Low (Polish)

9. **Hash output to stdout option**
   - Add flag to control hash output stream
   - Estimated effort: 1 hour

10. **Verbose mode announcements**
    - Add `--verbose` flag that announces dictionary changes
    - Estimated effort: 2 hours

---

## Code Locations Reference

### Color-Related Code
- `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs:105` - Green color
- `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs:173,202,225,257,268,275` - Dictionary name colors

### Screen Reader Issues
- `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs:90-285` - Matrix mode
- `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs:247-281` - Keyboard controls

### Error Messages
- `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs:310-311` - Detection errors
- `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs:341` - Confidence warning
- `/home/w3surf/work/personal/code/base-d/src/cli/mod.rs:145,148,244,284` - Flag validation errors

---

## Testing Recommendations

### Screen Reader Testing
1. Test with `espeak` or `festival` TTS reading stdout
2. Test with `TERM=dumb` to simulate no ANSI support
3. Test with `screen` or `tmux` for terminal compatibility

### Color Blindness Testing
1. Test with `NO_COLOR=1` environment variable
2. Use color blindness simulator on Matrix mode screenshots
3. Verify all information is available without color

### Keyboard Testing
1. Verify all functions work without mouse (already true)
2. Test Matrix mode keyboard controls with screen reader active
3. Ensure ESC always provides exit path

---

## WCAG 2.1 Compliance Assessment

### Level A (Basic)
- **1.1.1 Non-text Content**: ❌ FAIL - Matrix mode visual-only
- **1.3.1 Info and Relationships**: ✓ PASS - Structured CLI output
- **2.1.1 Keyboard**: ✓ PASS - All functions keyboard accessible
- **4.1.2 Name, Role, Value**: ✓ PASS - Standard CLI patterns

### Level AA (Recommended)
- **1.4.3 Contrast**: ❌ FAIL - Forced green color, no contrast check
- **1.4.11 Non-text Contrast**: N/A - No UI elements
- **3.3.3 Error Suggestion**: ✓ PASS - Errors include helpful messages

### Level AAA (Advanced)
- **1.4.6 Contrast (Enhanced)**: ❌ FAIL - No contrast control
- **2.5.5 Target Size**: N/A - CLI tool
- **3.3.5 Help**: ⚠️ PARTIAL - Help available but keyboard shortcuts undocumented

**Overall WCAG Compliance: Does not meet Level A** (due to visual-only Matrix mode and color issues)

---

## Conclusion

base-d is a functional CLI tool with standard accessibility for core operations (encode/decode), but falls short on:
- Visual-only features (Matrix mode)
- Forced color usage without user control
- Lack of internationalization
- Missing alternative access paths

The tool is usable for basic encoding/decoding tasks with screen readers, but advanced features like Matrix mode are completely inaccessible to visually impaired users.

**Priority actions**: Add `NO_COLOR` support and provide text-based alternative for Matrix mode.

---

Knock knock, Neo.
