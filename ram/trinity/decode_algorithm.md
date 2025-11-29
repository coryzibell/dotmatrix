# Base64 Decode Algorithm

## x86 SSSE3 Implementation

```rust
let merge_ab_and_bc = _mm_maddubs_epi16(indices, _mm_set1_epi32(0x01400140u32 as i32));
let final_32bit = _mm_madd_epi16(merge_ab_and_bc, _mm_set1_epi32(0x00011000u32 as i32));
```

### Stage 1: maddubs_epi16

`_mm_maddubs_epi16(a, b)` performs:
- Treats `a` as unsigned 8-bit, `b` as signed 8-bit
- Multiplies corresponding bytes: `a[i] * b[i]`
- Adds adjacent pairs: `result[i] = a[2i] * b[2i] + a[2i+1] * b[2i+1]`
- Returns 16-bit signed results

Constants: `0x01400140` repeated
- As bytes: `[0x40, 0x01, 0x40, 0x01]` (little endian)
- Decimal: `[64, 1, 64, 1]`

For indices [a, b, c, d]:
- Pair 0-1: `a * 0x40 + b * 0x01 = a * 64 + b` (16-bit result)
- Pair 2-3: `c * 0x40 + d * 0x01 = c * 64 + d` (16-bit result)

This merges pairs of 6-bit values:
- First pair (a,b): `(a << 6) | b`
- Second pair (c,d): `(c << 6) | d`

### Stage 2: madd_epi16

`_mm_madd_epi16(a, b)` performs:
- Multiplies 16-bit signed values
- Adds adjacent pairs
- Returns 32-bit signed results

Constants: `0x00011000`
- As 16-bit words: `[0x1000, 0x0001]` (little endian)
- Decimal: `[4096, 1]`

For 16-bit values [ab, cd]:
- Result: `ab * 0x1000 + cd * 0x0001 = ab * 4096 + cd`
- This is: `(ab << 12) | cd`

### Complete Flow

Input: 4 indices [a, b, c, d] (6-bit each)

Stage 1:
- ab = (a << 6) | b  (12 bits)
- cd = (c << 6) | d  (12 bits)

Stage 2:
- result = (ab << 12) | cd  (24 bits in 32-bit container)

Result in 32-bit little-endian:
```
Bits:  [31-24][23-16][15-8][7-0]
Data:  [  0  ][ ab  ][ cd ][  ]
Bytes: [  0  ][byte0][byte1][byte2]
```

Where:
- byte0 = ab[11:4] = a[5:0] << 2 | b[5:4]
- byte1 = ab[3:0] << 4 | cd[11:8] = b[3:0] << 4 | c[5:2]
- byte2 = cd[7:0] = c[1:0] << 6 | d[5:0]

Stage 3: Shuffle extracts bytes in reverse order: [2,1,0] to fix endianness

## NEON Implementation (Current - BROKEN)

```rust
let pairs = vreinterpretq_u16_u8(indices);
let even = vandq_u16(pairs, vdupq_n_u16(0xFF));
let odd = vshrq_n_u16(pairs, 8);
let merge_result = vaddq_u16(even, vshlq_n_u16(odd, 6));
```

This is trying to emulate maddubs but with ADD instead of proper multiply-add!

### Problem

The NEON code does:
```
even + (odd << 6)
```

But pairs are reinterpreted in little-endian:
- For indices [a, b, ...], pairs[0] = b << 8 | a (little endian u16)
- even = a
- odd = b
- Result: a + (b << 6)

This is BACKWARDS! Should be: b + (a << 6)

Actually wait, let me check the byte order...

Input indices (as bytes): [19, 22, 5, 46, ...]
Reinterpret as u16 LE: [0x1613, 0x2E05, ...]

even = and(0x1613, 0x00FF) = 0x0013 = 19 ✓
odd = 0x1613 >> 8 = 0x0016 = 22 ✓

merge = 19 + (22 << 6) = 19 + 1408 = 1427 = 0x0593

But we want: (19 << 6) | 22 = 1216 | 22 = 1238 = 0x04D6

The formula is WRONG. It should be:
```
(even << 6) | odd
```

Not:
```
even + (odd << 6)
```

## Fix for NEON

Stage 1 should be:
```rust
let pairs = vreinterpretq_u16_u8(indices);
let even = vandq_u16(pairs, vdupq_n_u16(0xFF));
let odd = vshrq_n_u16(pairs, 8);
let merge_result = vorrq_u16(vshlq_n_u16(even, 6), odd); // FIX: OR not ADD, shift EVEN not ODD
```

No wait, that's still wrong. Let me think about the bit layout again...

For base64 decode:
- 4 chars (6 bits each) -> 3 bytes (8 bits each)
- char0[5:0] char1[5:0] char2[5:0] char3[5:0] (24 bits total)

Target byte layout:
- byte0[7:0] = char0[5:0] char1[5:4]
- byte1[7:0] = char1[3:0] char2[5:2]
- byte2[7:0] = char2[1:0] char3[5:0]

The maddubs trick:
- char0 * 64 + char1 = (char0 << 6) + char1 = 12-bit value with char0 in upper 6 bits, char1 in lower 6 bits
- When shifted and merged properly, this gives us the byte boundaries

Actually, I think the NEON implementation needs to properly emulate maddubs which does:
```
result[i/2] = a[i] * b[i] + a[i+1] * b[i+1]
```

With b = [64, 1, 64, 1]:
```
result[0] = a[0] * 64 + a[1] * 1 = char0 * 64 + char1
result[1] = a[2] * 64 + a[3] * 1 = char2 * 64 + char3
```

So the NEON code should multiply by [64, 1] not just shift one side!
