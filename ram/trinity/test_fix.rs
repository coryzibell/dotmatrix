// Test the fix for NEON base64 reshuffle
use std::arch::aarch64::*;

fn main() {
    let data = b"Hello World!";

    println!("=== Testing FIXED NEON Reshuffle ===\n");
    println!("Input: {:?}", String::from_utf8_lossy(data));

    unsafe {
        let input_vec = vld1q_u8(data.as_ptr());

        // OLD (broken) version
        let old_indices = reshuffle_neon_broken(input_vec);
        let mut old_buf = [0u8; 16];
        vst1q_u8(old_buf.as_mut_ptr(), old_indices);

        // NEW (fixed) version
        let new_indices = reshuffle_neon_fixed(input_vec);
        let mut new_buf = [0u8; 16];
        vst1q_u8(new_buf.as_mut_ptr(), new_indices);

        // Scalar reference
        let scalar_indices = base64_encode_scalar_indices(data);

        println!("OLD (broken): {:?}", &old_buf);
        println!("NEW (fixed):  {:?}", &new_buf);
        println!("SCALAR:       {:?}", &scalar_indices[..16]);

        // Translate to chars
        let alphabet = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

        let old_chars: String = old_buf.iter()
            .map(|&idx| if (idx as usize) < 64 { alphabet[idx as usize] as char } else { '?' })
            .collect();

        let new_chars: String = new_buf.iter()
            .map(|&idx| if (idx as usize) < 64 { alphabet[idx as usize] as char } else { '?' })
            .collect();

        let scalar_chars: String = scalar_indices.iter()
            .map(|&idx| alphabet[idx as usize] as char)
            .collect();

        println!("\nOLD encoded:    {}", old_chars);
        println!("NEW encoded:    {}", new_chars);
        println!("SCALAR encoded: {}", scalar_chars);

        if new_buf == &scalar_indices[..16] {
            println!("\n✅ FIX WORKS! NEON matches scalar.");
        } else {
            println!("\n❌ Fix incomplete. Differences:");
            for i in 0..16 {
                if new_buf[i] != scalar_indices[i] {
                    println!("  Position {}: NEON={}, Scalar={}", i, new_buf[i], scalar_indices[i]);
                }
            }
        }
    }
}

unsafe fn reshuffle_neon_broken(input: uint8x16_t) -> uint8x16_t {
    let shuffle_indices = vld1q_u8([0, 0, 1, 2, 3, 3, 4, 5, 6, 6, 7, 8, 9, 9, 10, 11].as_ptr());
    let shuffled = vqtbl1q_u8(input, shuffle_indices);
    let shuffled_u32 = vreinterpretq_u32_u8(shuffled);

    let t0 = vandq_u32(shuffled_u32, vdupq_n_u32(0x0FC0FC00));
    let t0_u16 = vreinterpretq_u16_u32(t0);
    let mult_hi = vmulq_n_u16(t0_u16, 0x0040); // BROKEN: same multiplier for all lanes
    let t1 = vreinterpretq_u32_u16(vshrq_n_u16(mult_hi, 10));

    let t2 = vandq_u32(shuffled_u32, vdupq_n_u32(0x003F03F0));
    let t2_u16 = vreinterpretq_u16_u32(t2);
    let mult_lo = vmulq_n_u16(t2_u16, 0x0010); // BROKEN: same multiplier for all lanes
    let t3 = vreinterpretq_u32_u16(vshrq_n_u16(mult_lo, 6));

    vreinterpretq_u8_u32(vorrq_u32(t1, t3))
}

unsafe fn reshuffle_neon_fixed(input: uint8x16_t) -> uint8x16_t {
    let shuffle_indices = vld1q_u8([0, 0, 1, 2, 3, 3, 4, 5, 6, 6, 7, 8, 9, 9, 10, 11].as_ptr());
    let shuffled = vqtbl1q_u8(input, shuffle_indices);
    let shuffled_u32 = vreinterpretq_u32_u8(shuffled);

    // First extraction: use alternating multipliers 0x0040 and 0x0400
    let t0 = vandq_u32(shuffled_u32, vdupq_n_u32(0x0FC0FC00));
    let t0_u16 = vreinterpretq_u16_u32(t0);

    // Load alternating multipliers for u16 lanes
    let mult_hi_const = vld1q_u16([0x0040, 0x0400, 0x0040, 0x0400, 0x0040, 0x0400, 0x0040, 0x0400].as_ptr());
    let mult_hi = vmulq_u16(t0_u16, mult_hi_const);
    let t1 = vreinterpretq_u32_u16(vshrq_n_u16(mult_hi, 10));

    // Second extraction: use alternating multipliers 0x0010 and 0x0100
    let t2 = vandq_u32(shuffled_u32, vdupq_n_u32(0x003F03F0));
    let t2_u16 = vreinterpretq_u16_u32(t2);

    let mult_lo_const = vld1q_u16([0x0010, 0x0100, 0x0010, 0x0100, 0x0010, 0x0100, 0x0010, 0x0100].as_ptr());
    let mult_lo = vmulq_u16(t2_u16, mult_lo_const);
    let t3 = vreinterpretq_u32_u16(vshrq_n_u16(mult_lo, 6));

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
