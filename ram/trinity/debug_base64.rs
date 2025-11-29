// Debug script to test NEON base64 encoding
use std::arch::aarch64::*;

// Minimal test - just encode a few bytes and see what we get
fn main() {
    unsafe {
        let data = [0u8, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];

        println!("Input bytes: {:?}", &data);

        // Load input
        let input_vec = vld1q_u8(data.as_ptr());

        // Print input vector
        let mut input_bytes = [0u8; 16];
        vst1q_u8(input_bytes.as_mut_ptr(), input_vec);
        println!("Input vector: {:02X?}", &input_bytes);

        // Reshuffle
        let reshuffled = reshuffle_neon(input_vec);
        let mut reshuffled_bytes = [0u8; 16];
        vst1q_u8(reshuffled_bytes.as_mut_ptr(), reshuffled);
        println!("After reshuffle: {:02X?}", &reshuffled_bytes);
        println!("As 6-bit values: {:?}", reshuffled_bytes.iter().map(|&b| b & 0x3F).collect::<Vec<_>>());

        // Expected 6-bit indices for [0,1,2,3,4,5,6,7,8,9,10,11]
        // Bytes: 00000000 00000001 00000010 00000011 00000100 00000101 ...
        // 6-bit groups from left to right:
        // 000000 000000 000100 000010 | 000000 110000 010000 000101 | ...
        //   0      0      4      2        3     48     16      5
        println!("\nExpected 6-bit indices for first 12 bytes:");
        let expected = base64_indices_manual(&data);
        println!("{:?}", expected);
    }
}

unsafe fn reshuffle_neon(input: uint8x16_t) -> uint8x16_t {
    let shuffle_indices = vld1q_u8(
        [
            0, 0, 1, 2,
            3, 3, 4, 5,
            6, 6, 7, 8,
            9, 9, 10, 11,
        ]
        .as_ptr(),
    );

    let shuffled = vqtbl1q_u8(input, shuffle_indices);

    let shuffled_u32 = vreinterpretq_u32_u8(shuffled);

    let t0 = vandq_u32(shuffled_u32, vdupq_n_u32(0x0FC0FC00));
    let t0_u16 = vreinterpretq_u16_u32(t0);
    let mult_hi = vmulq_n_u16(t0_u16, 0x0040);
    let t1 = vreinterpretq_u32_u16(vshrq_n_u16(mult_hi, 10));

    let t2 = vandq_u32(shuffled_u32, vdupq_n_u32(0x003F03F0));
    let t2_u16 = vreinterpretq_u16_u32(t2);
    let mult_lo = vmulq_n_u16(t2_u16, 0x0010);
    let t3 = vreinterpretq_u32_u16(vshrq_n_u16(mult_lo, 6));

    vreinterpretq_u8_u32(vorrq_u32(t1, t3))
}

fn base64_indices_manual(data: &[u8]) -> Vec<u8> {
    let mut result = Vec::new();
    let mut i = 0;

    while i + 2 < data.len() {
        let b0 = data[i];
        let b1 = data[i + 1];
        let b2 = data[i + 2];

        result.push(b0 >> 2);
        result.push(((b0 & 0x03) << 4) | (b1 >> 4));
        result.push(((b1 & 0x0F) << 2) | (b2 >> 6));
        result.push(b2 & 0x3F);

        i += 3;
    }

    result
}
