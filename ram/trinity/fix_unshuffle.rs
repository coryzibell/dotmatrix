// Test the fixed unshuffle algorithm
use std::arch::aarch64::*;

unsafe fn print_vec(name: &str, vec: uint8x16_t) {
    let mut buf = [0u8; 16];
    vst1q_u8(buf.as_mut_ptr(), vec);
    print!("{}: ", name);
    for &b in &buf {
        print!("{:02x} ", b);
    }
    println!();
}

unsafe fn print_vec_u16(name: &str, vec: uint16x8_t) {
    let mut buf = [0u16; 8];
    vst1q_u16(buf.as_mut_ptr(), vec);
    print!("{}: ", name);
    for &w in &buf {
        print!("{:04x} ", w);
    }
    println!();
}

unsafe fn print_vec_u32(name: &str, vec: uint32x4_t) {
    let mut buf = [0u32; 4];
    vst1q_u32(buf.as_mut_ptr(), vec);
    print!("{}: ", name);
    for &d in &buf {
        print!("{:08x} ", d);
    }
    println!();
}

// BROKEN version (current code)
#[target_feature(enable = "neon")]
unsafe fn unshuffle_6bit_broken(indices: uint8x16_t) -> uint8x16_t {
    println!("\n=== BROKEN VERSION ===");

    let pairs = vreinterpretq_u16_u8(indices);
    print_vec_u16("Reinterpreted as u16", pairs);

    let even = vandq_u16(pairs, vdupq_n_u16(0xFF));
    print_vec_u16("Even (low bytes)", even);

    let odd = vshrq_n_u16(pairs, 8);
    print_vec_u16("Odd (high bytes)", odd);

    let merge_result = vaddq_u16(even, vshlq_n_u16(odd, 6));
    print_vec_u16("Merge (even + odd<<6)", merge_result);

    let merge_u32 = vreinterpretq_u32_u16(merge_result);
    let lo = vandq_u32(merge_u32, vdupq_n_u32(0xFFFF));
    let hi = vshrq_n_u32(merge_u32, 16);
    let final_32bit = vorrq_u32(vshlq_n_u32(lo, 12), hi);
    print_vec_u32("Final 32-bit", final_32bit);

    let shuffle_mask = vld1q_u8([2, 1, 0, 6, 5, 4, 10, 9, 8, 14, 13, 12, 255, 255, 255, 255].as_ptr());
    let result_bytes = vreinterpretq_u8_u32(final_32bit);
    vqtbl1q_u8(result_bytes, shuffle_mask)
}

// FIXED version - properly emulate maddubs
#[target_feature(enable = "neon")]
unsafe fn unshuffle_6bit_fixed(indices: uint8x16_t) -> uint8x16_t {
    println!("\n=== FIXED VERSION ===");

    // Stage 1: Emulate maddubs(indices, [64,1,64,1,...])
    // maddubs multiplies and adds adjacent pairs:
    //   result[i] = indices[2i] * 64 + indices[2i+1] * 1

    let pairs = vreinterpretq_u16_u8(indices);
    print_vec_u16("Reinterpreted as u16", pairs);

    let even = vandq_u16(pairs, vdupq_n_u16(0xFF)); // indices[0,2,4,...]
    let odd = vshrq_n_u16(pairs, 8); // indices[1,3,5,...]
    print_vec_u16("Even (indices 0,2,4,...)", even);
    print_vec_u16("Odd (indices 1,3,5,...)", odd);

    // Correct formula: even * 64 + odd * 1
    let merge_result = vmlaq_n_u16(odd, even, 64); // odd + even * 64
    print_vec_u16("Merge (even*64 + odd*1)", merge_result);

    // Stage 2: Emulate madd(merge_result, [4096,1,4096,1,...])
    // madd multiplies 16-bit values and adds adjacent pairs:
    //   result[i] = merge[2i] * 4096 + merge[2i+1] * 1

    let merge_u32 = vreinterpretq_u32_u16(merge_result);
    let lo = vandq_u32(merge_u32, vdupq_n_u32(0xFFFF)); // merge[0,2,4,6]
    let hi = vshrq_n_u32(merge_u32, 16); // merge[1,3,5,7]
    print_vec_u32("Lo 16-bit (merge 0,2,4,6)", lo);
    print_vec_u32("Hi 16-bit (merge 1,3,5,7)", hi);

    // Correct formula: lo * 4096 + hi * 1
    let final_32bit = vorrq_u32(vshlq_n_u32(lo, 12), hi); // (lo << 12) | hi
    print_vec_u32("Final 32-bit (lo*4096 + hi)", final_32bit);

    // Stage 3: Extract bytes in reverse order (little-endian fix)
    let shuffle_mask = vld1q_u8([
        2, 1, 0,      // first group (bytes 0-2)
        6, 5, 4,      // second group (bytes 3-5)
        10, 9, 8,     // third group (bytes 6-8)
        14, 13, 12,   // fourth group (bytes 9-11)
        255, 255, 255, 255 // unused
    ].as_ptr());

    let result_bytes = vreinterpretq_u8_u32(final_32bit);
    vqtbl1q_u8(result_bytes, shuffle_mask)
}

fn main() {
    println!("Testing unshuffle_6bit fix");
    println!("Input indices: [19, 22, 5, 46] (standard base64 for 'Man')");
    println!("Expected output: [0x4D, 0x61, 0x6E] ('Man')");

    let mut indices = [0u8; 16];
    indices[0] = 19;
    indices[1] = 22;
    indices[2] = 5;
    indices[3] = 46;

    unsafe {
        let indices_vec = vld1q_u8(indices.as_ptr());
        print_vec("Input indices", indices_vec);

        let broken = unshuffle_6bit_broken(indices_vec);
        print_vec("BROKEN result", broken);

        let fixed = unshuffle_6bit_fixed(indices_vec);
        print_vec("FIXED result", fixed);

        let mut result = [0u8; 16];
        vst1q_u8(result.as_mut_ptr(), fixed);

        println!("\nFinal check:");
        println!("Got:      [{:02x} {:02x} {:02x}]", result[0], result[1], result[2]);
        println!("Expected: [4d 61 6e]");

        if result[0] == 0x4D && result[1] == 0x61 && result[2] == 0x6E {
            println!("✓ SUCCESS!");
        } else {
            println!("✗ STILL BROKEN");
        }
    }
}
