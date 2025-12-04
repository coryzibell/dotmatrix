# base-d Schema Error Message Improvements

## Summary

Improved error messages in base-d's schema encoding feature to be more educational and actionable for users. All errors now provide context, explain what went wrong, and often suggest how to fix the issue.

## Changes Made

### 1. Enhanced Error Type Definitions

#### Added Context Fields to Binary Errors

**Before:**
```rust
UnexpectedEndOfData
InvalidVarint
InvalidUtf8(std::string::FromUtf8Error)
InvalidTypeTag(u8)
```

**After:**
```rust
UnexpectedEndOfData { context: String, position: usize }
InvalidVarint { context: String, position: usize }
InvalidUtf8 { context: String, error: std::string::FromUtf8Error }
InvalidTypeTag { tag: u8, context: Option<String> }
TypeMismatch { field: String, expected: String, actual: String, row: Option<usize> }
```

### 2. Added User-Friendly Type Names

**New helper method:**
```rust
impl FieldType {
    pub fn display_name(&self) -> String {
        // Returns "unsigned integer" instead of "FieldType::U64"
        // Returns "array of string" instead of "FieldType::Array(Box(FieldType::String))"
    }
}
```

### 3. Improved Error Messages

#### JSON Parsing Errors

| Scenario | Before | After |
|----------|--------|-------|
| Empty array | `"Empty array"` | `"Empty array - cannot infer schema from zero rows.\nProvide at least one object in the array."` |
| Invalid JSON | `"Invalid JSON: {e}"` | `"Invalid JSON syntax: {e}\nEnsure the input is valid JSON."` |
| Wrong root type | `"Expected JSON object or array"` | Multi-line explanation with examples |
| Array with primitives | `"Array must contain only objects"` | `"Array must contain only objects (tabular data). Found {type} at index {idx}.\nSchema encoding expects arrays of objects like: [{\"id\": 1}, {\"id\": 2}]"` |

#### Binary Decoding Errors

| Scenario | Before | After |
|----------|--------|-------|
| Truncated data | `"unexpected end of data"` | `"Unexpected end of data at byte {pos}: {context}.\nThe encoded data appears to be truncated or corrupted."` |
| Invalid varint | `"invalid varint encoding"` | `"Invalid varint encoding at byte {pos}: {context}.\nVarint exceeded maximum 64-bit length or was malformed."` |
| Invalid UTF-8 | `"invalid UTF-8 string: {e}"` | `"Invalid UTF-8 string while decoding {context}: {e}"` |
| Invalid type tag | `"invalid type tag: {tag}"` | `"Invalid type tag {tag} at byte offset{context}. Valid type tags are 0-7."` |

#### Frame Errors (Already Good)

These were already well-designed:
- Show Unicode codepoints
- Indicate position
- Explain what was expected
- No changes needed

### 4. Contextual Information in All Binary Operations

Updated all binary unpacking operations to track and report:
- **What was being read:** "row count", "field 3 name", "string length"
- **Where it failed:** byte offset in the stream
- **What was expected:** valid ranges, required delimiters

Example call sites:
```rust
// Before
decode_varint(cursor)?

// After
decode_varint(cursor, "row count")?

// Before
String::from_utf8(bytes).map_err(SchemaError::InvalidUtf8)?

// After
String::from_utf8(bytes).map_err(|e| SchemaError::InvalidUtf8 {
    context: format!("field {} name", idx),
    error: e,
})?
```

## Example Error Messages

### Empty Array Input
```
Empty array - cannot infer schema from zero rows.
Provide at least one object in the array.
```

### Array with Primitives
```
Array must contain only objects (tabular data). Found number at index 0.
Schema encoding expects arrays of objects like: [{"id": 1}, {"id": 2}]
```

### Invalid JSON
```
Invalid JSON syntax: key must be a string at line 1 column 2
Ensure the input is valid JSON.
```

### Truncated Binary Data
```
Unexpected end of data at byte 2: reading 83 bytes.
The encoded data appears to be truncated or corrupted.
```

### Invalid Frame Delimiter
```
Missing end delimiter '𓍺' (U+1337A).
Expected encoded data ending with 𓍺, but received:
  𓍹test
The data may be truncated or corrupted.
```

### Invalid Character in Encoded Data
```
Invalid character 'A' (U+0041) at position 0 of 3 (looks like Base64/hex - this is not the correct encoding).
Expected only display96 alphabet characters (box drawing, blocks, geometric shapes).
```

## Files Modified

1. `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/types.rs`
   - Added `FieldType::display_name()` method
   - Enhanced `SchemaError` enum with context fields
   - Rewrote `Display` implementation with educational messages

2. `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/binary_unpacker.rs`
   - Added position tracking to all Cursor operations
   - Added context parameters to `decode_varint()` and `decode_signed_varint()`
   - Enhanced all error construction with contextual information
   - Updated all call sites to provide meaningful context

3. `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/parsers/json.rs`
   - Improved all JSON parsing error messages
   - Added examples to error messages
   - Used `display_name()` instead of debug format
   - Clarified "internal errors" vs user errors

4. `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/mod.rs`
   - Updated test to match new error variants

## Testing

All existing tests pass without modification (except pattern matching updates for new error structure).

Manual testing confirms errors are now:
- **Clear:** Users understand what went wrong
- **Contextual:** Errors include position and what was being processed
- **Actionable:** Messages suggest how to fix the problem
- **Educational:** Users learn about the schema format from the errors

## Design Principles Applied

1. **Tell users WHERE:** Byte offsets, field indices, array positions
2. **Tell users WHAT:** What was being read when it failed
3. **Tell users WHY:** What was expected vs what was found
4. **Tell users HOW:** Provide examples of correct input
5. **Distinguish internal vs user errors:** Mark bugs vs usage issues

## Future Enhancements (Not Implemented)

These would further improve error messages but weren't in scope:

1. **Suggestions for common mistakes:**
   ```
   Hint: Did you mean to use an array of objects?
   Try: [{"value": 1}, {"value": 2}] instead of [1, 2]
   ```

2. **Show problematic JSON excerpt:**
   ```
   Error at line 3, column 15:
     "users": [1, 2, 3]
                  ^
   ```

3. **Type mismatch hints:**
   ```
   Hint: Found negative number (-5) in unsigned integer field.
   Consider changing field type to signed integer (i64).
   ```

4. **Validation mode:** Check JSON structure before encoding to report all issues at once

## Backward Compatibility

Error enum structure changed (new fields added), so:
- **Library users:** May need to update pattern matching
- **CLI users:** No breaking changes - just better error messages
- **Binary format:** No changes
