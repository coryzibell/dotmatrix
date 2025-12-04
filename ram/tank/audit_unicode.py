#!/usr/bin/env python3
"""
Audit Unicode ranges for display-safe characters.
Identify problematic characters that should be excluded.
"""

import unicodedata

def audit_range(start, end, range_name):
    """Audit a Unicode range and categorize characters."""

    problematic = []
    confusable = []
    safe = []

    for codepoint in range(start, end + 1):
        char = chr(codepoint)
        name = unicodedata.name(char, "UNKNOWN")

        # Check for problematic indicators in name
        is_problematic = False
        reason = []

        # Visually empty/blank indicators
        if any(keyword in name for keyword in [
            "WHITE", "LIGHT", "DOTTED", "DASHED",
            "SMALL SQUARE", "SMALL CIRCLE", "SMALL TRIANGLE",
            "FISHEYE", "BULLSEYE", "BULLET"
        ]):
            # Special handling - not all WHITE/LIGHT are bad
            if "WHITE" in name and any(shape in name for shape in [
                "SQUARE", "RECTANGLE", "CIRCLE", "TRIANGLE",
                "DIAMOND", "PARALLELOGRAM", "BULLET"
            ]):
                is_problematic = True
                reason.append("outline/white variant - may look empty")
            elif "LIGHT" in name and "BOX" in name:
                is_problematic = True
                reason.append("light box drawing - thin lines")
            elif "SMALL" in name:
                is_problematic = True
                reason.append("small variant - may be invisible")
            elif any(x in name for x in ["DOTTED", "DASHED"]):
                is_problematic = True
                reason.append("dotted/dashed - may look empty")

        # Shade characters (confusable)
        if "SHADE" in name:
            reason.append("shade character - confusable with others")
            confusable.append((codepoint, char, name, reason))
            continue

        # Half-filled shapes (ambiguous orientation)
        if any(x in name for x in ["HALF", "QUARTER", "EIGHTH"]):
            reason.append("partial fill - orientation ambiguous")
            confusable.append((codepoint, char, name, reason))
            continue

        # Known confusables
        if char == '○':  # U+25CB - looks like O/0
            is_problematic = True
            reason.append("CRITICAL: looks like letter O or digit 0")

        if char == '□':  # U+25A1 - looks like space
            is_problematic = True
            reason.append("CRITICAL: looks like whitespace")

        if is_problematic:
            problematic.append((codepoint, char, name, reason))
        else:
            safe.append((codepoint, char, name))

    return problematic, confusable, safe


def main():
    ranges = [
        (0x2500, 0x257F, "Box Drawing"),
        (0x2580, 0x259F, "Block Elements"),
        (0x25A0, 0x25FF, "Geometric Shapes"),
    ]

    all_exclusions = []
    total_safe = 0

    print("=" * 80)
    print("UNICODE DISPLAY-SAFE CHARACTER AUDIT")
    print("=" * 80)
    print()

    for start, end, name in ranges:
        print(f"\n{'=' * 80}")
        print(f"{name}: U+{start:04X}–U+{end:04X} ({end - start + 1} characters)")
        print(f"{'=' * 80}\n")

        problematic, confusable, safe = audit_range(start, end, name)

        print(f"PROBLEMATIC (EXCLUDE): {len(problematic)} characters")
        print("-" * 80)
        for cp, char, uname, reasons in problematic:
            print(f"U+{cp:04X} {char:2s} {uname}")
            for r in reasons:
                print(f"         → {r}")

        print(f"\nCONFUSABLE (CONSIDER EXCLUDING): {len(confusable)} characters")
        print("-" * 80)
        for cp, char, uname, reasons in confusable:
            print(f"U+{cp:04X} {char:2s} {uname}")
            for r in reasons:
                print(f"         → {r}")

        print(f"\nSAFE (KEEP): {len(safe)} characters")
        print("-" * 80)
        # Group safe chars by category
        examples = safe[:10]
        for cp, char, uname in examples:
            print(f"U+{cp:04X} {char:2s} {uname}")
        if len(safe) > 10:
            print(f"... and {len(safe) - 10} more")

        all_exclusions.extend([cp for cp, _, _, _ in problematic])
        all_exclusions.extend([cp for cp, _, _, _ in confusable])
        total_safe += len(safe)

        print(f"\n{name} Summary:")
        print(f"  Total:       {end - start + 1}")
        print(f"  Problematic: {len(problematic)}")
        print(f"  Confusable:  {len(confusable)}")
        print(f"  Safe:        {len(safe)}")

    print(f"\n{'=' * 80}")
    print("FINAL SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total characters audited: {sum(end - start + 1 for start, end, _ in ranges)}")
    print(f"Total exclusions (problematic + confusable): {len(all_exclusions)}")
    print(f"Total SAFE characters: {total_safe}")

    print(f"\n{'=' * 80}")
    print("EXCLUSION LIST (codepoints to EXCLUDE)")
    print(f"{'=' * 80}")
    print("all_exclusions = [")
    for i in range(0, len(all_exclusions), 8):
        chunk = all_exclusions[i:i+8]
        print("    " + ", ".join(f"0x{cp:04X}" for cp in chunk) + ",")
    print("]")

    print(f"\nSafe character count: {total_safe}")
    print(f"Exclusion count: {len(all_exclusions)}")
    print(f"\nRecommended alphabet size: {total_safe} characters")


if __name__ == "__main__":
    main()
