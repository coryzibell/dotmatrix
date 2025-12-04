# base-d Schema Error Message Analysis

## Current Error Inventory

### From `types.rs` SchemaError Enum

| Error Variant | Current Message | Context |
|---------------|----------------|---------|
| `InvalidTypeTag(u8)` | `"invalid type tag: {tag}"` | Type tag outside 0-7 range |
| `ValueCountMismatch` | `"value count mismatch: expected {expected}, got {actual}"` | Values don't match rows × fields |
| `UnexpectedEndOfData` | `"unexpected end of data"` | Binary stream truncated |
| `InvalidVarint` | `"invalid varint encoding"` | Varint exceeds 64 bits |
| `InvalidUtf8` | `"invalid UTF-8 string: {e}"` | UTF-8 decode failed |
| `TypeMismatch` | `"type mismatch for field '{field}': expected {expected}, got {actual}"` | Value type doesn't match field type |
| `InvalidNullBitmap` | `"invalid null bitmap: expected {expected_bytes} bytes, got {actual_bytes}"` | Null bitmap size wrong |
| `InvalidInput(String)` | `"invalid input: {msg}"` | Various JSON parsing issues |
| `InvalidFrame(String)` | `"invalid frame: {msg}"` | Missing delimiters |
| `InvalidCharacter(String)` | `"invalid character: {msg}"` | Non-display96 character |

### Usage Analysis

#### JSON Parser (`parsers/json.rs`)
- Line 13: `InvalidInput("Invalid JSON: {e}")` - Generic serde error passthrough
- Line 19: `InvalidInput("Expected JSON object or array")` - Wrong root type
- Line 28: `InvalidInput("Empty array")` - Empty input
- Line 40: `InvalidInput("Array must contain only objects")` - Mixed array types
- Line 337: `InvalidInput("Type mismatch: expected {:?}, got number")` - Debug format leak
- Line 347: `InvalidInput("Expected array type")` - Missing context
- Line 357: `InvalidInput("Nested objects should be flattened")` - Internal error leaked

#### Binary Unpacker (`binary_unpacker.rs`)
- Lines 36, 45, 144: `UnexpectedEndOfData` - No context about what was expected
- Line 255: `InvalidVarint` - No hint about position or value
- Lines 62, 119, 222: `InvalidUtf8(e)` - No field name context
- Line 47: `InvalidTypeTag(tag)` - No position or expected range

#### Frame Decoder (`frame.rs`)
- Lines 47-50: `InvalidFrame` with delimiter context (GOOD)
- Lines 54-57: `InvalidFrame` with delimiter context (GOOD)
- Lines 134-137: `InvalidCharacter` with position and char code (GOOD)

## Problems

### 1. **Debug Format Leaks**
- Line 337 in json.rs: `"expected {:?}"` exposes internal enum representation
- Users see `FieldType::U64` instead of `"unsigned integer"`

### 2. **No Context for Binary Errors**
- `UnexpectedEndOfData` doesn't say what was being read
- `InvalidVarint` doesn't indicate position in stream
- Type tag errors don't show valid range

### 3. **Unclear User Guidance**
- "Empty array" - is this an error? What should user do?
- "Expected JSON object or array" - doesn't explain why this restriction exists
- "Nested objects should be flattened" - internal implementation detail

### 4. **Missing Position Information**
- JSON errors don't indicate which field or row failed
- Binary errors don't show byte offset
- Only frame decoder has position info

### 5. **Inconsistent Detail Level**
- Frame errors are excellent (char, unicode, position)
- Binary errors are minimal (no context)
- JSON errors are mixed

## Proposed Improvements

### Priority 1: Fix Debug Format Leaks

Add helper to convert `FieldType` to user-friendly string:

```rust
impl FieldType {
    pub fn display_name(&self) -> &str {
        match self {
            FieldType::U64 => "unsigned integer",
            FieldType::I64 => "signed integer",
            FieldType::F64 => "floating-point number",
            FieldType::String => "string",
            FieldType::Bool => "boolean",
            FieldType::Null => "null",
            FieldType::Array(et) => "array",
            FieldType::Any => "any type",
        }
    }
}
```

### Priority 2: Add Context to Binary Errors

Enhance error variants:

```rust
// Before
UnexpectedEndOfData

// After
UnexpectedEndOfData {
    context: String,  // "reading field name", "decoding varint for row count"
    position: usize,  // byte offset
}

// Before
InvalidVarint

// After
InvalidVarint {
    context: String,  // "row count", "string length", "value at row 2 field 'id'"
    position: usize,
}
```

### Priority 3: Improve User Guidance

Make errors educational:

```rust
// Before
"Empty array"

// After
"Empty array - cannot infer schema from zero rows. Provide at least one object."

// Before
"Expected JSON object or array"

// After
"Expected JSON object or array at root level. Schema encoding works with:
  - Single object: {\"name\": \"value\"}
  - Array of objects: [{\"id\": 1}, {\"id\": 2}]
  - Object with array: {\"users\": [{\"id\": 1}]}"

// Before
"Array must contain only objects"

// After
"Array must contain only objects (tabular data). Found {actual_type} at index {idx}.
Schema encoding expects homogeneous arrays of objects like [{\"id\":1},{\"id\":2}]."
```

### Priority 4: Add Field/Position Context to JSON Errors

Track parse path:

```rust
// In json_to_schema_value()
Err(SchemaError::TypeMismatch {
    field: field_name.to_string(),  // "user.profile.age"
    expected: expected_type.display_name().to_string(),
    actual: actual_value_description,
    row: Some(row_idx),  // NEW
})
```

### Priority 5: Enhance Type Mismatch Messages

```rust
// Before
"type mismatch for field 'age': expected U64, got number"

// After
"Type mismatch in field 'age' at row 3: expected unsigned integer, but found negative number (-5).
Hint: Use signed integer type (i64) for negative numbers, or ensure all values are positive."
```

## Implementation Plan

1. Add `FieldType::display_name()` method
2. Add `context` and `position` fields to binary errors
3. Update all error construction sites with better messages
4. Add hints/suggestions to common errors
5. Test error messages manually with CLI
