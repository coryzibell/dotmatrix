// Correct NEON implementation using vmull for mulhi simulation
use std::arch::aarch64::*;

fn main() {
    let data = b"Hello World!";

    println!("=== Testing CORRECTLY FIXED NEON Reshuffle ===\n");

    unsafe {
        let input_vec = vld1q_u8(data.as_ptr());

        let new_indices = reshuffle_neon_correct(input_vec);
        let mut new_buf = [0u8; 16];
        vst1q_u8(new_buf.as_mut_ptr(), new_indices);

        let scalar_indices = base64_encode_scalar_indices(data);

        println!("NEON (corrected): {:?}", &new_buf);
        println!("SCALAR:           {:?}", &scalar_indices[..16]);

        let alphabet = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

        let new_chars: String = new_buf.iter()
            .map(|&idx| if (idx as usize) < 64 { alphabet[idx as usize] as char } else { '?' })
            .collect();

        let scalar_chars: String = scalar_indices.iter()
            .map(|&idx| alphabet[idx as usize] as char)
            .collect();

        println!("\nNEON encoded:   {}", new_chars);
        println!("SCALAR encoded: {}", scalar_chars);

        if new_buf == &scalar_indices[..16] {
            println!("\n✅ FIX WORKS! NEON matches scalar perfectly.");
        } else {
            println!("\n❌ Still has differences:");
            for i in 0..16 {
                if new_buf[i] != scalar_indices[i] {
                    println!("  Position {}: NEON={}, Scalar={}", i, new_buf[i], scalar_indices[i]);
                }
            }
        }
    }
}

unsafe fn reshuffle_neon_correct(input: uint8x16_t) -> uint8x16_t {
    let shuffle_indices = vld1q_u8([0, 0, 1, 2, 3, 3, 4, 5, 6, 6, 7, 8, 9, 9, 10, 11].as_ptr());
    let shuffled = vqtbl1q_u8(input, shuffle_indices);
    let shuffled_u32 = vreinterpretq_u32_u8(shuffled);

    // First extraction: simulate mulhi_epu16
    let t0 = vandq_u32(shuffled_u32, vdupq_n_u32(0x0FC0FC00));
    let t0_u16 = vreinterpretq_u16_u32(t0);

    // Multiply low and high halves separately using vmull (widening multiply)
    // This gives us 32-bit results, from which we take the high 16 bits
    let mult_const = vld1_u16([0x0040, 0x0400, 0x0040, 0x0400].as_ptr());

    let t0_lo = vget_low_u16(t0_u16);   // First 4 u16 values
    let t0_hi = vget_high_u16(t0_u16);  // Last 4 u16 values

    let prod_lo = vmull_u16(t0_lo, mult_const);  // 4x u32 products
    let prod_hi = vmull_u16(t0_hi, mult_const);  // 4x u32 products

    // Extract high 16 bits of each 32-bit product
    let hi_lo = vshrn_n_u32(prod_lo, 16);  // Shift right 16, narrow to u16
    let hi_hi = vshrn_n_u32(prod_hi, 16);

    let t1_u16 = vcombine_u16(hi_lo, hi_hi);  // Recombine into uint16x8_t
    let t1 = vreinterpretq_u32_u16(t1_u16);

    // Second extraction: simulate mullo_epi16 (just multiply low bits)
    let t2 = vandq_u32(shuffled_u32, vdupq_n_u32(0x003F03F0));
    let t2_u16 = vreinterpretq_u16_u32(t2);

    let mult2_const = vld1_u16([0x0010, 0x0100, 0x0010, 0x0100].as_ptr());

    let t2_lo = vget_low_u16(t2_u16);
    let t2_hi = vget_high_u16(t2_u16);

    // For mullo, we want the low 16 bits, but we still need to shift right by 6 later
    // The x86 does: mullo_epi16 (gives low 16 bits of product), result is used directly
    // So we just do regular multiply
    let prod2_lo = vmul_u16(t2_lo, mult2_const);
    let prod2_hi = vmul_u16(t2_hi, mult2_const);

    let t3_u16 = vcombine_u16(prod2_lo, prod2_hi);
    let t3 = vreinterpretq_u32_u16(t3_u16);

    // Combine
    vreinterpretq_u8_u32(vorrq_u32(t1, t3))
}

fn base64_encode_scalar_indices(data: &[u8]) -> Vec<u8> {
    let mut result = Vec::new();

    for chunk in data.chunks(3) {
        let b0 = chunk[0];
        let b1 = if chunk.len() > 1 { chunk[1] } else { 0 };
        let b2 = if chunk.len() > 2 { chunk[2] } else { 0 };

        result.push(b0 >> 2);
        result.push(((b0 & 0x03) << 4) | (b1 >> 4));
        result.push(((b1 & 0x0F) << 2) | (b2 >> 6));
        result.push(b2 & 0x3F);
    }

    result
}
