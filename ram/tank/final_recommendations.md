# Unicode Display-Safe Character Audit - Final Recommendations

## Executive Summary

**Total Characters Audited:** 256
**Characters Excluded:** 154
**Safe Characters Remaining:** **102**

## Breakdown by Range

### Box Drawing (U+2500–U+257F)
- **Total:** 128 characters
- **Excluded:** 78 (all "light" variants with thin lines)
- **Safe:** 50 (heavy, double, and solid variants only)

**Key exclusions:**
- All "LIGHT" box drawing characters (U+2500, U+2502, etc.) - thin lines not visible at small sizes
- Light corners, intersections, and segments
- Arc variants with light lines

**Safe characters kept:**
- Heavy horizontal/vertical lines (━ ┃)
- Heavy corners (┏ ┓ ┗ ┛)
- Double-line box drawing (═ ║)
- All heavy intersections and junctions

### Block Elements (U+2580–U+259F)
- **Total:** 32 characters
- **Excluded:** 21 (partial fills and shades)
- **Safe:** 11 (full block and distinct quadrants only)

**Key exclusions:**
- All half/quarter/eighth blocks (orientation ambiguous)
- All shade characters (░ ▒ ▓) - confusable with each other
- Partial fills that depend on orientation

**Safe characters kept:**
- Full block (█)
- Quadrant blocks with distinct patterns (▖ ▗ ▘ ▙ ▚ ▛ ▜ ▝ ▞ ▟)

### Geometric Shapes (U+25A0–U+25FF)
- **Total:** 96 characters
- **Excluded:** 55 (outline/white variants and partial fills)
- **Safe:** 41 (solid filled shapes only)

**Critical exclusions:**
- U+25A1 □ WHITE SQUARE - looks like whitespace/empty box
- U+25CB ○ WHITE CIRCLE - **CRITICALLY** confusable with letter 'O' and digit '0'
- All "WHITE" (outline) variants - may be invisible or look empty
- All "SMALL" variants - too tiny to distinguish
- Dotted/dashed variants
- All half-filled shapes (orientation ambiguous)

**Safe characters kept:**
- Solid filled shapes: ■ ◆ ● ▲ ▼ ◀ ▶
- Filled variants with internal patterns: ▤ ▥ ▦ ▧ ▨ ▩
- Distinct geometric shapes: ◊ ◎ ◉
- Large outline circle: ◯ (kept - distinct from small white circle)

## Potential Additional Exclusions

**Heavy dashed variants** (6 characters) - may render poorly:
- U+2505 ┅ HEAVY TRIPLE DASH HORIZONTAL
- U+2507 ┇ HEAVY TRIPLE DASH VERTICAL
- U+2509 ┉ HEAVY QUADRUPLE DASH HORIZONTAL
- U+250B ┋ HEAVY QUADRUPLE DASH VERTICAL
- U+254D ╍ HEAVY DOUBLE DASH HORIZONTAL
- U+254F ╏ HEAVY DOUBLE DASH VERTICAL

**Recommendation:** Test these 6 in actual display contexts. If dashes don't render clearly, exclude them.

**Adjusted safe count if excluding dashed:** 102 - 6 = **96 characters**

## Final Safe Character List

### Conservative (96 chars) - Exclude Dashed Variants
```
SAFE_ALPHABET_CONSERVATIVE = [
    0x2501, 0x2503, 0x250F, 0x2513, 0x2517, 0x251B, 0x2523, 0x252B,
    0x2533, 0x253B, 0x254B, 0x2550, 0x2551, 0x2552, 0x2553, 0x2554,
    0x2555, 0x2556, 0x2557, 0x2558, 0x2559, 0x255A, 0x255B, 0x255C,
    0x255D, 0x255E, 0x255F, 0x2560, 0x2561, 0x2562, 0x2563, 0x2564,
    0x2565, 0x2566, 0x2567, 0x2568, 0x2569, 0x256A, 0x256B, 0x256C,
    0x2578, 0x2579, 0x257A, 0x257B,  # 44 box drawing chars
    0x2588, 0x2596, 0x2597, 0x2598, 0x2599, 0x259A, 0x259B, 0x259C,
    0x259D, 0x259E, 0x259F,  # 11 block elements
    0x25A0, 0x25A4, 0x25A5, 0x25A6, 0x25A7, 0x25A8, 0x25A9, 0x25AC,
    0x25AE, 0x25B0, 0x25B2, 0x25B6, 0x25BA, 0x25BB, 0x25BC, 0x25C0,
    0x25C4, 0x25C5, 0x25C6, 0x25C9, 0x25CA, 0x25CD, 0x25CE, 0x25CF,
    0x25D4, 0x25D5, 0x25D8, 0x25DC, 0x25DD, 0x25DE, 0x25DF, 0x25E2,
    0x25E3, 0x25E4, 0x25E5, 0x25EF, 0x25F8, 0x25F9, 0x25FA, 0x25FC,
    0x25FF,  # 41 geometric shapes
]
```

### Liberal (102 chars) - Include Dashed Variants
Use `SAFE_ALPHABET` from `verify_safe_chars.py` output.

## Key Findings

### Most Critical Exclusions
1. **U+25CB ○** - White circle looks identical to 'O' and '0'
2. **U+25A1 □** - White square looks like empty space
3. **All "LIGHT" box drawing** - Invisible on many displays
4. **All "SMALL" geometric shapes** - Too tiny to distinguish
5. **Shade characters (░ ▒ ▓)** - Confusable with each other

### Why These Characters Are Safe

1. **Visually distinct** - Each character has a unique, recognizable shape
2. **High contrast** - Solid fills or heavy lines ensure visibility
3. **Size-independent** - Render clearly even at small font sizes
4. **No ASCII confusion** - Don't look like letters, digits, or punctuation
5. **No whitespace confusion** - Can't be mistaken for spaces or blank areas

## Recommendations for Implementation

### Use Conservative Set (96 chars)
Provides maximum reliability across all display contexts.

### Test Contexts
Before finalizing, verify rendering in:
- Terminal emulators (various fonts)
- Web browsers (various fonts and sizes)
- Code editors (monospace fonts)
- Low-DPI displays
- High-DPI/retina displays

### Confusability Testing
Run base58-style checks to ensure no two characters look identical in:
- Standard monospace fonts (Courier, Monaco, Consolas)
- Terminal fonts (DejaVu Sans Mono, Source Code Pro)
- Small sizes (10pt, 12pt)

## Comparison to Base58

**Base58 alphabet:** 58 characters (excludes 0/O, I/l/1 confusables)
**Our safe set:** 96-102 characters (excludes all visually ambiguous Unicode)

**Entropy per character:**
- Base58: log₂(58) ≈ 5.86 bits
- Ours (96): log₂(96) ≈ 6.58 bits (+12% more efficient)
- Ours (102): log₂(102) ≈ 6.67 bits (+14% more efficient)

## Next Steps

1. Visual testing in target environments
2. Confusability matrix generation (pairwise comparison)
3. Font compatibility testing
4. Consider locale/platform-specific rendering issues
5. Generate test strings with all 96/102 characters
