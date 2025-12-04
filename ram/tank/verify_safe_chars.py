#!/usr/bin/env python3
"""
Visual verification of safe characters.
Display them grouped by range for visual inspection.
"""

import unicodedata

# The exclusion list from audit
EXCLUSIONS = [
    0x2500, 0x2502, 0x2504, 0x2506, 0x2508, 0x250A, 0x250C, 0x250D,
    0x250E, 0x2510, 0x2511, 0x2512, 0x2514, 0x2515, 0x2516, 0x2518,
    0x2519, 0x251A, 0x251C, 0x251D, 0x251E, 0x251F, 0x2520, 0x2521,
    0x2522, 0x2524, 0x2525, 0x2526, 0x2527, 0x2528, 0x2529, 0x252A,
    0x252C, 0x252D, 0x252E, 0x252F, 0x2530, 0x2531, 0x2532, 0x2534,
    0x2535, 0x2536, 0x2537, 0x2538, 0x2539, 0x253A, 0x253C, 0x253D,
    0x253E, 0x253F, 0x2540, 0x2541, 0x2542, 0x2543, 0x2544, 0x2545,
    0x2546, 0x2547, 0x2548, 0x2549, 0x254A, 0x254C, 0x254E, 0x256D,
    0x256E, 0x256F, 0x2570, 0x2571, 0x2572, 0x2573, 0x2574, 0x2575,
    0x2576, 0x2577, 0x257C, 0x257D, 0x257E, 0x257F, 0x2580, 0x2581,
    0x2582, 0x2583, 0x2584, 0x2585, 0x2586, 0x2587, 0x2589, 0x258A,
    0x258B, 0x258C, 0x258D, 0x258E, 0x258F, 0x2590, 0x2591, 0x2592,
    0x2593, 0x2594, 0x2595, 0x25A1, 0x25A2, 0x25A3, 0x25AA, 0x25AB,
    0x25AD, 0x25AF, 0x25B1, 0x25B3, 0x25B4, 0x25B5, 0x25B7, 0x25B8,
    0x25B9, 0x25BD, 0x25BE, 0x25BF, 0x25C1, 0x25C2, 0x25C3, 0x25C7,
    0x25C8, 0x25CB, 0x25CC, 0x25D9, 0x25E6, 0x25EB, 0x25EC, 0x25F0,
    0x25F1, 0x25F2, 0x25F3, 0x25F4, 0x25F5, 0x25F6, 0x25F7, 0x25FB,
    0x25FD, 0x25FE, 0x25D0, 0x25D1, 0x25D2, 0x25D3, 0x25D6, 0x25D7,
    0x25DA, 0x25DB, 0x25E0, 0x25E1, 0x25E7, 0x25E8, 0x25E9, 0x25EA,
    0x25ED, 0x25EE,
]

def get_safe_chars(start, end):
    """Get safe characters from a range."""
    return [cp for cp in range(start, end + 1) if cp not in EXCLUSIONS]

def main():
    ranges = [
        (0x2500, 0x257F, "Box Drawing"),
        (0x2580, 0x259F, "Block Elements"),
        (0x25A0, 0x25FF, "Geometric Shapes"),
    ]

    print("=" * 80)
    print("SAFE CHARACTERS - VISUAL VERIFICATION")
    print("=" * 80)
    print()

    all_safe = []

    for start, end, name in ranges:
        safe = get_safe_chars(start, end)
        all_safe.extend(safe)

        print(f"\n{name}: {len(safe)} safe characters")
        print("-" * 80)

        # Display in rows of 16
        for i in range(0, len(safe), 16):
            row = safe[i:i+16]
            # Show the characters
            chars = " ".join(chr(cp) for cp in row)
            print(f"{chars}")
            # Show their codepoints
            codes = " ".join(f"{cp:04X}" for cp in row)
            print(f"{codes}")
            print()

    print("=" * 80)
    print(f"TOTAL SAFE CHARACTERS: {len(all_safe)}")
    print("=" * 80)

    # Generate the alphabet array for use in code
    print("\n# Python array for safe alphabet:")
    print("SAFE_ALPHABET = [")
    for i in range(0, len(all_safe), 8):
        chunk = all_safe[i:i+8]
        print("    " + ", ".join(f"0x{cp:04X}" for cp in chunk) + ",")
    print("]")

    # Also show as actual string
    print("\n# As string:")
    print(f'SAFE_CHARS = "{"".join(chr(cp) for cp in all_safe)}"')
    print(f"# Length: {len(all_safe)} characters")

    # Character density check - look for any that might still be problematic
    print("\n" + "=" * 80)
    print("SPOT CHECK - Characters that might still be questionable:")
    print("=" * 80)
    for cp in all_safe:
        char = chr(cp)
        name = unicodedata.name(char, "UNKNOWN")

        # Flag anything that might still be questionable
        if any(keyword in name for keyword in ["HEAVY DOUBLE", "QUADRUPLE", "TRIPLE"]):
            print(f"U+{cp:04X} {char} {name}")
            print(f"         → May be too complex/heavy")


if __name__ == "__main__":
    main()
