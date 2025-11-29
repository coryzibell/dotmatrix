# Base32 Extraction Map from large.rs

## Base32 Functions to Extract

### NEON (aarch64) Encode
- Line 191-261: `encode_neon_base32` - NEON base32 encoder

### Scalar Encode (shared/aarch64)
- Line 388-411: `encode_scalar_base32` - Scalar base32 fallback

### x86_64 Range-Reduction Encode
- Line 481-565: `encode_ssse3_range_reduction_5bit` - SSE base32 range-reduction encoder

### AVX-512 VBMI Encode  
- Line 696-764: `encode_avx512_vbmi_base32` - AVX-512 VBMI base32 encoder

### Scalar Encode (x86)
- Line 859-882: `encode_scalar_base32_x86` - x86 scalar fallback

### Helper Functions
- Line 962-970: `is_rfc4648_base32` - RFC4648 base32 dictionary check

### SSSE3 Decode
- Line 1031-1074: `decode_ssse3_multi_range_5bit` - Multi-range 5-bit decoder
- Line 1169-1204: `unpack_5bit_ssse3` - Unpack 16×5-bit to 10 bytes
- Line 1206-1278: `decode_ssse3_base32_rfc4648` - RFC4648 base32 SSSE3 decoder

### NEON Decode
- Line 1279-1348: `decode_neon_base32_rfc4648` - RFC4648 base32 NEON decoder

### Tests
All test functions with "base32" in name
