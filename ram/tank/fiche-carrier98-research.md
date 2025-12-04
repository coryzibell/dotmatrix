# Fiche and Carrier98 Research - base-d

## Executive Summary

**carrier98** is just a name for the opaque binary schema encoding (the "Schema" command).
**fiche** is the human/model-readable sibling format.

Both share the SAME underlying code:
- Same `IntermediateRepresentation` (IR)
- Same `JsonParser` for JSON -> IR
- Same type system (`FieldType`, `SchemaValue`)

**Key insight**: Fix the JSON parser, both formats benefit.

---

## Architecture Overview

```
JSON Input
    |
    v
+------------------+
|   JsonParser     |  <-- SHARED: Type inference happens here
+------------------+
    |
    v
+------------------------------+
| IntermediateRepresentation   |  <-- SHARED: IR is the bridge
+------------------------------+
    |                      |
    v                      v
+-----------+       +------------+
| carrier98 |       |   fiche    |
| (binary)  |       | (Unicode)  |
+-----------+       +------------+
    |                      |
    v                      v
display96           @root|field:type
framed              row values
```

---

## File Locations

| Component | File | Purpose |
|-----------|------|---------|
| JSON Parser | `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/parsers/json.rs` | JSON -> IR conversion, type inference |
| IR Types | `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/types.rs` | FieldType, SchemaValue, IR structs |
| Fiche Format | `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/fiche.rs` | IR -> fiche serialization |
| Schema Module | `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/mod.rs` | encode_schema, decode_schema (carrier98) |
| JSON Serializer | `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/serializers/json.rs` | IR -> JSON output |
| Binary Packer | `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/binary_packer.rs` | IR -> binary (carrier98) |
| Edge Cases | `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/edge_cases.rs` | Known edge case tests |

---

## SWAPI Edge Cases Analysis

### 1. Paginated Wrappers

```json
{"count": 82, "next": "url", "previous": null, "results": [...]}
```

**What happens now**:
- `parse_object()` at line 131 in `json.rs` checks for root key pattern
- Line 136-147: Only triggers if object has SINGLE key containing array of objects
- Paginated wrapper has 4 keys (count, next, previous, results) -> NOT root key pattern
- Falls through to "single object" handling (line 166)
- `flatten_object()` called - flattens nested objects but...

**The Bug**:
- `results` array IS an array of objects, but it's a field not root key
- Line 241-248 in `flatten_object()`: Objects are recursively flattened, but arrays are NOT
- Arrays are kept as-is and passed to `infer_type()` for field type inference

**Where it fails**:
- `json.rs` line 282-293: `infer_type()` for arrays infers from FIRST non-null element only
- If `results: [{...}, {...}]` - this works IF all objects have same structure
- The type is `FieldType::Array(Box::new(FieldType::???))` - but inner is inferred as object/string

**Specific failure point**:
- `FieldType::Array` doesn't support nested objects as element type
- Line 295-298: Objects after flatten default to `FieldType::String` (fallback)

### 2. Heterogeneous Arrays

```json
{"field": []}           // record 1
{"field": ["a", "b"]}   // record 2
```

**What happens now**:
- `infer_field_type()` (line 303-333) iterates all rows to find common type
- Line 282-293: Empty array `[]` returns `FieldType::Array(Box::new(FieldType::Null))`
- Non-empty array `["a","b"]` returns `FieldType::Array(Box::new(FieldType::String))`

**The Bug - Type Conflict**:
- Line 319-322: If types differ, returns `FieldType::Any`
- `Array(Null)` != `Array(String)` -> becomes `Any`
- But `json_to_schema_value()` (line 336-390) doesn't handle `Any` properly for arrays

**Specific failure point**:
- Line 369-384: When converting array value, expects `FieldType::Array(et)`
- If field was inferred as `Any`, this fails at line 373-377

**Secondary issue**:
- Edge case test `test_array_with_null_elements` (line 382-402) documents this:
  > "BUG: Array field containing null elements is not properly supported"
  > "Null bitmap only works for top-level fields, not array elements"

### 3. Nested Objects Within Records

```json
{"name": "Luke", "homeworld": {"name": "Tatooine", "climate": "arid"}}
```

**What happens now**:
- `flatten_object()` (line 231-252) recursively flattens nested objects
- `homeworld.name` and `homeworld.climate` become separate fields
- This WORKS for true nested objects

**BUT if nested object is in an array**:
```json
{"characters": [{"name": "Luke", "homeworld": {"name": "Tatooine"}}]}
```

**The Bug**:
- Line 241-248: Only `Value::Object` is recursively flattened
- Arrays are NOT descended into
- Inner objects within arrays remain as `Value::Object`
- Line 369-384 in `json_to_schema_value()`: Object values cause error at line 385-388

**Specific failure point**:
```rust
Value::Object(_) => Err(SchemaError::InvalidInput(
    "Internal error: Encountered nested object that wasn't flattened..."
))
```

---

## Type System Limitations

From `types.rs` line 18-28:

```rust
pub enum FieldType {
    U64,
    I64,
    F64,
    String,
    Bool,
    Null,
    Array(Box<FieldType>),  // Homogeneous arrays only
    Any,                     // Mixed-type fallback
}
```

**Key limitation**: `Array(Box<FieldType>)` assumes homogeneous element type.
No support for:
- Nested objects inside arrays
- Mixed-type array elements
- Nullable array elements (nulls inside arrays)

---

## Fix Locations (Single Point Fixes)

| Issue | File | Function | Line Range |
|-------|------|----------|------------|
| Paginated wrapper detection | json.rs | parse_object() | 131-163 |
| Array type inference | json.rs | infer_type() | 282-293 |
| Cross-row type unification | json.rs | infer_field_type() | 303-333 |
| Nested objects in arrays | json.rs | flatten_object() | 231-252 |
| Array null handling | types.rs | FieldType enum | 26 (needs extension) |

---

## Relationship Summary

```
carrier98 (Schema CLI) ----+
                           |
                           +---> JsonParser (SHARED)
                           |           |
                           |           v
fiche (Fiche CLI) ---------+    IntermediateRepresentation
                                       |
                           +-----------+-----------+
                           |                       |
                           v                       v
                     binary_packer            fiche::serialize
                     (carrier98)              (fiche format)
```

**Answer to your questions**:

1. **Is carrier98 a wrapper around fiche?** No. They're siblings - both consume the same IR.

2. **Does carrier98 have independent JSON handling?** No. Both use `JsonParser`.

3. **If we fix fiche, does carrier98 benefit?** Yes - fixing `JsonParser` fixes both.

4. **Are there separate places needing fixes?** No. All fixes are in the shared JSON parser.

---

## Recommended Fix Order

1. **Array element type unification** - Handle `Array(Null)` unifying with `Array(String)`
2. **Nested objects in arrays** - Extend flatten_object to descend into arrays
3. **Paginated wrapper detection** - Recognize SWAPI-style wrappers with results array
4. **Nullable array elements** - Extend type system for inner nulls

All fixes go in `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/parsers/json.rs`
