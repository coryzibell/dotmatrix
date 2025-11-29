// Standalone NEON trace - run with: rustc --target=aarch64-apple-darwin -C opt-level=3 trace_neon.rs && ./trace_neon
use std::arch::aarch64::*;

// Helper to print uint8x16_t in hex
unsafe fn print_vec(name: &str, vec: uint8x16_t) {
    let mut buf = [0u8; 16];
    vst1q_u8(buf.as_mut_ptr(), vec);
    print!("{}: ", name);
    for &b in &buf {
        print!("{:02x} ", b);
    }
    println!();
}

// Copy of reshuffle_6bit
#[target_feature(enable = "neon")]
unsafe fn reshuffle_6bit(input: uint8x16_t) -> uint8x16_t {
    let shuffle_indices = vld1q_u8(
        [
            1, 0, 2, 1, // bytes 0-2 -> positions 0-3
            4, 3, 5, 4, // bytes 3-5 -> positions 4-7
            7, 6, 8, 7, // bytes 6-8 -> positions 8-11
            10, 9, 11, 10, // bytes 9-11 -> positions 12-15
        ]
        .as_ptr(),
    );

    let shuffled = vqtbl1q_u8(input, shuffle_indices);

    let shuffled_u32 = vreinterpretq_u32_u8(shuffled);

    // First extraction: positions 0 and 2
    let t0 = vandq_u32(shuffled_u32, vdupq_n_u32(0x0FC0FC00_u32));
    let t1 = {
        let t0_u16 = vreinterpretq_u16_u32(t0);
        let mult_pattern = vreinterpretq_u16_u32(vdupq_n_u32(0x04000040_u32));
        let lo = vget_low_u16(t0_u16);
        let hi = vget_high_u16(t0_u16);
        let mult_lo = vget_low_u16(mult_pattern);
        let mult_hi = vget_high_u16(mult_pattern);
        let lo_32 = vmull_u16(lo, mult_lo);
        let hi_32 = vmull_u16(hi, mult_hi);
        let lo_result = vshrn_n_u32(lo_32, 16);
        let hi_result = vshrn_n_u32(hi_32, 16);
        vreinterpretq_u32_u16(vcombine_u16(lo_result, hi_result))
    };

    // Second extraction: positions 1 and 3
    let t2 = vandq_u32(shuffled_u32, vdupq_n_u32(0x003F03F0_u32));
    let t3 = {
        let t2_u16 = vreinterpretq_u16_u32(t2);
        let mult_pattern = vreinterpretq_u16_u32(vdupq_n_u32(0x01000010_u32));
        vreinterpretq_u32_u16(vmulq_u16(t2_u16, mult_pattern))
    };

    vreinterpretq_u8_u32(vorrq_u32(t1, t3))
}

// Copy of unshuffle_6bit
#[target_feature(enable = "neon")]
unsafe fn unshuffle_6bit(indices: uint8x16_t) -> uint8x16_t {
    let pairs = vreinterpretq_u16_u8(indices);
    let even = vandq_u16(pairs, vdupq_n_u16(0xFF));
    let odd = vshrq_n_u16(pairs, 8);
    let merge_result = vaddq_u16(even, vshlq_n_u16(odd, 6));

    let merge_u32 = vreinterpretq_u32_u16(merge_result);
    let lo = vandq_u32(merge_u32, vdupq_n_u32(0xFFFF));
    let hi = vshrq_n_u32(merge_u32, 16);
    let final_32bit = vorrq_u32(vshlq_n_u32(lo, 12), hi);

    let shuffle_mask = vld1q_u8(
        [
            2, 1, 0, // first group
            6, 5, 4, // second group
            10, 9, 8, // third group
            14, 13, 12, // fourth group
            255, 255, 255, 255, // unused
        ]
        .as_ptr(),
    );

    let result_bytes = vreinterpretq_u8_u32(final_32bit);
    vqtbl1q_u8(result_bytes, shuffle_mask)
}

fn main() {
    println!("\n=== ENCODE TRACE ===");
    println!("Input: 'Man' = [4D 61 6E]");
    println!("Expected in standard base64: 'TWFu' (indices 19, 22, 5, 46)");

    // Pad input to 16 bytes for SIMD safety
    let mut input = [0u8; 16];
    input[0] = 0x4D; // 'M'
    input[1] = 0x61; // 'a'
    input[2] = 0x6E; // 'n'

    unsafe {
        let input_vec = vld1q_u8(input.as_ptr());
        print_vec("Input bytes", input_vec);

        // Manual bit extraction for verification
        // M(0x4D) a(0x61) n(0x6E)
        // Binary: 01001101 01100001 01101110
        // 6-bit groups: 010011 | 010110 | 000101 | 101110
        // Decimal: 19, 22, 5, 46
        println!("Manual calculation:");
        println!("  Byte 0 (M=0x4D=0b01001101): bits [7:2] = 0b010011 = 19");
        println!("  Bytes 0-1: bits [1:0] of M + bits [7:4] of a = 0b01_0110 = 22");
        println!("  Bytes 1-2: bits [3:0] of a + bits [7:6] of n = 0b0001_01 = 5");
        println!("  Byte 2 (n=0x6E=0b01101110): bits [5:0] = 0b101110 = 46");

        let reshuffled = reshuffle_6bit(input_vec);
        print_vec("After reshuffle (6-bit indices)", reshuffled);

        let mut indices = [0u8; 16];
        vst1q_u8(indices.as_mut_ptr(), reshuffled);
        println!("First 4 indices: {} {} {} {}", indices[0], indices[1], indices[2], indices[3]);
        println!("Expected:        19 22 5 46");

        if indices[0] == 19 && indices[1] == 22 && indices[2] == 5 && indices[3] == 46 {
            println!("✓ ENCODE RESHUFFLE CORRECT");
        } else {
            println!("✗ ENCODE RESHUFFLE WRONG");
        }
    }

    println!("\n=== DECODE TRACE ===");
    println!("Input indices: [19, 22, 5, 46]");

    let mut indices_input = [0u8; 16];
    indices_input[0] = 19;
    indices_input[1] = 22;
    indices_input[2] = 5;
    indices_input[3] = 46;

    unsafe {
        let indices_vec = vld1q_u8(indices_input.as_ptr());
        print_vec("Input indices", indices_vec);

        let bytes_out = unshuffle_6bit(indices_vec);
        print_vec("After unshuffle (output bytes)", bytes_out);

        let mut result = [0u8; 16];
        vst1q_u8(result.as_mut_ptr(), bytes_out);
        println!("First 3 bytes: {:02x} {:02x} {:02x}", result[0], result[1], result[2]);
        println!("Expected:      4d 61 6e");

        if result[0] == 0x4D && result[1] == 0x61 && result[2] == 0x6E {
            println!("✓ DECODE UNSHUFFLE CORRECT");
        } else {
            println!("✗ DECODE UNSHUFFLE WRONG");
        }
    }
}
