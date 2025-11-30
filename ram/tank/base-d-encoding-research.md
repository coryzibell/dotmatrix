# Binary-to-Text Encoding Catalog for base-d

Comprehensive research on binary-to-text encodings for the base-d library.
Research completed: 2025-11-29

---

## Table of Contents

1. [Power-of-2 Encodings](#power-of-2-encodings)
2. [Non-Power-of-2 Encodings](#non-power-of-2-encodings)
3. [Unicode-Based Encodings](#unicode-based-encodings)
4. [Legacy/Historical Encodings](#legacyhistorical-encodings)
5. [Encoding Comparison Table](#encoding-comparison-table)

---

## Power-of-2 Encodings

These encodings work with clean bit boundaries (chunk-compatible).

### Base2 (Binary)

| Property | Value |
|----------|-------|
| **Base Size** | 2 |
| **Power of 2** | Yes (2^1) |
| **Bits per char** | 1 |
| **Alphabet** | `01` |
| **Padding** | None |
| **RFC/Spec** | Multibase draft |
| **Notes** | Fundamental binary representation |

### Base4 (Quaternary)

| Property | Value |
|----------|-------|
| **Base Size** | 4 |
| **Power of 2** | Yes (2^2) |
| **Bits per char** | 2 |
| **Alphabet** | `0123` |
| **Padding** | None |
| **RFC/Spec** | No formal spec |
| **Notes** | DNA encoding uses ACGT variant |

### Base8 (Octal)

| Property | Value |
|----------|-------|
| **Base Size** | 8 |
| **Power of 2** | Yes (2^3) |
| **Bits per char** | 3 |
| **Alphabet** | `01234567` |
| **Padding** | None |
| **RFC/Spec** | Multibase draft |
| **Notes** | Unix file permissions (chmod), C/shell literals |

### Base16 (Hexadecimal)

| Property | Value |
|----------|-------|
| **Base Size** | 16 |
| **Power of 2** | Yes (2^4) |
| **Bits per char** | 4 |
| **RFC/Spec** | [RFC 4648 Section 8](https://datatracker.ietf.org/doc/html/rfc4648) |

**Standard (Uppercase):**
```
Alphabet: 0123456789ABCDEF
```

**Lowercase variant:**
```
Alphabet: 0123456789abcdef
```

| Property | Value |
|----------|-------|
| **Padding** | None |
| **Case-sensitive** | No (spec says case-insensitive) |
| **Notes** | Most common binary representation, hash displays |

### Base32 Variants

#### RFC 4648 Base32 (Standard)

| Property | Value |
|----------|-------|
| **Base Size** | 32 |
| **Power of 2** | Yes (2^5) |
| **Bits per char** | 5 |
| **RFC/Spec** | [RFC 4648 Section 6](https://datatracker.ietf.org/doc/html/rfc4648) |

```
Alphabet: ABCDEFGHIJKLMNOPQRSTUVWXYZ234567
Padding:  =
```

| Property | Value |
|----------|-------|
| **Case-sensitive** | No |
| **Padding chars** | 0, 1, 3, 4, or 6 |
| **Notes** | Avoids 0,1,8,9 to prevent confusion with O,I,B |

#### Base32hex (Extended Hex)

| Property | Value |
|----------|-------|
| **Base Size** | 32 |
| **RFC/Spec** | [RFC 4648 Section 7](https://datatracker.ietf.org/doc/html/rfc4648) |

```
Alphabet: 0123456789ABCDEFGHIJKLMNOPQRSTUV
Padding:  =
```

| Property | Value |
|----------|-------|
| **Notes** | Maintains sort order when compared bitwise |

#### Crockford's Base32

| Property | Value |
|----------|-------|
| **Base Size** | 32 (37 with check) |
| **Spec** | [crockford.com/base32.html](http://www.crockford.com/base32.html) |

```
Alphabet:      0123456789ABCDEFGHJKMNPQRSTVWXYZ
Check chars:   *~$=U (for values 32-36, modulo 37)
```

| Property | Value |
|----------|-------|
| **Padding** | None |
| **Case-sensitive** | No |
| **Excluded** | I, L, O, U |
| **Decoding aliases** | i,l -> 1; o -> 0 |
| **Notes** | Human-readable, optional checksum, hyphens ignored |

#### z-base-32

| Property | Value |
|----------|-------|
| **Base Size** | 32 |
| **Spec** | [philzimmermann.com](https://philzimmermann.com/docs/human-oriented-base-32-encoding.txt) |

```
Alphabet: ybndrfg8ejkmcpqxot1uwisza345h769
```

| Property | Value |
|----------|-------|
| **Padding** | None |
| **Case** | Lowercase only |
| **Excluded** | 0, l, v, 2 |
| **Notes** | Optimized character frequency for pronounceability. Used in Tahoe-LAFS, ZRTP |

#### Geohash Base32

| Property | Value |
|----------|-------|
| **Base Size** | 32 |
| **Spec** | De facto (geohash algorithm) |

```
Alphabet: 0123456789bcdefghjkmnpqrstuvwxyz
```

| Property | Value |
|----------|-------|
| **Padding** | None |
| **Case** | Lowercase |
| **Excluded** | a, i, l, o |
| **Notes** | Geographic coordinate encoding |

### Base64 Variants

#### RFC 4648 Base64 (Standard)

| Property | Value |
|----------|-------|
| **Base Size** | 64 |
| **Power of 2** | Yes (2^6) |
| **Bits per char** | 6 |
| **RFC/Spec** | [RFC 4648 Section 4](https://datatracker.ietf.org/doc/html/rfc4648) |

```
Alphabet: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
Padding:  =
```

| Property | Value |
|----------|-------|
| **Padding chars** | 0, 1, or 2 |
| **Efficiency** | 33% overhead (4 chars per 3 bytes) |

#### Base64url (URL-safe)

| Property | Value |
|----------|-------|
| **RFC/Spec** | [RFC 4648 Section 5](https://datatracker.ietf.org/doc/html/rfc4648) |

```
Alphabet: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_
Padding:  = (optional)
```

| Property | Value |
|----------|-------|
| **Notes** | Replaces + and / with - and _ for URL/filename safety |

#### MIME Base64

| Property | Value |
|----------|-------|
| **RFC/Spec** | [RFC 2045](https://datatracker.ietf.org/doc/html/rfc2045) |

```
Alphabet: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
Padding:  =
```

| Property | Value |
|----------|-------|
| **Line length** | Max 76 characters |
| **Line separator** | CRLF |
| **Notes** | Used in email attachments |

#### IMAP Modified Base64 (UTF-7)

| Property | Value |
|----------|-------|
| **RFC/Spec** | [RFC 3501 Section 5.1.3](https://www.rfc-editor.org/rfc/rfc3501) |

```
Alphabet: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+,
```

| Property | Value |
|----------|-------|
| **Padding** | None |
| **Shift chars** | & (shift in), - (shift out) |
| **Notes** | Uses , instead of / for IMAP mailbox names |

### Base128

| Property | Value |
|----------|-------|
| **Base Size** | 128 |
| **Power of 2** | Yes (2^7) |
| **Bits per char** | 7 |
| **Spec** | No formal RFC |

```
Alphabet: ASCII 0x00-0x7F (all 7-bit ASCII)
```

| Property | Value |
|----------|-------|
| **Padding** | Implementation-dependent |
| **Efficiency** | 14.3% overhead (8 chars per 7 bytes) |
| **Notes** | Limited use due to control characters. LEB128 is related variable-length encoding |

### Base256

| Property | Value |
|----------|-------|
| **Base Size** | 256 |
| **Power of 2** | Yes (2^8) |
| **Bits per char** | 8 |
| **Spec** | No formal RFC |

```
Alphabet: All 256 byte values (0x00-0xFF)
```

| Property | Value |
|----------|-------|
| **Notes** | Raw binary; identity encoding. Latin1/ISO-8859-1 for printable subset. PGP Word List uses words for each byte value |

---

## Non-Power-of-2 Encodings

These use radix conversion (not chunk-aligned).

### Base36

| Property | Value |
|----------|-------|
| **Base Size** | 36 |
| **Power of 2** | No |
| **Spec** | No formal RFC; Multibase draft |

```
Alphabet: 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ
```

| Property | Value |
|----------|-------|
| **Case-sensitive** | No |
| **Notes** | Case-insensitive alphanumeric. Good for URLs, identifiers |

### Base45

| Property | Value |
|----------|-------|
| **Base Size** | 45 |
| **Power of 2** | No |
| **RFC/Spec** | [RFC 9285](https://datatracker.ietf.org/doc/html/rfc9285) |

```
Alphabet: 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:
```

| Property | Value |
|----------|-------|
| **Padding** | None |
| **Efficiency** | 2 bytes -> 3 chars |
| **Notes** | Optimized for QR code alphanumeric mode. Used in COVID-19 certificates |

### Base52

| Property | Value |
|----------|-------|
| **Base Size** | 52 |
| **Power of 2** | No |
| **Spec** | No formal spec |

```
Alphabet: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```

| Property | Value |
|----------|-------|
| **Notes** | Alphabetic only (no digits). Rarely used |

### Base56

| Property | Value |
|----------|-------|
| **Base Size** | 56 |
| **Power of 2** | No |
| **Spec** | No formal RFC |

**Std variant:**
```
Alphabet: 0123456789ABCEFGHJKLMNPRSTUVWXYZabcdefghjklmnpqrstuvwxyz
Excluded: D, I, O, Q, i, o
```

**Alt variant (PHP/Java):**
```
Alphabet: 23456789abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ
Excluded: 0, 1, l, o, I, O
```

**Py3 variant:**
```
Alphabet: 23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz
```

| Property | Value |
|----------|-------|
| **Notes** | Human-readable variant of Base58 with additional exclusions |

### Base58 Variants

#### Base58 Bitcoin

| Property | Value |
|----------|-------|
| **Base Size** | 58 |
| **Power of 2** | No |
| **Spec** | De facto (Bitcoin) |

```
Alphabet: 123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz
Excluded: 0, O, I, l
```

| Property | Value |
|----------|-------|
| **Notes** | Cryptocurrency addresses. Base58Check adds 4-byte checksum |

#### Base58 Flickr

| Property | Value |
|----------|-------|
| **Spec** | De facto (Flickr short URLs) |

```
Alphabet: 123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ
```

| Property | Value |
|----------|-------|
| **Notes** | Lowercase before uppercase (inverted from Bitcoin) |

#### Base58 Ripple

| Property | Value |
|----------|-------|
| **Spec** | De facto (Ripple/XRP) |

```
Alphabet: rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz
```

| Property | Value |
|----------|-------|
| **Notes** | 'r' = 0, so all Ripple addresses start with 'r' |

### Base62

| Property | Value |
|----------|-------|
| **Base Size** | 62 |
| **Power of 2** | No |
| **Spec** | No formal RFC |

```
Alphabet: 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```

| Property | Value |
|----------|-------|
| **Case-sensitive** | Yes |
| **Notes** | URL-safe alphanumeric. URL shorteners, unique IDs |

### Base85 Variants

#### Ascii85 (Adobe/btoa)

| Property | Value |
|----------|-------|
| **Base Size** | 85 |
| **Power of 2** | No |
| **Spec** | De facto (Adobe PostScript) |

```
Alphabet: !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstu
         (ASCII 33-117)
Special:  z = all-zero group (0x00000000)
          y = all-space group (0x20202020) [btoa 4.2+]
Delimiters: <~ ... ~> (Adobe)
```

| Property | Value |
|----------|-------|
| **Efficiency** | 25% overhead (5 chars per 4 bytes) |
| **Notes** | Used in PostScript, PDF |

#### Z85 (ZeroMQ)

| Property | Value |
|----------|-------|
| **Spec** | [ZeroMQ RFC 32](https://rfc.zeromq.org/spec/32/) |

```
Alphabet: 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#
```

| Property | Value |
|----------|-------|
| **Notes** | No quotes (', "). Shell-safe. Input must be divisible by 4 |

#### RFC 1924 (IPv6)

| Property | Value |
|----------|-------|
| **Spec** | [RFC 1924](https://www.rfc-editor.org/rfc/rfc1924.txt) (April Fools) |

```
Alphabet: 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~
Excluded: "',./:[\]
```

| Property | Value |
|----------|-------|
| **Notes** | JSON-safe (no " or \). Encodes 128-bit IPv6 as 20 chars |

### Base91 (basE91)

| Property | Value |
|----------|-------|
| **Base Size** | 91 |
| **Power of 2** | No |
| **Spec** | [basE91](http://base91.sourceforge.net/) by Joachim Henke |

```
Alphabet: ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&()*+,./:;<=>?@[]^_`{|}~"
Excluded: - (dash), \ (backslash), ' (apostrophe)
```

| Property | Value |
|----------|-------|
| **Efficiency** | 14-23% overhead (13 bits -> 2 chars) |
| **Notes** | Variable-length encoding. More efficient than Base64 |

### Base92

| Property | Value |
|----------|-------|
| **Base Size** | 92 |
| **Power of 2** | No |
| **Spec** | No formal spec |

```
Alphabet: Same 91 as Base91 + ~ (tilde for empty string)
```

| Property | Value |
|----------|-------|
| **Notes** | Variant of Base91; 92nd char only for edge cases |

### Base94

| Property | Value |
|----------|-------|
| **Base Size** | 94 |
| **Power of 2** | No |
| **Spec** | No formal RFC |

```
Alphabet: !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~
         (ASCII 33-126, all printable non-space)
```

| Property | Value |
|----------|-------|
| **Efficiency** | 22% overhead (9 bytes -> 11 chars) |
| **Notes** | Maximum printable ASCII density |

### Base100 (emoji)

| Property | Value |
|----------|-------|
| **Base Size** | 256 (1:1 byte mapping) |
| **Power of 2** | Yes (2^8) |
| **Spec** | [github.com/AdamNiederer/base100](https://github.com/AdamNiederer/base100) |

```
Encoding: Each byte -> 4-byte UTF-8 emoji
Formula:  0xf0, 0x9f, ((byte+55)/64)+0x8f, (byte+55)%64+0x80
```

| Property | Value |
|----------|-------|
| **Efficiency** | 300% overhead (1 byte -> 4 bytes UTF-8) |
| **Notes** | Human-friendly for small data. Fast encoding |

### Base122

| Property | Value |
|----------|-------|
| **Base Size** | 122 |
| **Power of 2** | No |
| **Spec** | [blog.kevinalbs.com/base122](http://blog.kevinalbs.com/base122) |

```
Alphabet: 122 safe UTF-8 code points (7 bits per char)
```

| Property | Value |
|----------|-------|
| **Efficiency** | ~14% overhead |
| **Notes** | Exploits UTF-8 properties. Not good with gzip. Experimental |

---

## Unicode-Based Encodings

High-density encodings using Unicode code points.

### Ecoji (Base1024)

| Property | Value |
|----------|-------|
| **Base Size** | 1024 |
| **Power of 2** | Yes (2^10) |
| **Bits per char** | 10 |
| **Spec** | [github.com/keith-turner/ecoji](https://github.com/keith-turner/ecoji) |

```
Alphabet: 1024 emoji from Unicode 14 (V2) or Unicode 11 (V1)
Padding:  5 additional padding emoji
```

| Property | Value |
|----------|-------|
| **Encoding** | 5 bytes (40 bits) -> 4 emoji |
| **Notes** | Human-friendly emoji encoding. V2 is backwards-compatible with V1 |

### Base2048

| Property | Value |
|----------|-------|
| **Base Size** | 2048 |
| **Power of 2** | Yes (2^11) |
| **Bits per char** | 11 |
| **Spec** | [github.com/qntm/base2048](https://github.com/qntm/base2048) |

```
Alphabet: 2048 "light" Unicode code points (U+0000 to U+10FF)
Padding:  8 additional padding characters
```

| Property | Value |
|----------|-------|
| **Efficiency** | 385 bytes per 280-char Tweet |
| **Notes** | Optimized for Twitter's weighted character counting |

### Base32768

| Property | Value |
|----------|-------|
| **Base Size** | 32768 |
| **Power of 2** | Yes (2^15) |
| **Bits per char** | 15 |
| **Spec** | [github.com/qntm/base32768](https://github.com/qntm/base32768) |

```
Alphabet: 32768 safe BMP Unicode code points
```

| Property | Value |
|----------|-------|
| **Efficiency** | 93.75% in UTF-16 |
| **Notes** | Optimized for UTF-16. All chars in BMP (no surrogates) |

### Base65536

| Property | Value |
|----------|-------|
| **Base Size** | 65536 |
| **Power of 2** | Yes (2^16) |
| **Bits per char** | 16 |
| **Spec** | [github.com/qntm/base65536](https://github.com/qntm/base65536) |

```
Alphabet: 65536 safe Unicode code points (outside BMP)
```

| Property | Value |
|----------|-------|
| **Efficiency** | 280 bytes per 140-char Tweet |
| **Notes** | Uses "heavy" code points (U+1100+). Optimized for UTF-32 |

---

## Legacy/Historical Encodings

### Uuencode

| Property | Value |
|----------|-------|
| **Base Size** | 64 |
| **Power of 2** | Yes (2^6) |
| **Spec** | De facto (1980, Mary Ann Horton) |

```
Alphabet: ` !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_
         (ASCII 32-95, space to underscore)
         Note: Space (32) often replaced with ` (96)
```

| Property | Value |
|----------|-------|
| **Header** | `begin <mode> <filename>` |
| **Footer** | `end` |
| **Notes** | Legacy email encoding. Largely replaced by MIME/Base64 |

### Xxencode

| Property | Value |
|----------|-------|
| **Base Size** | 64 |
| **Power of 2** | Yes (2^6) |
| **Spec** | De facto (fix for uuencode EBCDIC issues) |

```
Alphabet: +-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```

| Property | Value |
|----------|-------|
| **Notes** | Alphanumeric + and -. More portable than uuencode |

### BinHex (HQX)

| Property | Value |
|----------|-------|
| **Base Size** | 64 |
| **Power of 2** | Yes (2^6) |
| **Spec** | [RFC 1741](https://datatracker.ietf.org/doc/html/rfc1741) |

```
Alphabet: !"#$%&'()*+,-012345689@ABCDEFGHIJKLMNPQRSTUVXYZ[`abcdefhijklmpqr
Excluded: 7, O, g, o (confusable)
```

| Property | Value |
|----------|-------|
| **Delimiters** | Starts with `:`, ends with `:` |
| **Header** | `(This file must be converted with BinHex 4.0)` |
| **Notes** | Classic Mac OS file encoding. Includes RLE compression |

### yEnc

| Property | Value |
|----------|-------|
| **Base Size** | ~252 |
| **Power of 2** | No |
| **Spec** | [yenc.org](http://www.yenc.org/yenc-draft.1.3.txt) |

```
Encoding: O = (I + 42) % 256
Critical chars (escaped): NULL (0x00), LF (0x0A), CR (0x0D), = (0x3D)
Escape sequence: = followed by (char + 64) % 256
```

| Property | Value |
|----------|-------|
| **Efficiency** | 1-2% overhead |
| **Notes** | 8-bit encoding for Usenet. Much more efficient than Base64 |

### Quoted-Printable

| Property | Value |
|----------|-------|
| **Base Size** | N/A (escape encoding) |
| **Power of 2** | No |
| **Spec** | [RFC 2045](https://datatracker.ietf.org/doc/html/rfc2045) |

```
Encoding: Non-printable bytes -> =XX (hex)
Safe chars: ASCII 33-126 except = (0x3D)
Soft line break: = at end of line
```

| Property | Value |
|----------|-------|
| **Line length** | Max 76 characters |
| **Notes** | Best for mostly-ASCII text with occasional 8-bit chars |

---

## Encoding Comparison Table

| Encoding | Base | Power of 2 | Bits/Char | Efficiency | Alphabet Size | Padding | Spec |
|----------|------|------------|-----------|------------|---------------|---------|------|
| Base2 | 2 | Yes | 1 | 12.5% | 2 | None | Multibase |
| Base4 | 4 | Yes | 2 | 25% | 4 | None | None |
| Base8 | 8 | Yes | 3 | 37.5% | 8 | None | Multibase |
| Base16 | 16 | Yes | 4 | 50% | 16 | None | RFC 4648 |
| Base32 | 32 | Yes | 5 | 62.5% | 32 | = | RFC 4648 |
| Base36 | 36 | No | ~5.17 | ~64.6% | 36 | None | Multibase |
| Base45 | 45 | No | ~5.49 | ~68.6% | 45 | None | RFC 9285 |
| Base52 | 52 | No | ~5.70 | ~71.2% | 52 | None | None |
| Base56 | 56 | No | ~5.81 | ~72.6% | 56 | None | None |
| Base58 | 58 | No | ~5.86 | ~73.2% | 58 | None | De facto |
| Base62 | 62 | No | ~5.95 | ~74.4% | 62 | None | None |
| Base64 | 64 | Yes | 6 | 75% | 64 | = | RFC 4648 |
| Base85 | 85 | No | ~6.41 | 80% | 85 | None | Various |
| Base91 | 91 | No | ~6.51 | ~81.4% | 91 | None | basE91 |
| Base94 | 94 | No | ~6.55 | ~81.9% | 94 | None | None |
| Base100 | 256 | Yes | 8 | 25%* | 256 | None | De facto |
| Base122 | 122 | No | ~6.93 | ~86.6% | 122 | None | Experimental |
| Base128 | 128 | Yes | 7 | 87.5% | 128 | Varies | None |
| Base256 | 256 | Yes | 8 | 100% | 256 | None | None |
| Ecoji | 1024 | Yes | 10 | 80%** | 1024 | 5 emoji | De facto |
| Base2048 | 2048 | Yes | 11 | 68.75%** | 2048 | 8 chars | De facto |
| Base32768 | 32768 | Yes | 15 | 93.75%** | 32768 | Varies | De facto |
| Base65536 | 65536 | Yes | 16 | 50%** | 65536 | Varies | De facto |

*Base100 efficiency is 25% because each byte becomes 4 UTF-8 bytes
**Unicode encoding efficiency varies by UTF encoding (UTF-8/16/32)

---

## Multibase Prefixes (Self-Identifying)

For interoperability, the [Multibase](https://github.com/multiformats/multibase) spec defines single-character prefixes:

| Prefix | Encoding | Status |
|--------|----------|--------|
| `0` | base2 | Experimental |
| `7` | base8 | Draft |
| `9` | base10 | Draft |
| `f` | base16 (lower) | Final |
| `F` | base16 (upper) | Final |
| `v` | base32hex (lower) | Final |
| `V` | base32hex (upper) | Final |
| `b` | base32 (lower) | Final |
| `B` | base32 (upper) | Final |
| `c` | base32pad (lower) | Draft |
| `C` | base32pad (upper) | Draft |
| `h` | base32z | Draft |
| `k` | base36 (lower) | Draft |
| `K` | base36 (upper) | Draft |
| `z` | base58btc | Final |
| `Z` | base58flickr | Experimental |
| `m` | base64 | Final |
| `M` | base64pad | Final |
| `u` | base64url | Final |
| `U` | base64urlpad | Final |

---

## Quick Reference: Alphabets

```
Base16:      0123456789ABCDEF
Base32:      ABCDEFGHIJKLMNOPQRSTUVWXYZ234567
Base32hex:   0123456789ABCDEFGHIJKLMNOPQRSTUV
Crockford:   0123456789ABCDEFGHJKMNPQRSTVWXYZ
z-base-32:   ybndrfg8ejkmcpqxot1uwisza345h769
Geohash:     0123456789bcdefghjkmnpqrstuvwxyz
Base36:      0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ
Base45:      0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:
Base52:      ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
Base58btc:   123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz
Base58flickr:123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ
Base58ripple:rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz
Base62:      0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
Base64:      ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
Base64url:   ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_
IMAP-UTF7:   ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+,
Ascii85:     !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstu
Z85:         0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#
RFC1924:     0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~
Base91:      ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&()*+,./:;<=>?@[]^_`{|}~"
Base94:      !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~
Uuencode:    `!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_
Xxencode:    +-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
BinHex:      !"#$%&'()*+,-012345689@ABCDEFGHIJKLMNPQRSTUVXYZ[`abcdefhijklmpqr
```

---

## Sources

### RFCs
- [RFC 4648 - Base16, Base32, Base64](https://datatracker.ietf.org/doc/html/rfc4648)
- [RFC 9285 - Base45](https://datatracker.ietf.org/doc/html/rfc9285)
- [RFC 2045 - MIME](https://datatracker.ietf.org/doc/html/rfc2045)
- [RFC 3501 - IMAP4](https://www.rfc-editor.org/rfc/rfc3501)
- [RFC 1924 - IPv6 Base85](https://www.rfc-editor.org/rfc/rfc1924.txt)
- [RFC 1741 - BinHex](https://datatracker.ietf.org/doc/html/rfc1741)

### Specifications
- [Crockford's Base32](http://www.crockford.com/base32.html)
- [z-base-32](https://philzimmermann.com/docs/human-oriented-base-32-encoding.txt)
- [Z85 (ZeroMQ)](https://rfc.zeromq.org/spec/32/)
- [basE91](http://base91.sourceforge.net/)
- [yEnc](http://www.yenc.org/yenc-draft.1.3.txt)
- [Multibase](https://github.com/multiformats/multibase)

### Implementations
- [Base58 Bitcoin](https://en.bitcoin.it/wiki/Base58Check_encoding)
- [Ecoji](https://github.com/keith-turner/ecoji)
- [Base2048](https://github.com/qntm/base2048)
- [Base32768](https://github.com/qntm/base32768)
- [Base65536](https://github.com/qntm/base65536)
- [Base100](https://github.com/AdamNiederer/base100)
- [Base122](http://blog.kevinalbs.com/base122)
