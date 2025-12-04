# Unicode Display-Safe Character Exclusion List

## Summary

**Original ranges:** 256 characters (U+2500–U+257F, U+2580–U+259F, U+25A0–U+25FF)
**Excluded:** 154 characters
**Safe remaining:** **102 characters**

## Complete Exclusion List (154 characters)

### Box Drawing Exclusions (78 characters)
All "LIGHT" variants - thin lines not visible at small sizes:

```python
BOX_DRAWING_EXCLUSIONS = [
    # Light horizontal and vertical
    0x2500, 0x2502, 0x2504, 0x2506, 0x2508, 0x250A,

    # Light corners
    0x250C, 0x250D, 0x250E, 0x2510, 0x2511, 0x2512,
    0x2514, 0x2515, 0x2516, 0x2518, 0x2519, 0x251A,

    # Light intersections and junctions
    0x251C, 0x251D, 0x251E, 0x251F, 0x2520, 0x2521, 0x2522,
    0x2524, 0x2525, 0x2526, 0x2527, 0x2528, 0x2529, 0x252A,
    0x252C, 0x252D, 0x252E, 0x252F, 0x2530, 0x2531, 0x2532,
    0x2534, 0x2535, 0x2536, 0x2537, 0x2538, 0x2539, 0x253A,
    0x253C, 0x253D, 0x253E, 0x253F, 0x2540, 0x2541, 0x2542,
    0x2543, 0x2544, 0x2545, 0x2546, 0x2547, 0x2548, 0x2549,
    0x254A, 0x254C, 0x254E,

    # Light arcs and diagonals
    0x256D, 0x256E, 0x256F, 0x2570, 0x2571, 0x2572, 0x2573,

    # Light segments and mixed
    0x2574, 0x2575, 0x2576, 0x2577, 0x257C, 0x257D, 0x257E, 0x257F,
]
```

### Block Elements Exclusions (21 characters)
Half/partial fills (orientation ambiguous) and shade characters (confusable):

```python
BLOCK_ELEMENTS_EXCLUSIONS = [
    # Half and partial blocks - orientation ambiguous
    0x2580,  # ▀ UPPER HALF BLOCK
    0x2581,  # ▁ LOWER ONE EIGHTH BLOCK
    0x2582,  # ▂ LOWER ONE QUARTER BLOCK
    0x2583,  # ▃ LOWER THREE EIGHTHS BLOCK
    0x2584,  # ▄ LOWER HALF BLOCK
    0x2585,  # ▅ LOWER FIVE EIGHTHS BLOCK
    0x2586,  # ▆ LOWER THREE QUARTERS BLOCK
    0x2587,  # ▇ LOWER SEVEN EIGHTHS BLOCK
    0x2589,  # ▉ LEFT SEVEN EIGHTHS BLOCK
    0x258A,  # ▊ LEFT THREE QUARTERS BLOCK
    0x258B,  # ▋ LEFT FIVE EIGHTHS BLOCK
    0x258C,  # ▌ LEFT HALF BLOCK
    0x258D,  # ▍ LEFT THREE EIGHTHS BLOCK
    0x258E,  # ▎ LEFT ONE QUARTER BLOCK
    0x258F,  # ▏ LEFT ONE EIGHTH BLOCK
    0x2590,  # ▐ RIGHT HALF BLOCK

    # Shade characters - confusable with each other
    0x2591,  # ░ LIGHT SHADE
    0x2592,  # ▒ MEDIUM SHADE
    0x2593,  # ▓ DARK SHADE

    # Tiny blocks
    0x2594,  # ▔ UPPER ONE EIGHTH BLOCK
    0x2595,  # ▕ RIGHT ONE EIGHTH BLOCK
]
```

### Geometric Shapes Exclusions (55 characters)
"WHITE" (outline) variants, "SMALL" variants, and half-filled shapes:

```python
GEOMETRIC_SHAPES_EXCLUSIONS = [
    # WHITE/outline variants - may look empty or like whitespace
    0x25A1,  # □ WHITE SQUARE **CRITICAL - looks like space**
    0x25A2,  # ▢ WHITE SQUARE WITH ROUNDED CORNERS
    0x25A3,  # ▣ WHITE SQUARE CONTAINING BLACK SMALL SQUARE
    0x25AB,  # ▫ WHITE SMALL SQUARE
    0x25AD,  # ▭ WHITE RECTANGLE
    0x25AF,  # ▯ WHITE VERTICAL RECTANGLE
    0x25B1,  # ▱ WHITE PARALLELOGRAM
    0x25B3,  # △ WHITE UP-POINTING TRIANGLE
    0x25B5,  # ▵ WHITE UP-POINTING SMALL TRIANGLE
    0x25B7,  # ▷ WHITE RIGHT-POINTING TRIANGLE
    0x25B9,  # ▹ WHITE RIGHT-POINTING SMALL TRIANGLE
    0x25BD,  # ▽ WHITE DOWN-POINTING TRIANGLE
    0x25BF,  # ▿ WHITE DOWN-POINTING SMALL TRIANGLE
    0x25C1,  # ◁ WHITE LEFT-POINTING TRIANGLE
    0x25C3,  # ◃ WHITE LEFT-POINTING SMALL TRIANGLE
    0x25C7,  # ◇ WHITE DIAMOND
    0x25C8,  # ◈ WHITE DIAMOND CONTAINING BLACK SMALL DIAMOND
    0x25CB,  # ○ WHITE CIRCLE **CRITICAL - looks like O/0**
    0x25D9,  # ◙ INVERSE WHITE CIRCLE
    0x25E6,  # ◦ WHITE BULLET
    0x25EB,  # ◫ WHITE SQUARE WITH VERTICAL BISECTING LINE
    0x25EC,  # ◬ WHITE UP-POINTING TRIANGLE WITH DOT
    0x25F0,  # ◰ WHITE SQUARE WITH UPPER LEFT QUADRANT
    0x25F1,  # ◱ WHITE SQUARE WITH LOWER LEFT QUADRANT
    0x25F2,  # ◲ WHITE SQUARE WITH LOWER RIGHT QUADRANT
    0x25F3,  # ◳ WHITE SQUARE WITH UPPER RIGHT QUADRANT
    0x25F4,  # ◴ WHITE CIRCLE WITH UPPER LEFT QUADRANT
    0x25F5,  # ◵ WHITE CIRCLE WITH LOWER LEFT QUADRANT
    0x25F6,  # ◶ WHITE CIRCLE WITH LOWER RIGHT QUADRANT
    0x25F7,  # ◷ WHITE CIRCLE WITH UPPER RIGHT QUADRANT
    0x25FB,  # ◻ WHITE MEDIUM SQUARE
    0x25FD,  # ◽ WHITE MEDIUM SMALL SQUARE

    # SMALL variants - too tiny to distinguish
    0x25AA,  # ▪ BLACK SMALL SQUARE
    0x25B4,  # ▴ BLACK UP-POINTING SMALL TRIANGLE
    0x25B8,  # ▸ BLACK RIGHT-POINTING SMALL TRIANGLE
    0x25BE,  # ▾ BLACK DOWN-POINTING SMALL TRIANGLE
    0x25C2,  # ◂ BLACK LEFT-POINTING SMALL TRIANGLE
    0x25FE,  # ◾ BLACK MEDIUM SMALL SQUARE

    # Dotted/special
    0x25CC,  # ◌ DOTTED CIRCLE

    # Half-filled shapes - orientation ambiguous
    0x25D0,  # ◐ CIRCLE WITH LEFT HALF BLACK
    0x25D1,  # ◑ CIRCLE WITH RIGHT HALF BLACK
    0x25D2,  # ◒ CIRCLE WITH LOWER HALF BLACK
    0x25D3,  # ◓ CIRCLE WITH UPPER HALF BLACK
    0x25D6,  # ◖ LEFT HALF BLACK CIRCLE
    0x25D7,  # ◗ RIGHT HALF BLACK CIRCLE
    0x25DA,  # ◚ UPPER HALF INVERSE WHITE CIRCLE
    0x25DB,  # ◛ LOWER HALF INVERSE WHITE CIRCLE
    0x25E0,  # ◠ UPPER HALF CIRCLE
    0x25E1,  # ◡ LOWER HALF CIRCLE
    0x25E7,  # ◧ SQUARE WITH LEFT HALF BLACK
    0x25E8,  # ◨ SQUARE WITH RIGHT HALF BLACK
    0x25E9,  # ◩ SQUARE WITH UPPER LEFT DIAGONAL HALF BLACK
    0x25EA,  # ◪ SQUARE WITH LOWER RIGHT DIAGONAL HALF BLACK
    0x25ED,  # ◭ UP-POINTING TRIANGLE WITH LEFT HALF BLACK
    0x25EE,  # ◮ UP-POINTING TRIANGLE WITH RIGHT HALF BLACK
]
```

## Combined Exclusion List (All 154 characters)

```python
ALL_EXCLUSIONS = [
    # Box Drawing (78)
    0x2500, 0x2502, 0x2504, 0x2506, 0x2508, 0x250A, 0x250C, 0x250D,
    0x250E, 0x2510, 0x2511, 0x2512, 0x2514, 0x2515, 0x2516, 0x2518,
    0x2519, 0x251A, 0x251C, 0x251D, 0x251E, 0x251F, 0x2520, 0x2521,
    0x2522, 0x2524, 0x2525, 0x2526, 0x2527, 0x2528, 0x2529, 0x252A,
    0x252C, 0x252D, 0x252E, 0x252F, 0x2530, 0x2531, 0x2532, 0x2534,
    0x2535, 0x2536, 0x2537, 0x2538, 0x2539, 0x253A, 0x253C, 0x253D,
    0x253E, 0x253F, 0x2540, 0x2541, 0x2542, 0x2543, 0x2544, 0x2545,
    0x2546, 0x2547, 0x2548, 0x2549, 0x254A, 0x254C, 0x254E, 0x256D,
    0x256E, 0x256F, 0x2570, 0x2571, 0x2572, 0x2573, 0x2574, 0x2575,
    0x2576, 0x2577, 0x257C, 0x257D, 0x257E, 0x257F,

    # Block Elements (21)
    0x2580, 0x2581, 0x2582, 0x2583, 0x2584, 0x2585, 0x2586, 0x2587,
    0x2589, 0x258A, 0x258B, 0x258C, 0x258D, 0x258E, 0x258F, 0x2590,
    0x2591, 0x2592, 0x2593, 0x2594, 0x2595,

    # Geometric Shapes (55)
    0x25A1, 0x25A2, 0x25A3, 0x25AA, 0x25AB, 0x25AD, 0x25AF, 0x25B1,
    0x25B3, 0x25B4, 0x25B5, 0x25B7, 0x25B8, 0x25B9, 0x25BD, 0x25BE,
    0x25BF, 0x25C1, 0x25C2, 0x25C3, 0x25C7, 0x25C8, 0x25CB, 0x25CC,
    0x25D0, 0x25D1, 0x25D2, 0x25D3, 0x25D6, 0x25D7, 0x25D9, 0x25DA,
    0x25DB, 0x25E0, 0x25E1, 0x25E6, 0x25E7, 0x25E8, 0x25E9, 0x25EA,
    0x25EB, 0x25EC, 0x25ED, 0x25EE, 0x25F0, 0x25F1, 0x25F2, 0x25F3,
    0x25F4, 0x25F5, 0x25F6, 0x25F7, 0x25FB, 0x25FD, 0x25FE,
]
```

## Rationale by Category

### Why Exclude "LIGHT" Box Drawing?
- Thin lines (~1px) often invisible at small sizes
- Poor rendering on low-DPI displays
- May disappear in terminal emulators with bold/anti-aliasing

### Why Exclude Half/Partial Blocks?
- Orientation dependence makes them ambiguous
- Progressive sizes (1/8, 1/4, 1/2) are indistinguishable at normal sizes
- Shade characters (░ ▒ ▓) look nearly identical

### Why Exclude "WHITE" Geometric Shapes?
- Outline-only rendering may be invisible on light backgrounds
- U+25A1 □ looks like empty space or input box
- U+25CB ○ critically confusable with letter 'O' and digit '0'
- Small variants too tiny to distinguish reliably

### Why Exclude "SMALL" Variants?
- Rendered at smaller scale within the character cell
- Often invisible at normal text sizes
- Indistinguishable from their regular-sized counterparts

## What We Kept (102 characters)

### Box Drawing (50 chars)
- Heavy lines (━ ┃)
- Double lines (═ ║)
- Heavy corners and intersections
- All solid, bold, clearly visible

### Block Elements (11 chars)
- Full block (█)
- Quadrant patterns (▖ ▗ ▘ ▙ ▚ ▛ ▜ ▝ ▞ ▟)
- Each with unique, recognizable pattern

### Geometric Shapes (41 chars)
- Solid filled shapes (■ ● ◆ ▲ ▼ ◀ ▶)
- Shapes with internal patterns (▤ ▥ ▦ ▧ ▨ ▩)
- Distinct, unambiguous forms

## Optional Conservative Variant

Exclude 6 additional heavy dashed characters if dash rendering is unreliable:

```python
OPTIONAL_DASHED_EXCLUSIONS = [
    0x2505,  # ┅ HEAVY TRIPLE DASH HORIZONTAL
    0x2507,  # ┇ HEAVY TRIPLE DASH VERTICAL
    0x2509,  # ┉ HEAVY QUADRUPLE DASH HORIZONTAL
    0x250B,  # ┋ HEAVY QUADRUPLE DASH VERTICAL
    0x254D,  # ╍ HEAVY DOUBLE DASH HORIZONTAL
    0x254F,  # ╏ HEAVY DOUBLE DASH VERTICAL
]
```

**Conservative count:** 96 characters

## Critical Exclusions Summary

**Must exclude:**
1. U+25CB ○ - looks like O/0
2. U+25A1 □ - looks like whitespace
3. All "LIGHT" box drawing - invisible
4. All "SMALL" shapes - too tiny
5. All shade characters - confusable

**Result:** 102 highly distinct, display-safe characters (or 96 conservative)
