# Phase 2 Complete: JSON Parser & Serializer

## Files Created

1. `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/parsers/json.rs` (460 lines)
   - `JsonParser` implementing `InputParser` trait
   - Handles objects, arrays, nested structures, all types
   - Flattens nested objects to dotted keys
   - Preserves field insertion order
   - Detects root key pattern for tabular data

2. `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/serializers/json.rs` (225 lines)
   - `JsonSerializer` implementing `OutputSerializer` trait
   - Unflattens dotted keys back to nested objects
   - Reconstructs arrays for multiple rows
   - Applies root key when present
   - Handles null bitmap correctly

## Files Modified

1. `src/encoders/algorithms/schema/types.rs`
   - Added `InvalidInput(String)` error variant

2. `src/encoders/algorithms/schema/parsers/mod.rs`
   - Added `pub mod json` and `pub use json::JsonParser`

3. `src/encoders/algorithms/schema/serializers/mod.rs`
   - Added `pub mod json` and `pub use json::JsonSerializer`

4. `src/encoders/algorithms/schema/mod.rs`
   - Added 5 integration tests for full JSON roundtrip

## Design Decisions

### 1. Root Key Detection
Only treat single-key objects as root key pattern if the array contains objects:
- `{"users":[{"id":1}]}` → root key "users"
- `{"scores":[1,2,3]}` → regular field with array value

### 2. Field Ordering
Preserve insertion order from JSON objects (serde_json maintains this).
Helper function `collect_field_names_ordered` walks structure in order.

### 3. Type Inference
- Numbers without fractional part → I64 or U64 based on sign
- Numbers with fractional part → F64
- Arrays → infer from first non-null element
- Empty arrays → Array(Null)
- Null values set bitmap and field type inferred from other rows

### 4. Flattening Strategy
Nested objects flattened to dotted keys during parse:
- `{"a":{"b":{"c":1}}}` → field "a.b.c"
Unflattened during serialization by reconstructing nested structure.

### 5. Null Handling
- Null JSON values set bit in null_bitmap
- SchemaValue::Null stored in values array
- Serializer checks bitmap via `ir.is_null()` before converting

## Test Results

All 52 schema tests pass:
- 10 parser tests (simple, nested, arrays, nulls, types)
- 9 serializer tests (roundtrip for all cases)
- 5 JSON integration tests (full roundtrip through binary)
- 28 existing schema tests (types, packer, unpacker)

Full test suite: 333 tests pass, 0 failures

## Edge Cases Handled

1. **Empty arrays**: `{"items":[]}` → Array(Null)
2. **Deeply nested objects**: `{"a":{"b":{"c":{"d":1}}}}` → field "a.b.c.d"
3. **Null values**: Proper bitmap handling, field order independent
4. **Homogeneous arrays**: `{"scores":[1,2,3]}` → Array(U64)
5. **Root key with array**: `{"users":[{...}]}` preserved on roundtrip
6. **All scalar types**: u64, i64, f64, string, bool, null tested
7. **Mixed null/non-null**: Type inference across rows

## Performance Characteristics

- Parser: O(n) where n = total JSON tokens
- Flattening: Single pass with HashMap storage
- Serializer: O(n) where n = total values
- Unflattening: Recursive insertion, O(depth * fields)
- Type inference: Single pass over all rows per field

## Next Steps

Phase 3 will add CSV/TSV parser and serializer using same IR.
