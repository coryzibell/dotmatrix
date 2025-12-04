# Unicode Range Audit for Display-Safe Characters

## Goal
Identify visually empty, ambiguous, or problematic characters in proposed ranges:
- Box Drawing: U+2500–U+257F (128 chars)
- Block Elements: U+2580–U+259F (32 chars)
- Geometric Shapes: U+25A0–U+25FF (96 chars)

## Audit Results

### Box Drawing (U+2500–U+257F)

#### Visually Empty/Blank Characters
None - all box drawing characters have visible lines or corners.

#### Very Thin/Light Characters (may not render at small sizes)
- U+2500–U+250B: Light horizontal/vertical lines
- U+250C–U+2513: Light corners
- U+2514–U+251B: Light corners
- U+251C–U+253F: Light intersections
- U+2574–U+2577: Light line segments (partial lines)
- U+257A–U+257B: Light line segments
- U+257E–U+257F: Light line segments

**Problem**: "Light" variants use thin lines that may be invisible at small font sizes or on low-DPI displays.

#### Confusable Pairs
- Light vs Heavy variants (e.g., U+2500 ─ vs U+2501 ━)
- Similar intersection types (many 4-way vs 3-way intersections look similar)
- Rounded vs square corners at small sizes

### Block Elements (U+2580–U+259F)

#### Visually Empty/Blank Characters
None in the traditional sense, but:
- U+2591 ░ (light shade) - very light, might look empty on some displays
- U+2592 ▒ (medium shade) - could be confused with light shade
- U+2580 ▀ (upper half block) - on some terminals, might render oddly

#### Confusable Pairs
- U+2588 █ (full block) vs U+25A0 ■ (black square from Geometric)
- U+2591 ░, U+2592 ▒, U+2593 ▓ (shade progression - may look similar)
- Upper/lower half blocks vs quarter blocks (orientation confusion)

### Geometric Shapes (U+25A0–U+25FF)

#### Visually Empty/Blank Characters
**CRITICAL ISSUES**:
- U+25A1 □ WHITE SQUARE - outline only, looks like space on many displays
- U+25AB ▫ WHITE SMALL SQUARE - tiny outline, nearly invisible
- U+25AD ▭ WHITE RECTANGLE - outline only
- U+25AF ▯ WHITE VERTICAL RECTANGLE - outline only
- U+25B1 ◱ WHITE PARALLELOGRAM - outline only
- U+25B3 △ WHITE UP-POINTING TRIANGLE - outline only
- U+25B5 ▵ WHITE UP-POINTING SMALL TRIANGLE - outline, very small
- U+25B7 ▷ WHITE RIGHT-POINTING TRIANGLE - outline only
- U+25B9 ▹ WHITE RIGHT-POINTING SMALL TRIANGLE - outline, very small
- U+25BB ▻ WHITE RIGHT-POINTING POINTER - outline only
- U+25BD ▽ WHITE DOWN-POINTING TRIANGLE - outline only
- U+25BF ▿ WHITE DOWN-POINTING SMALL TRIANGLE - outline, very small
- U+25C1 ◁ WHITE LEFT-POINTING TRIANGLE - outline only
- U+25C3 ◃ WHITE LEFT-POINTING SMALL TRIANGLE - outline, very small
- U+25C5 ◅ WHITE LEFT-POINTING POINTER - outline only
- U+25C7 ◇ WHITE DIAMOND - outline only
- U+25C9 ◉ FISHEYE - has white center, variable rendering
- U+25CB ○ WHITE CIRCLE - outline only, very common confusion with O/0
- U+25CD ◍ CIRCLE WITH VERTICAL FILL - complex, renders poorly
- U+25D0 ◐ CIRCLE WITH LEFT HALF BLACK - half-filled, ambiguous
- U+25D1 ◑ CIRCLE WITH RIGHT HALF BLACK - half-filled, ambiguous
- U+25E6 ◦ WHITE BULLET - very small outline circle
- U+25EF ◯ LARGE CIRCLE - outline only

#### Confusable with ASCII/Common Characters
- U+25CB ○ vs ASCII 'O' and digit '0'
- U+25A1 □ vs space character
- U+25B2 ▲ vs U+25B4 ▴ (size difference only)
- U+25C6 ◆ vs U+25C7 ◇ (filled vs outline - critical difference)

#### Size Variants (confusable)
Many shapes have SMALL variants that are nearly identical at normal sizes:
- U+25B2 ▲ vs U+25B4 ▴ (triangles)
- U+25BA ► vs U+25B8 ▸ (pointers)
- etc.

## Testing Plan
