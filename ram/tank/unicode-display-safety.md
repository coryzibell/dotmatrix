# Unicode Display Safety Research
## For Schema-Aware Encoding System

Research conducted: 2025-12-02
Operator: Tank

---

## 1. RECOMMENDED UNICODE RANGES

### Tier 1: Maximum Safety (Near-Universal Support)

| Range | Block Name | Count | Notes |
|-------|------------|-------|-------|
| U+0020–U+007E | Basic Latin (printable ASCII) | 95 | Universal, but limited space |
| U+00A0–U+00FF | Latin-1 Supplement | 96 | Very safe, Western European support |
| U+2500–U+257F | Box Drawing | 128 | Excellent terminal support, visually distinct |
| U+2580–U+259F | Block Elements | 32 | Progress bars, fills - very safe |
| U+25A0–U+25FF | Geometric Shapes | 96 | Squares, circles, triangles - good support |
| U+2190–U+21FF | Arrows | 112 | Directional indicators, widely supported |

**Total Tier 1: ~559 characters** (excluding ASCII overlap)

### Tier 2: Good Support (Modern Systems)

| Range | Block Name | Count | Notes |
|-------|------------|-------|-------|
| U+2200–U+22FF | Mathematical Operators | 256 | ∀∃∈∉⊂⊃∪∩ - good in modern fonts |
| U+2600–U+26FF | Miscellaneous Symbols | 256 | ☀☁★☆♠♣♥♦ - solid coverage |
| U+2700–U+27BF | Dingbats | 192 | ✓✗✔✘➔➜ - checkmarks, arrows |
| U+2300–U+23FF | Miscellaneous Technical | 256 | ⌘⌥⎋⏎ - keyboard symbols, brackets |
| U+2460–U+24FF | Enclosed Alphanumerics | 160 | ①②③ Ⓐ Ⓑ - circled numbers/letters |

**Total Tier 2: ~1,120 additional characters**

### Tier 3: Use With Caution

| Range | Block Name | Count | Caution |
|-------|------------|-------|---------|
| U+1F300–U+1F5FF | Miscellaneous Symbols & Pictographs | 768 | Emoji - rendering varies wildly |
| U+0100–U+017F | Latin Extended-A | 128 | Generally safe but check fonts |
| U+0180–U+024F | Latin Extended-B | 208 | Less common, font gaps possible |

---

## 2. RANGES TO BLACKLIST

### Absolute Avoid

| Range | Block Name | Reason |
|-------|------------|--------|
| U+0000–U+001F | C0 Controls | Control characters (NULL, CR, LF, etc.) |
| U+007F | DELETE | Control character |
| U+0080–U+009F | C1 Controls | Control characters, unpredictable rendering |
| U+E000–U+F8FF | Private Use Area (BMP) | No standard meaning, font-dependent |
| U+F0000–U+FFFFD | Supplementary PUA-A | Private Use, no guarantees |
| U+100000–U+10FFFD | Supplementary PUA-B | Private Use, no guarantees |
| U+FDD0–U+FDEF | Noncharacters | Explicitly not for text interchange |
| U+FFFE, U+FFFF | Noncharacters | Byte-order marks, internal use |
| U+D800–U+DFFF | Surrogate Pairs | UTF-16 encoding artifacts, invalid in UTF-8 |

### Combining Characters - Special Handling

| Range | Block Name | Note |
|-------|------------|------|
| U+0300–U+036F | Combining Diacritical Marks | Require base character, complex rendering |
| U+1AB0–U+1AFF | Combining Diacritical Marks Extended | Same as above |
| U+1DC0–U+1DFF | Combining Diacritical Marks Supplement | Same as above |
| U+20D0–U+20FF | Combining Diacritical Marks for Symbols | Same as above |
| U+FE20–U+FE2F | Combining Half Marks | Same as above |

**Avoid combining characters unless you have strong normalization guarantees.**

### Width Issues - Avoid for Data Encoding

| Range | Block Name | Issue |
|-------|------------|-------|
| U+3000–U+303F | CJK Symbols and Punctuation | Wide characters, alignment issues |
| U+4E00–U+9FFF | CJK Unified Ideographs | Wide characters, 20,000+ chars |
| U+AC00–U+D7AF | Hangul Syllables | Wide characters, 11,000+ chars |
| U+FF00–U+FFEF | Halfwidth/Fullwidth Forms | Mixed width, confusing |

---

## 3. DELIMITER CHARACTERS

For schema syntax like `users[3]{id,name}:encoded_data`

### ASCII Delimiters (Maximum Safety)

| Char | Unicode | Name | Use Case | Conflict Risk |
|------|---------|------|-----------|---------------|
| `:` | U+003A | Colon | Schema separator | URLs, time, JSON keys |
| `[` `]` | U+005B U+005D | Square brackets | Array indexing | Arrays, IPv6 |
| `{` `}` | U+007B U+007D | Curly braces | Field selection | JSON, code blocks |
| `|` | U+007C | Vertical bar | Field separator | Shell pipes, regex |
| `;` | U+003B | Semicolon | Statement separator | SQL, code |
| `@` | U+0040 | At sign | Metadata marker | Email, mentions |
| `~` | U+007E | Tilde | Placeholder/variant | Home dir, regex |
| `` ` `` | U+0060 | Backtick | Literal marker | Markdown, shell |

**Recommendation:** Stick with your current ASCII set. They're universally safe, readable, and understood.

### Unicode Alternatives (If You Want Distinct Delimiters)

| Char | Unicode | Name | Advantage |
|------|---------|------|-----------|
| `‹` `›` | U+2039 U+203A | Single guillemets | Distinct from < >, rarely used in data |
| `⟨` `⟩` | U+27E8 U+27E9 | Math angle brackets | Clear nesting, math context |
| `⦃` `⦄` | U+2983 U+2984 | White curly brackets | Visually distinct from {} |
| `⦗` `⦘` | U+2997 U+2998 | Black tortoise shell brackets | Very unique |
| `∷` | U+2237 | Proportion | Distinct separator (like ::) |
| `⦂` | U+2982 | Z notation type colon | Distinct from : |
| `⁞` | U+205E | Vertical four dots | Field separator |
| `⫿` | U+2AFF | N-ary white vertical bar | Distinct from | |

**Caution:** Unicode delimiters require good font support. Test thoroughly.

### Recommended Delimiter Set

For maximum compatibility:

```
Schema:   :   (colon)
Arrays:   []  (square brackets)
Fields:   {}  (curly braces)
Separator: |  (vertical bar)
Literal:  `   (backtick)
Metadata: @   (at sign)
```

**Alternative if you want visual distinction:**

```
Schema:   ∷   (U+2237 - proportion)
Arrays:   ⟦⟧  (U+27E6 U+27E7 - math white brackets)
Fields:   ⟨⟩  (U+27E8 U+27E9 - math angle brackets)
Separator: ⫿  (U+2AFF - vertical bar variant)
```

---

## 4. EXISTING STANDARDS & PRIOR ART

### Base64/Base85/BaseN Encodings

- Base64: Uses A-Z, a-z, 0-9, +, / (64 chars)
- Base85: Uses ASCII 33-117 (85 chars)
- Base91: Uses ASCII 33-126 minus backslash, single quote (91 chars)

**Lesson:** Stay in ASCII printable range for maximum compatibility.

### Emoji Keyboards & "Safe" Ranges

Modern emoji keyboards use:
- Basic Emoji: U+2600–U+26FF (Miscellaneous Symbols)
- Emoticons: U+1F600–U+1F64F
- Extended: U+1F300–U+1F9FF

**Rendering wildly inconsistent across platforms.** Avoid for data encoding.

### Terminal Font Coverage

Common monospace fonts with good Unicode coverage:
- **JetBrains Mono** - Excellent coverage of Box Drawing, Math Operators
- **Fira Code** - Good for ligatures and symbols
- **Cascadia Code** - Microsoft's modern terminal font
- **DejaVu Sans Mono** - Open source, wide coverage
- **Noto Mono** - Google's pan-language font
- **Consolas** (Windows), **SF Mono** (macOS), **Liberation Mono** (Linux)

**Safe bet:** Characters that render in DejaVu Sans Mono and Consolas will work almost everywhere.

### Unicode "Display-Safe" Guidelines

From Unicode Consortium Technical Reports:

1. **UTR #36 (Security Considerations)**: Avoid confusables, homoglyphs, invisible characters
2. **UTR #51 (Emoji)**: Emoji support is fragmented, not reliable for data
3. **UAX #9 (Bidirectional Algorithm)**: Avoid RTL marks unless you handle bidi
4. **UAX #15 (Normalization)**: Use NFC normalization for consistency

**Key takeaway:** Stick to BMP (U+0000–U+FFFF), avoid combining chars, normalize data.

### Cross-Platform Font Fallback

Safe characters are those present in:
- **Windows:** Arial Unicode MS, Segoe UI Symbol
- **macOS:** Apple Color Emoji, Helvetica Neue
- **Linux:** DejaVu, Liberation, Noto

**Intersection:** Basic Latin, Latin-1 Supplement, Box Drawing, Geometric Shapes, Arrows.

---

## 5. RECOMMENDATIONS

### For High-Density Encoding

Use **Box Drawing (U+2500–U+257F)** + **Block Elements (U+2580–U+259F)** + **Geometric Shapes (U+25A0–U+25FF)**.

- **Total: ~256 distinct, visually clear characters**
- Excellent terminal support
- Monospace-friendly
- Visually distinct (not confusable)
- Cross-platform safe

### For Maximum Compatibility

Use **ASCII printable (U+0020–U+007E)** minus delimiters.

- **Total: ~85 characters** (if you reserve 10 for delimiters)
- Universal support
- Copy-paste safe
- URL-safe subset available

### For Schema Delimiters

Stick with **ASCII**: `:`, `[`, `]`, `{`, `}`, `|`, `@`, `` ` ``

- Universally understood
- No font issues
- Easy to type and read
- Familiar from JSON, SQL, URLs

### Blacklist Summary

**Never use:**
- U+0000–U+001F (C0 controls)
- U+0080–U+009F (C1 controls)
- U+E000–U+F8FF (Private Use Area)
- U+D800–U+DFFF (Surrogates)
- Combining characters (unless you have NFC normalization)
- Wide CJK characters (for alignment reasons)
- Emoji (for consistency reasons)

---

## 6. EDGE CASES & CAVEATS

### Terminal Emulators

- **Windows cmd.exe**: Limited Unicode support, use Windows Terminal instead
- **PowerShell 5.1**: UTF-16LE internally, can be tricky with pipes
- **PowerShell 7+**: Better UTF-8 support
- **iTerm2/Terminal.app**: Excellent Unicode support on macOS
- **GNOME Terminal/Konsole**: Good support on Linux

**Test on lowest common denominator:** Windows Terminal on Windows 10+.

### Font Fallback Chains

If a glyph isn't in the primary font:
1. System checks fallback fonts
2. If no match, renders as replacement character (�, □, ?)

**Risk:** Same codepoint may render differently across systems if fallback chains differ.

### Copy-Paste Across Environments

- Some terminals normalize Unicode on paste (NFC/NFD)
- Some web apps strip certain ranges
- Some shells interpret certain characters (backticks, dollar signs)

**Mitigation:** Use ranges with consistent rendering, avoid confusables.

### Screen Readers & Accessibility

- Box drawing characters may read as "box drawing light vertical" etc.
- Some symbols have no semantic meaning to screen readers
- Consider providing alternate text representations

**If accessibility matters:** Document semantic meanings, consider ASCII fallback mode.

### Font Rendering Bugs

- Some fonts misrender Box Drawing at certain sizes
- Some terminals have ligature bugs
- Windows Terminal sometimes clips wide characters

**Mitigation:** Test at multiple terminal sizes and zoom levels.

---

## 7. FINAL RECOMMENDATIONS

### Encoding Character Set

**Option A: Conservative (ASCII)**
- Use Base91-style encoding with ASCII 33-126 minus delimiters
- ~85 usable characters
- Universal compatibility

**Option B: Expanded (Box Drawing + Geometric)**
- Use U+2500–U+259F (Box Drawing + Block Elements)
- ~160 distinct glyphs
- Excellent terminal support
- Visually distinct

**Option C: Maximum Density (BMP Safe Subset)**
- Combine Tier 1 ranges (Box Drawing, Geometric, Arrows, Block Elements)
- ~500+ distinct glyphs
- Good modern terminal support
- Requires thorough testing

### Delimiter Set (Final)

Stick with ASCII for schema syntax:

```
users[3]{id,name}:encoded_data
```

- `:` separates schema from data
- `[]` for array indexing
- `{}` for field selection
- `|` for multi-field separator (if needed)

**These are battle-tested in URLs, JSON, SQL, and shell syntax.**

### Blacklist (Final)

Exclude:
- U+0000–U+001F, U+007F, U+0080–U+009F (controls)
- U+E000–U+F8FF (PUA)
- U+D800–U+DFFF (surrogates)
- U+0300–U+036F (combining marks)
- U+FDD0–U+FDEF, U+FFFE, U+FFFF (noncharacters)
- Emoji ranges (inconsistent rendering)
- CJK ranges (width issues)

---

## DELIVERY SUMMARY

1. **Recommended ranges:**
   - Tier 1 (max safety): Box Drawing, Block Elements, Geometric Shapes, Arrows (~559 chars)
   - Tier 2 (good support): Math Operators, Misc Symbols, Dingbats (~1,120 chars)

2. **Blacklist:**
   - Controls, PUA, Surrogates, Combining marks, Emoji, CJK

3. **Delimiters:**
   - ASCII recommended: `:`, `[]`, `{}`, `|`, `@`, `` ` ``
   - Unicode alternatives available but risky

4. **Prior art:**
   - Base64/85/91 stick to ASCII for good reason
   - Terminal fonts converge on Box Drawing and Geometric Shapes
   - Unicode standards warn against confusables and invisible chars

**Risk mitigation:** Test on Windows Terminal, macOS Terminal, and Linux gnome-terminal before deploying.

Intel complete. You've got what you need.
