// Diagnostic test to see exactly where NEON base64 encode/decode fails
use std::arch::aarch64::*;

fn main() {
    // Test data - simple bytes
    let data = b"Hello World!"; // 12 bytes = exactly 1 NEON block

    println!("=== Testing NEON Base64 Encode/Decode ===\n");
    println!("Input: {:?}", data);
    println!("Input hex: {:02X?}", data);

    unsafe {
        // Step 1: Encode using NEON
        let input_vec = vld1q_u8(data.as_ptr());

        // Reshuffle to get 6-bit indices
        let indices = reshuffle_neon_base64(input_vec);

        let mut indices_buf = [0u8; 16];
        vst1q_u8(indices_buf.as_mut_ptr(), indices);

        println!("\n=== ENCODE ===");
        println!("6-bit indices from NEON: {:?}", &indices_buf);

        // Check if any indices are out of range (> 63)
        let mut bad_indices = Vec::new();
        for (i, &idx) in indices_buf.iter().enumerate() {
            if idx > 63 {
                bad_indices.push((i, idx));
            }
        }
        if !bad_indices.is_empty() {
            println!("⚠️  BAD INDICES (>63): {:?}", bad_indices);
        }

        // Translate to base64 chars using standard alphabet
        let alphabet = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
        let mut encoded = Vec::new();
        for &idx in &indices_buf {
            if (idx as usize) < alphabet.len() {
                encoded.push(alphabet[idx as usize]);
            } else {
                encoded.push(b'?');
            }
        }

        println!("Encoded chars: {}", String::from_utf8_lossy(&encoded));
        println!("Encoded hex: {:02X?}", &encoded);

        // Step 2: Verify with scalar encode
        println!("\n=== SCALAR REFERENCE ===");
        let scalar_encoded = base64_encode_scalar(data);
        println!("Scalar encoded: {}", scalar_encoded);

        if encoded != scalar_encoded.as_bytes() {
            println!("❌ NEON encode doesn't match scalar!");
            println!("Differences:");
            for i in 0..16 {
                if i < encoded.len() && i < scalar_encoded.len() {
                    let neon_char = encoded[i] as char;
                    let scalar_char = scalar_encoded.chars().nth(i).unwrap();
                    if neon_char != scalar_char {
                        println!("  Position {}: NEON='{}' (idx={}), Scalar='{}' (idx={})",
                            i, neon_char, indices_buf[i], scalar_char,
                            alphabet.iter().position(|&c| c == scalar_char as u8).unwrap_or(255));
                    }
                }
            }
        } else {
            println!("✅ NEON encode matches scalar");
        }

        // Step 3: Try to decode
        println!("\n=== DECODE ===");
        let decode_result = decode_base64_neon(&encoded);

        match decode_result {
            Some(decoded) => {
                println!("Decoded: {:?}", String::from_utf8_lossy(&decoded));
                println!("Decoded hex: {:02X?}", &decoded[..12.min(decoded.len())]);

                if &decoded[..12] == data {
                    println!("✅ Roundtrip successful");
                } else {
                    println!("❌ Decoded data doesn't match input");
                }
            }
            None => {
                println!("❌ Decode returned None");

                // Check which chars failed validation
                println!("\nValidating each encoded char:");
                let decode_lut = build_decode_lut();
                for (i, &ch) in encoded.iter().enumerate() {
                    let idx = decode_lut[ch as usize];
                    if idx == 0xFF {
                        println!("  Position {}: char='{}' (0x{:02X}) -> INVALID",
                            i, ch as char, ch);
                    }
                }
            }
        }
    }
}

unsafe fn reshuffle_neon_base64(input: uint8x16_t) -> uint8x16_t {
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

fn base64_encode_scalar(data: &[u8]) -> String {
    let alphabet = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    let mut result = String::new();

    for chunk in data.chunks(3) {
        let b0 = chunk[0];
        let b1 = if chunk.len() > 1 { chunk[1] } else { 0 };
        let b2 = if chunk.len() > 2 { chunk[2] } else { 0 };

        result.push(alphabet[(b0 >> 2) as usize] as char);
        result.push(alphabet[(((b0 & 0x03) << 4) | (b1 >> 4)) as usize] as char);
        result.push(alphabet[(((b1 & 0x0F) << 2) | (b2 >> 6)) as usize] as char);
        result.push(alphabet[(b2 & 0x3F) as usize] as char);
    }

    result
}

fn build_decode_lut() -> [u8; 256] {
    let mut lut = [0xFF; 256];
    let alphabet = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

    for (idx, &ch) in alphabet.iter().enumerate() {
        lut[ch as usize] = idx as u8;
    }

    lut
}

unsafe fn decode_base64_neon(encoded: &[u8]) -> Option<Vec<u8>> {
    use std::arch::aarch64::*;

    if encoded.len() < 16 {
        return None;
    }

    let input_vec = vld1q_u8(encoded.as_ptr());
    let mut char_buf = [0u8; 16];
    vst1q_u8(char_buf.as_mut_ptr(), input_vec);

    // Validate and translate
    let decode_lut = build_decode_lut();
    let mut indices_buf = [0u8; 16];

    for j in 0..16 {
        let idx = decode_lut[char_buf[j] as usize];
        if idx == 0xFF {
            return None;
        }
        indices_buf[j] = idx;
    }

    let indices = vld1q_u8(indices_buf.as_ptr());

    // Unpack 6-bit indices to 8-bit bytes
    let mut out_buf = [0u8; 16];
    for j in 0..4 {
        let base = j * 4;
        let a = indices_buf[base];
        let b = indices_buf[base + 1];
        let c = indices_buf[base + 2];
        let d = indices_buf[base + 3];

        out_buf[j * 3] = (a << 2) | (b >> 4);
        out_buf[j * 3 + 1] = (b << 4) | (c >> 2);
        out_buf[j * 3 + 2] = (c << 6) | d;
    }

    Some(out_buf.to_vec())
}
