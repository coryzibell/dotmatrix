# Binary Encoding Issue - Inline Primitive Arrays

## Problem

Binary encoding fails for arrays containing null elements:
- `test_array_with_null_elements` - fails with `UnexpectedEndOfData { context: "reading single byte", position: 15 }`
- `test_mixed_array_depths` - returns empty array for `deep` field

## Root Cause #1: Null elements in arrays not handled

**Location:** `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/binary_packer.rs:111`

```rust
SchemaValue::Null => {} // Null encoded in bitmap, no value bytes
```

When packing `SchemaValue::Array([U64(1), Null, U64(3), Null, U64(5)])`:
1. Writes array length: 5
2. Calls `pack_value()` on each element
3. For `SchemaValue::Null`, writes **nothing** to buffer

Binary output:
```
[count=5] [1] [nothing] [3] [nothing] [5]
```

When unpacking with field type `Array(U64)`:
1. Reads count: 5
2. Loops 5 times calling `unpack_value(cursor, U64)`
3. Each call expects a varint
4. On iterations 2 and 4, buffer is exhausted → `UnexpectedEndOfData`

**The null bitmap only tracks nulls at the field level, not nulls inside arrays.**

## Root Cause #2: JSON serializer treats nested arrays as null

**Location:** `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/serializers/json.rs:29-35`

```rust
let json_value = if ir.is_null(row_idx, field_idx) {
    // Check if field type is Array - null in array field means empty array
    if matches!(field.field_type, FieldType::Array(_)) {
        Value::Array(vec![])
    } else {
        Value::Null
    }
} else {
    schema_value_to_json(value)?
};
```

For `test_mixed_array_depths`, the "deep" field (`Array(Array(U64))`) is incorrectly flagged as null and converted to empty array `[]`.

This is likely a separate bug in the JSON parsing/flattening logic for nested arrays.

## Solution Required

### For null elements in arrays:

**Option A: Tagged encoding for arrays with nulls**
- When packing arrays, check if any element is null
- If yes, use tagged format: write element type tag before each value
- Example: `[count=5] [tag:U64][1] [tag:Null] [tag:U64][3] [tag:Null] [tag:U64][5]`

**Option B: Inline null bitmap for arrays**
- Add a null bitmap after the array count
- Example: `[count=5] [null_bitmap=0b01010] [1] [3] [5]`

**Option C: Use FieldType::Any for arrays with nulls**
- During type inference, detect arrays with nulls
- Infer as `Array(Any)` instead of `Array(U64)`
- `Any` type already supports tagged encoding (line 274-279 in binary_unpacker.rs)

Option C is likely simplest and already implemented.

### For nested array serialization:

Need to investigate why `ir.is_null(row_idx, field_idx)` returns true for non-null nested arrays. Check the flattening/unflattening logic in JSON parser.

## Files Affected

- `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/binary_packer.rs` - pack_value() for arrays
- `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/binary_unpacker.rs` - unpack_value() for arrays
- `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/parsers/json.rs` - infer_type() or infer_field_type()
- `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/serializers/json.rs` - JSON serialization logic for arrays

## Test Cases

- `test_array_with_null_elements` at line 391 in `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/edge_cases.rs`
- `test_mixed_array_depths` at line 148 in `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/edge_cases.rs`
