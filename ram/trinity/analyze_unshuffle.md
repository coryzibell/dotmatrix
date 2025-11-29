# Decode Unshuffle Analysis

## Input
Indices: [19, 22, 5, 46] (0x13, 0x16, 0x05, 0x2E)
Expected output: [0x4D, 0x61, 0x6E] ("Man")

## Current Algorithm (BROKEN)

```rust
// Stage 1: Merge adjacent pairs
let pairs = vreinterpretq_u16_u8(indices);
// Reinterpret as u16: [0x1613, 0x2E05, ...]
let even = vandq_u16(pairs, vdupq_n_u16(0xFF));
// Extract even bytes: [0x13, 0x05, ...]
let odd = vshrq_n_u16(pairs, 8);
// Extract odd bytes: [0x16, 0x2E, ...]
let merge_result = vaddq_u16(even, vshlq_n_u16(odd, 6));
// even + (odd << 6) = 0x13 + (0x16 << 6) = 0x13 + 0x580 = 0x593
```

Wait, this is wrong. The algorithm is treating pairs in little-endian order incorrectly.

## Binary Analysis

Indices in 6-bit form:
- Index 0: 19 = 0b00010011
- Index 1: 22 = 0b00010110
- Index 2: 5  = 0b00000101
- Index 3: 46 = 0b00101110

These should pack into bytes as:
```
Byte 0 = index[0][5:0] | index[1][1:0] << 6
       = 0b00010011 | 0b10_000000
       = 0b01_010011 = 0x53... NO

Actually base64 decode:
4 indices (24 bits) -> 3 bytes (24 bits)

index[0] is bits [23:18]
index[1] is bits [17:12]
index[2] is bits [11:6]
index[3] is bits [5:0]

Byte 0 (MSB) = index[0] << 2 | index[1] >> 4
Byte 1 (MID) = (index[1] & 0x0F) << 4 | index[2] >> 2
Byte 2 (LSB) = (index[2] & 0x03) << 6 | index[3]
```

Let me verify:
```
Byte 0 = 19 << 2 | 22 >> 4
       = 0b01001100 | 0b00000001
       = 0b01001101 = 0x4D ✓ ('M')

Byte 1 = (22 & 0x0F) << 4 | 5 >> 2
       = 0b0110_0000 | 0b00000001
       = 0b01100001 = 0x61 ✓ ('a')

Byte 2 = (5 & 0x03) << 6 | 46
       = 0b01_000000 | 0b00101110
       = 0b01101110 = 0x6E ✓ ('n')
```

## The Bug

The current algorithm uses `maddubs` style multiply-add which is correct for x86,
but the implementation is doing arithmetic in the wrong order or with wrong masks.

The algorithm should:
1. Pack pairs: (idx[0] << 2) | (idx[1] >> 4), (idx[1] << 4) | (idx[2] >> 2), (idx[2] << 6) | idx[3]
2. But it's trying to use vectorized multiply-add tricks

Let me check the x86 reference to see what the actual bit math should be.
