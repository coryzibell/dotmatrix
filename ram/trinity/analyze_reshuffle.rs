// Analyze the NEON reshuffle step-by-step
use std::arch::aarch64::*;

fn main() {
    let data = b"Hel"; // Just 3 bytes to analyze

    println!("=== Analyzing NEON Reshuffle for 3 bytes ===\n");
    println!("Input: {:?}", data);
    println!("Input hex: {:02X?}\n", data);

    // Expected 6-bit indices for "Hel":
    // H = 0x48 = 01001000
    // e = 0x65 = 01100101
    // l = 0x6C = 01101100
    //
    // Reading 24 bits left-to-right in 6-bit groups:
    // 010010 000110 010101 101100
    //   18     6      21     44
    //   S      G      V      s

    println!("Expected 6-bit indices: [18, 6, 21, 44]");
    println!("Expected chars: SGVs\n");

    unsafe {
        // Load input
        let input_vec = vld1q_u8([data[0], data[1], data[2], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0].as_ptr());

        let mut input_bytes = [0u8; 16];
        vst1q_u8(input_bytes.as_mut_ptr(), input_vec);
        println!("Input vector: {:02X?}", &input_bytes);

        // Step 1: Shuffle
        let shuffle_indices = vld1q_u8([0, 0, 1, 2, 3, 3, 4, 5, 6, 6, 7, 8, 9, 9, 10, 11].as_ptr());
        let shuffled = vqtbl1q_u8(input_vec, shuffle_indices);

        let mut shuffled_bytes = [0u8; 16];
        vst1q_u8(shuffled_bytes.as_mut_ptr(), shuffled);
        println!("\nAfter shuffle: {:02X?}", &shuffled_bytes);
        println!("As u32 (LE): [{:08X}, {:08X}, {:08X}, {:08X}]",
            u32::from_le_bytes([shuffled_bytes[0], shuffled_bytes[1], shuffled_bytes[2], shuffled_bytes[3]]),
            u32::from_le_bytes([shuffled_bytes[4], shuffled_bytes[5], shuffled_bytes[6], shuffled_bytes[7]]),
            u32::from_le_bytes([shuffled_bytes[8], shuffled_bytes[9], shuffled_bytes[10], shuffled_bytes[11]]),
            u32::from_le_bytes([shuffled_bytes[12], shuffled_bytes[13], shuffled_bytes[14], shuffled_bytes[15]]));

        let shuffled_u32 = vreinterpretq_u32_u8(shuffled);

        // Step 2: First extraction (mask 0x0FC0FC00)
        println!("\n--- First extraction (high bits) ---");
        println!("Mask: 0x0FC0FC00");
        let t0 = vandq_u32(shuffled_u32, vdupq_n_u32(0x0FC0FC00));

        let mut t0_bytes = [0u8; 16];
        vst1q_u8(t0_bytes.as_mut_ptr(), vreinterpretq_u8_u32(t0));
        println!("After mask: {:02X?}", &t0_bytes);
        println!("As u32: [{:08X}, {:08X}, {:08X}, {:08X}]",
            u32::from_le_bytes([t0_bytes[0], t0_bytes[1], t0_bytes[2], t0_bytes[3]]),
            u32::from_le_bytes([t0_bytes[4], t0_bytes[5], t0_bytes[6], t0_bytes[7]]),
            u32::from_le_bytes([t0_bytes[8], t0_bytes[9], t0_bytes[10], t0_bytes[11]]),
            u32::from_le_bytes([t0_bytes[12], t0_bytes[13], t0_bytes[14], t0_bytes[15]]));

        let t0_u16 = vreinterpretq_u16_u32(t0);
        let mult_hi = vmulq_n_u16(t0_u16, 0x0040);

        let mut mult_hi_bytes = [0u8; 16];
        vst1q_u8(mult_hi_bytes.as_mut_ptr(), vreinterpretq_u8_u16(mult_hi));
        println!("After mult by 0x0040: {:02X?}", &mult_hi_bytes);

        let t1 = vreinterpretq_u32_u16(vshrq_n_u16(mult_hi, 10));

        let mut t1_bytes = [0u8; 16];
        vst1q_u8(t1_bytes.as_mut_ptr(), vreinterpretq_u8_u32(t1));
        println!("After shift >>10: {:02X?}", &t1_bytes);

        // Step 3: Second extraction (mask 0x003F03F0)
        println!("\n--- Second extraction (low bits) ---");
        println!("Mask: 0x003F03F0");
        let t2 = vandq_u32(shuffled_u32, vdupq_n_u32(0x003F03F0));

        let mut t2_bytes = [0u8; 16];
        vst1q_u8(t2_bytes.as_mut_ptr(), vreinterpretq_u8_u32(t2));
        println!("After mask: {:02X?}", &t2_bytes);

        let t2_u16 = vreinterpretq_u16_u32(t2);
        let mult_lo = vmulq_n_u16(t2_u16, 0x0010);

        let mut mult_lo_bytes = [0u8; 16];
        vst1q_u8(mult_lo_bytes.as_mut_ptr(), vreinterpretq_u8_u16(mult_lo));
        println!("After mult by 0x0010: {:02X?}", &mult_lo_bytes);

        let t3 = vreinterpretq_u32_u16(vshrq_n_u16(mult_lo, 6));

        let mut t3_bytes = [0u8; 16];
        vst1q_u8(t3_bytes.as_mut_ptr(), vreinterpretq_u8_u32(t3));
        println!("After shift >>6: {:02X?}", &t3_bytes);

        // Step 4: OR together
        println!("\n--- Final OR ---");
        let result = vreinterpretq_u8_u32(vorrq_u32(t1, t3));

        let mut result_bytes = [0u8; 16];
        vst1q_u8(result_bytes.as_mut_ptr(), result);
        println!("Result: {:02X?}", &result_bytes);
        println!("First 4 indices: [{}, {}, {}, {}]", result_bytes[0], result_bytes[1], result_bytes[2], result_bytes[3]);

        println!("\nExpected: [18, 6, 21, 44]");
        println!("Got:      [{}, {}, {}, {}]", result_bytes[0], result_bytes[1], result_bytes[2], result_bytes[3]);
    }
}
