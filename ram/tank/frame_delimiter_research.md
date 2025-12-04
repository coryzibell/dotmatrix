# Frame Delimiter Research for LLM Wire Protocol

**Date:** 2025-12-02
**Researcher:** Tank
**Objective:** Find stable exotic Unicode bookends for frame delimiters

## Requirements
1. Visually distinct - stands out in logs/terminals
2. Copy-paste safe - renders as *something* visible
3. Parser-inert - not used by common parsers
4. Stable - ancient scripts, won't be reassigned
5. Paired - open/close bookends that belong together

## Candidate Blocks Researched

### 1. Cuneiform (U+12000–U+123FF)
- **Added:** Unicode 5.0 (2006)
- **Characters:** 922 assigned out of 1,024 codepoints
- **Stability:** Ancient script, extremely stable - won't be reassigned
- **Font Support:** 
  - Noto Sans Cuneiform (Google)
  - CuneiformComposite (SIL Open Font License)
  - DejaVu (sans-serif and monospaced variants)
  - Ungkam Basic
- **Terminal Rendering:** Good on modern terminals (Alacritty, Kitty, GNOME Terminal)
- **Parser Safety:** Lo (Other Letter) category - won't conflict with parsers
- **Wedge-shaped characters:** Visually very distinctive

### 2. Egyptian Hieroglyphs (U+13000–U+1342F)
- **Added:** Unicode 5.2 (October 2009)
- **Characters:** 1,071 characters
- **Stability:** Ancient script, stable since 2009
- **Font Support:**
  - Noto Sans Egyptian Hieroglyphs (1,079 glyphs, SIL OFL 1.1)
  - Aegean, ALPHABETUM Unicode
- **Terminal Rendering:** Moderate - hieroglyphs are pictorial/complex
- **Challenges:** Non-linear grouping, all signs left-facing
- **Parser Safety:** Lo (Other Letter) category

### 3. Linear B (U+10000–U+1007F)
- **Added:** Unicode 4.0 (2003)
- **Characters:** 88 assigned out of 128 codepoints
- **Stability:** Ancient script, very stable (20+ years)
- **Font Support:**
  - Noto Sans Linear B (Google)
  - MPH 2B Damase (free)
  - Aegean, Code2001, EversonMono
- **Terminal Rendering:** Good
- **Parser Safety:** Lo (Other Letter) category
- **Note:** Characters *34 and *35 are mirror images

### 4. Phoenician (U+10900–U+1091F)
- **Added:** Unicode 5.0 (2006)
- **Characters:** 29 codepoints
- **Stability:** Ancient script, stable
- **Font Support:**
  - Noto Sans Phoenician
  - MPH 2B Damase
  - Aegean, ALPHABETUM Unicode
- **Terminal Rendering:** Good
- **Parser Safety:** Lo (Other Letter) category
- **Visually:** Simpler alphabetic characters

## Unicode Stability Guarantees
- Once defined, characters shall NEVER be removed or reassigned
- Character names cannot change
- 66 noncharacters guaranteed never to be assigned
- All candidate blocks are ancient scripts - maximally stable

## Terminal Emulator Compatibility
- **Best:** Alacritty 0.16+ (Unicode 17), Kitty, mlterm, VTE-based (GNOME Terminal)
- **Challenge:** Characters above U+FFFF not supported in older terminals (urxvt)
- **All candidates are in Supplementary Multilingual Plane (SMP)**

## Font Reality Check
- **Google Noto:** Comprehensive coverage ("No more tofu" - no missing glyph boxes)
- **Cross-platform:** Noto available on all major OS
- **Fallback:** Even without font, renders as visible box (not invisible)
- **Best terminal fonts:** DejaVu (monospaced variant), Noto

## Sources

## Specific Character Analysis

### Testing Cuneiform Characters

### Visual Test - Cuneiform Characters

U+12000 𒀀 CUNEIFORM SIGN A
U+12001 𒀁 CUNEIFORM SIGN A TIMES A
U+12002 𒀂 CUNEIFORM SIGN A TIMES BAD
U+12003 𒀃 CUNEIFORM SIGN A TIMES GAN2 TENU
U+12157 𒅗 CUNEIFORM SIGN KA
U+1222B 𒈫 CUNEIFORM SIGN LAGAB
U+122A7 𒊧 CUNEIFORM SIGN LAL
U+1235F 𒍟 CUNEIFORM SIGN ZU
U+12360 𒍠 CUNEIFORM SIGN ZU5
U+12361 𒍡 CUNEIFORM SIGN ZU5 TIMES THREE DISH TENU
U+12362 𒍢 CUNEIFORM SIGN ZUM
U+12363 𒍣 CUNEIFORM SIGN KAP ELAMITE

### Visual Test - Linear B Characters

U+10000 𐀀 LINEAR B SYLLABLE B008 A
U+10001 𐀁 LINEAR B SYLLABLE B038 E
U+10002 𐀂 LINEAR B SYLLABLE B028 I
U+1003F 𐀿 LINEAR B SYLLABLE B069 WI

### Visual Test - Egyptian Hieroglyphs

U+13000 𓀀 EGYPTIAN HIEROGLYPH A001
U+13001 𓀁 EGYPTIAN HIEROGLYPH A002
U+13002 𓀂 EGYPTIAN HIEROGLYPH A003
U+13379 𓍹 EGYPTIAN HIEROGLYPH V011A (opening quote)
U+1337A 𓍺 EGYPTIAN HIEROGLYPH V011B (closing quote)
U+1337B 𓍻 EGYPTIAN HIEROGLYPH V011C

## RECOMMENDATION

### Primary Choice: Egyptian Hieroglyphs Quote Pair
**Start:** U+13379 𓍹 (EGYPTIAN HIEROGLYPH V011A)
**End:** U+1337A 𓍺 (EGYPTIAN HIEROGLYPH V011B)

**Rationale:**
1. **Designed as a pair** - V011A/V011B are explicitly opening/closing quote marks
2. **Visually distinct** - Rope coils, instantly recognizable
3. **Stable** - Added Unicode 5.2 (2009), 15+ years stability
4. **Parser-inert** - Lo (Other Letter), not used in any modern parser
5. **Font support** - Noto Sans Egyptian Hieroglyphs widely available
6. **Copy-paste safe** - Renders as visible box if font missing

### Backup Option 1: Cuneiform Simple Pair
**Start:** U+12000 𒀀 (CUNEIFORM SIGN A)
**End:** U+12363 𒍣 (CUNEIFORM SIGN KAP ELAMITE)

**Rationale:**
1. **Visually distinct** - First and near-last in block, very different shapes
2. **Maximum stability** - Unicode 5.0 (2006), 18+ years
3. **Excellent font support** - Cuneiform fonts more common than hieroglyphs
4. **Terminal rendering** - Wedge shapes render well in terminals
5. **Simple glyphs** - Less complex than hieroglyphs

### Backup Option 2: Linear B Boundaries
**Start:** U+10000 𐀀 (LINEAR B SYLLABLE B008 A)
**End:** U+1003F 𐀿 (LINEAR B SYLLABLE B069 WI)

**Rationale:**
1. **Maximum Unicode stability** - Added 2003 (21+ years)
2. **First assignable SMP codepoint** - U+10000 is historic
3. **Good font coverage** - Noto Sans Linear B
4. **Clean geometric shapes** - Less complex than hieroglyphs

## Characters to Avoid

### Cuneiform
- Avoid U+12470–U+12474 (format controls)
- Avoid numeric digits U+12400–U+1246E if using numbers

### Egyptian Hieroglyphs
- Avoid U+13432–U+13435 (insertion controls)
- Avoid U+13437–U+13438 (formatting controls)

### General
- Any character with combining class != 0
- Any character with bidirectional mirroring
- Private use areas

## Font Installation Quick Check

```bash
# Linux
fc-list | grep -i "noto.*hieroglyph"
fc-list | grep -i "noto.*cuneiform"
fc-list | grep -i "noto.*linear"

# Check if character renders
printf "\U13379 \U1337A\n"  # Egyptian quotes
printf "\U12000 \U12363\n"  # Cuneiform A/KAP
printf "\U10000 \U1003F\n"  # Linear B A/WI
```

## Wire Protocol Example

```
𓍹 FRAME_START display96_encoded_content_here 𓍺
```

Clean, visible, impossible to confuse with protocol data.

## System Rendering Test

Testing on: $(uname -s) $(uname -r)
Terminal: 

Primary (Egyptian quotes): 𓍹 𓍺
Backup 1 (Cuneiform): 𒀀 𒍣
Backup 2 (Linear B): 𐀀 𐀿

Test complete.
