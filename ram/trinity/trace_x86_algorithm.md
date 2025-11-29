# Tracing x86 Base64 Reshuffle Algorithm

## Input
"Hel" = [0x48, 0x65, 0x6C]

Binary:
- H = 0x48 = `0100 1000`
- e = 0x65 = `0110 0101`
- l = 0x6C = `0110 1100`

## Expected Output
24 bits → 4 x 6-bit indices:
```
010010 | 00 0110 | 0101 01 | 101100
  18   |    6    |   21    |   44
  'S'  |   'G'   |   'V'   |   's'
```

## Step 1: Shuffle

Shuffle mask: `[0, 1, 1, 2]` → load bytes `[0x48, 0x65, 0x65, 0x6C]`

As u32 (little-endian): `0x6C656548`

As u16[2]:
- u16[0] = `0x6548`
- u16[1] = `0x6C65`

## Step 2: First Extraction (mulhi)

Mask: `0x0FC0FC00`

```
  0x6C656548
& 0x0FC0FC00
-----------
  0x0C404800
```

As u16:
- u16[0] = `0x4800`
- u16[1] = `0x0C40`

Multiply (mulhi_epu16 with `0x04000040`):
- u16[0]: `0x4800 * 0x0040 = 0x00120000` → high 16 = `0x0012`
- u16[1]: `0x0C40 * 0x0400 = 0x00310000` → high 16 = `0x0031`

Result t1 as u32: `0x00310012`
Result t1 as bytes: `[0x12, 0x00, 0x31, 0x00]`

Binary of 0x12 = `00010010` = 18 ✓
Binary of 0x31 = `00110001` = 49 ❌ (should be 21)

Wait, that's wrong. Let me recalculate...

## Recalculating

After shuffle `[H, e, e, l]` = `[0x48, 0x65, 0x65, 0x6C]`

Reading as u32 LE: byte0 is LSB
```
bytes[0] = 0x48  (bits 0-7)
bytes[1] = 0x65  (bits 8-15)
bytes[2] = 0x65  (bits 16-23)
bytes[3] = 0x6C  (bits 24-31)

u32 = 0x6C656548
```

Reading as u16 LE:
```
u16[0] (bits 0-15)  = 0x6548
u16[1] (bits 16-31) = 0x6C65
```

Hmm, wait. Let me check the x86 shuffle mask more carefully...

## X86 Shuffle Mask

```rust
_mm_set_epi8(
    10, 11, 9, 10,  // positions 12-15
    7, 8, 6, 7,     // positions 8-11
    4, 5, 3, 4,     // positions 4-7
    1, 2, 0, 1,     // positions 0-3 ← THIS IS REVERSED
)
```

`_mm_set_epi8` takes arguments in REVERSE order (MSB first).

So positions 0-3 get: `[input[1], input[0], input[2], input[1]]`

For "Hel":
- Position 0: input[1] = 0x65 ('e')
- Position 1: input[0] = 0x48 ('H')
- Position 2: input[2] = 0x6C ('l')
- Position 3: input[1] = 0x65 ('e')

So shuffled = `[0x65, 0x48, 0x6C, 0x65, ...]`

As u32: `0x656C4865`
As u16:
- u16[0] = `0x4865`
- u16[1] = `0x656C`

Now apply mask `0x0FC0FC00`:
```
  0x656C4865
& 0x0FC0FC00
-----------
  0x044C4800
```

As u16:
- u16[0] = `0x4800`
- u16[1] = `0x044C`

Multiply (mulhi):
- u16[0]: `0x4800 * 0x0040 = 0x00120000` → high 16 = `0x0012` = 18 ✓
- u16[1]: `0x044C * 0x0400 = 0x00113000` → high 16 = `0x0011` = 17 ❌

Still wrong. The x86 algorithm is complex. Let me just look at what the reference implementation does.
