#!/usr/bin/env python3
"""Remove base32 methods from large.rs"""

# Line ranges to delete (method_name: (start_line, end_line))
# Note: Line numbers are 1-indexed
TO_DELETE = [
    ("encode_neon_base32", 188, 261),  # Including comment
    ("encode_scalar_base32", 386, 408),  # Including comment
    ("encode_ssse3_range_reduction_5bit", 478, 565),  # Including comment
    ("encode_avx512_vbmi_base32", 693, 760),  # Including comment
    ("encode_scalar_base32_x86", 857, 879),  # Including comment
    ("is_rfc4648_base32", 960, 969),  # Including comment and blank line
    ("decode_ssse3_multi_range_5bit", 1028, 1070),  # Including comment
    ("unpack_5bit_ssse3", 1166, 1201),  # Including comment
    ("decode_ssse3_base32_rfc4648", 1203, 1274),  # Including comment
    ("decode_neon_base32_rfc4648", 1276, 1344),  # Including comment
]

file_path = "/home/w3surf/work/personal/code/base-d/src/simd/lut/large.rs"

# Read file
with open(file_path, 'r') as f:
    lines = f.readlines()

# Create set of line numbers to delete (convert to 0-indexed)
lines_to_delete = set()
for name, start, end in TO_DELETE:
    for line_num in range(start - 1, end):  # Convert to 0-indexed
        lines_to_delete.add(line_num)
    print(f"Marking {name}: lines {start}-{end} for deletion")

# Write back, skipping deleted lines
with open(file_path, 'w') as f:
    for i, line in enumerate(lines):
        if i not in lines_to_delete:
            f.write(line)

print(f"\nDeleted {len(lines_to_delete)} lines from {file_path}")
