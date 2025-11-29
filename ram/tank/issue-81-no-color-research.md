# Issue #81: NO_COLOR Support - Research Report

**Timestamp:** 2025-11-29
**Status:** Research Complete
**Agent:** Tank

## Issue Summary

**Title:** Add NO_COLOR support
**Number:** #81
**Repository:** coryzibell/base-d
**Labels:** identity:smith, identity:zee, high-priority, accessibility
**Status:** Open

### Problem Statement

base-d doesn't respect the `NO_COLOR` environment variable. Users who need plain output for accessibility or piping have no way to disable colors.

### Context

Identified by Zee during Construct review of base-d project.
Source: `~/.matrix/cache/construct/base-d/accessibility.md`

## NO_COLOR Standard Specification

**Standard URL:** https://no-color.org/

### Core Requirements

1. **Environment Variable:** `NO_COLOR`
2. **Activation Condition:** When present AND not empty (any value: `1`, `true`, etc.)
3. **Effect:** Prevents addition of ANSI color codes to output
4. **Override Priority:** User config files and CLI flags should take precedence
5. **Scope:** Only applies to software that outputs color by default

### Key Implementation Principle

NO_COLOR is a user preference signal, not a terminal capability check. It tells software to suppress color regardless of terminal support.

## Current Color Usage in base-d

### Dependencies

- **crossterm v0.28** - Used for keyboard event handling (not for colors)
- Located in: `/home/w3surf/work/personal/code/base-d/Cargo.toml`

### ANSI Escape Sequences Found

All color usage is concentrated in the **Matrix mode** feature:

**File:** `/home/w3surf/work/personal/code/base-d/src/cli/commands.rs`

**Function:** `matrix_mode()` (lines 98-293)

#### Specific Color Usage:

1. **Line 112:** `println!("\x1b[2J\x1b[H");` - Clear screen
2. **Line 113:** `println!("\x1b[32m");` - Set green text (Matrix theme)
3. **Line 134:** `print!("\r\x1b[K");` - Clear line (intro skip)
4. **Line 142:** `print!("\r\x1b[K");` - Clear line (between messages)
5. **Line 181:** `eprintln!("\x1b[32mDictionary: {}\x1b[0m", ...)` - Green dictionary name
6. **Line 210:** `eprintln!("\x1b[32mDictionary: {}\x1b[0m", ...)` - Green dictionary name (cycle mode)
7. **Line 233:** `eprintln!("\x1b[32mDictionary: {}\x1b[0m", ...)` - Green dictionary name (random mode)
8. **Line 265:** `eprintln!("\r\x1b[32m[Matrix: {}]\x1b[0m", ...)` - Green matrix indicator
9. **Line 276:** `eprintln!("\r\x1b[32m[Matrix: {}]\x1b[0m", ...)` - Green matrix indicator
10. **Line 283:** `eprintln!("\r\x1b[32m[Matrix: {}]\x1b[0m", ...)` - Green matrix indicator

#### ANSI Codes Used:

- `\x1b[2J` - Clear entire screen
- `\x1b[H` - Move cursor to home (0,0)
- `\x1b[32m` - Set foreground color to green
- `\x1b[0m` - Reset all attributes (color, style)
- `\x1b[K` - Clear line from cursor to end
- `\r` - Carriage return

### Other Files

**No ANSI color codes found in:**
- `/home/w3surf/work/personal/code/base-d/src/cli/config.rs`
- `/home/w3surf/work/personal/code/base-d/src/tests.rs`

**Note:** `crossterm` is imported but only used for keyboard event polling (`poll`, `read`, `Event`, `KeyCode`, `KeyEvent`) - NOT for color output.

## Implementation Requirements (from issue)

### Steps

1. Add `NO_COLOR` check at startup
2. Disable all ANSI escapes when `NO_COLOR` is set (any value)
3. Also respect `--no-color` flag for explicit control
4. Ensure Matrix mode respects this too

### Acceptance Criteria

- [ ] `NO_COLOR=1 base-d ...` produces no ANSI escapes
- [ ] `--no-color` flag works
- [ ] Matrix mode works without colors
- [ ] Piped output is clean

## Recommended Implementation Approach

### 1. Configuration Check

Add a global color configuration that checks:
1. CLI flag `--no-color` (highest priority)
2. Environment variable `NO_COLOR` (if set and non-empty)
3. Default: colors enabled

### 2. Centralized Color Helper

Create a helper function that wraps ANSI escape codes:

```rust
fn colorize(text: &str, code: &str, should_color: bool) -> String {
    if should_color {
        format!("\x1b[{}m{}\x1b[0m", code, text)
    } else {
        text.to_string()
    }
}
```

### 3. Matrix Mode Modifications

Update `matrix_mode()` to:
- Accept `should_color` parameter
- Conditionally apply all ANSI escapes
- Still provide full functionality without colors

### 4. Testing

Matrix mode without colors should:
- Skip screen clearing (`\x1b[2J\x1b[H`)
- Show plain text intro messages
- Display dictionary names without green color
- Maintain all keyboard controls and switching logic

## Files to Modify

1. **CLI argument parsing** - Add `--no-color` flag
2. **/home/w3surf/work/personal/code/base-d/src/cli/commands.rs** - Update `matrix_mode()` function
3. **Main entry point** - Add NO_COLOR environment check

## Additional Notes

- crossterm is only used for keyboard input, not color output
- All color codes are raw ANSI escapes, no abstraction layer
- Matrix mode is the ONLY feature using colors
- Implementation is straightforward - all color usage is centralized

## Handoff Recommendation

**To:** Smith (implementation)
**Then:** Zee (accessibility verification)
**Finally:** Neo (merge)

---

**Research complete. Standing by.**
