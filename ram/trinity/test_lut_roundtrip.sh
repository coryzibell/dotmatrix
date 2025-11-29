#!/bin/bash
cd /Users/coryzibell/work/personal/code/base-d

cat > /tmp/test_lut.rs << 'EOF'
#[test]
fn test_lut_standard_alphabet() {
    use crate::core::dictionary::Dictionary;
    use crate::simd::lut::large::LargeLutCodec;

    // Standard base64 alphabet
    let chars: Vec<char> = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        .chars()
        .collect();
    let dict = Dictionary::new(chars).unwrap();
    let codec = LargeLutCodec::from_dictionary(&dict).unwrap();

    let data = b"Hello World!";
    println!("Input: {:?}", String::from_utf8_lossy(data));

    let encoded = codec.encode(data, &dict).unwrap();
    println!("Encoded: {}", encoded);
    println!("Expected: SGVsbG8gV29ybGQh");

    let decoded = codec.decode(&encoded, &dict).unwrap();
    println!("Decoded: {:?}", String::from_utf8_lossy(&decoded));

    assert_eq!(&decoded[..], &data[..], "Roundtrip failed!");
}
EOF

cargo test --lib test_lut_standard_alphabet -- --nocapture --ignored 2>&1 | tail -30
