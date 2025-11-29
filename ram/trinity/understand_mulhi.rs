// Understand what _mm_mulhi_epu16 does
use std::arch::aarch64::*;

fn main() {
    println!("=== Understanding _mm_mulhi_epu16 ===\n");

    // Test values
    let a: u16 = 0x1234;
    let b: u16 = 0x0040;

    let product = (a as u32) * (b as u32);
    let lo = (product & 0xFFFF) as u16;
    let hi = (product >> 16) as u16;

    println!("Multiply: 0x{:04X} * 0x{:04X}", a, b);
    println!("  Full product: 0x{:08X}", product);
    println!("  Low 16 bits:  0x{:04X}", lo);
    println!("  High 16 bits: 0x{:04X}", hi);
    println!("  mulhi result: 0x{:04X}\n", hi);

    // What x86 does:
    // _mm_mulhi_epu16(t0, 0x04000040) where t0 has masked values
    //
    // Example with one u32 from after mask:
    let masked = 0x0C404800u32;  // From our test
    let u16_lo = (masked & 0xFFFF) as u16;  // 0x4800
    let u16_hi = (masked >> 16) as u16;     // 0x0C40

    println!("Masked u32: 0x{:08X}", masked);
    println!("  As u16[0]: 0x{:04X}", u16_lo);
    println!("  As u16[1]: 0x{:04X}\n", u16_hi);

    let mult_const_lo = 0x0040u16;
    let mult_const_hi = 0x0400u16;

    let product_lo = (u16_lo as u32) * (mult_const_lo as u32);
    let product_hi = (u16_hi as u32) * (mult_const_hi as u32);

    let result_lo = (product_lo >> 16) as u16;  // mulhi
    let result_hi = (product_hi >> 16) as u16;  // mulhi

    println!("After mulhi_epu16:");
    println!("  u16[0]: 0x{:04X} * 0x{:04X} = 0x{:08X} >> 16 = 0x{:04X}", u16_lo, mult_const_lo, product_lo, result_lo);
    println!("  u16[1]: 0x{:04X} * 0x{:04X} = 0x{:08X} >> 16 = 0x{:04X}\n", u16_hi, mult_const_hi, product_hi, result_hi);

    println!("Result u32: 0x{:04X}{:04X}\n", result_hi, result_lo);

    // The x86 code then does NO shift - it directly uses this as the result!
    // But NEON code shifts right by 10. That's wrong.

    println!("=== Correct NEON simulation ===");
    println!("vmulq_u16 gives full 16-bit product (not mulhi)");
    println!("To simulate mulhi, we need:");
    println!("  1. Use vmull_u16 (multiply to 32-bit)");
    println!("  2. Extract high 16 bits");
    println!("  OR");
    println!("  1. Multiply by larger constants");
    println!("  2. Shift to extract the high bits we want\n");

    println!("x86 approach: multiply, take bits [31:16] of 32-bit product");
    println!("NEON broken: multiply by 0x0040, shift >>10 → takes bits [25:10]");
    println!("NEON needs: multiply to get bits in correct position\n");

    // Check what the x86 version actually produces
    println!("Expected after mulhi + no shift:");
    println!("  0x{:04X} → bytes [0x{:02X}, 0x{:02X}]",
        (result_hi as u32) << 16 | result_lo as u32,
        result_lo as u8,
        (result_lo >> 8) as u8);
}
