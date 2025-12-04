# base-d Array Flattening Bug Analysis

## Error Message
```
Internal error: Encountered nested object that wasn't flattened. This is a bug in the JSON parser.
```

## Location
- **File**: `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/parsers/json.rs`
- **Line**: 472
- **Function**: `json_to_schema_value()`

## Root Cause

The flattening logic **does not flatten objects inside arrays**. When the JSON parser encounters:

1. **Top-level array of objects** → Works (treated as tabular data, each object is flattened)
2. **Single object with nested objects** → Works (`flatten_object()` recursively flattens)
3. **Array field containing primitives** → Works (stored as `FieldType::Array`)
4. **Array field containing objects** → **FAILS**

The bug manifests when:
- An array of objects (root-level) contains objects
- Those objects have fields that are arrays of objects

## Failing Pattern

```json
{
  "services": [           // Root-level array → treated as tabular data
    {
      "service": "CSI",   // Flattened during parse_array()
      "params": [         // Field is an array
        {                 // Objects inside this array are NOT flattened
          "key": "c",     // These nested objects cause the error
          "value": "WEB"
        }
      ]
    }
  ]
}
```

## Code Flow

1. **`parse_array()` (line 37)**: Handles root-level array of objects
   - Line 76: Calls `flatten_object()` on each object in the array
   - Line 90: Calls `infer_field_type()` for each field

2. **`flatten_object()` (line 301)**: Recursively flattens nested objects
   - Line 311-314: When it encounters an object, it recursively flattens it
   - **Line 315-318**: When it encounters an array, it **stops and stores the array as-is**
   - Arrays are never recursively processed

3. **`infer_type()` (line 325)**: Determines field types
   - Line 352-364: For arrays, infers element type from first element
   - Returns `FieldType::Array(Box::new(element_type))`
   - If array contains objects, marks as `FieldType::Array(Box::new(FieldType::String))`
   - **Does not flatten objects inside arrays**

4. **`json_to_schema_value()` (line 422)**: Converts JSON to schema values
   - Line 455-469: For arrays, recursively converts each element
   - **Line 471-474**: If element is `Value::Object`, throws error
   - This is where the error occurs

## Why It Fails

The parser assumes all objects will be flattened before reaching `json_to_schema_value()`. However:

- **Top-level objects**: Flattened by `flatten_object()` ✓
- **Objects nested in objects**: Flattened recursively ✓
- **Objects nested in arrays**: **Never flattened** ✗

When `json_to_schema_value()` processes an array field, it encounters the un-flattened objects and throws the error.

## YouTube JSON Structure

The YouTube API response has this exact pattern:

```json
{
  "responseContext": {
    "serviceTrackingParams": [        // Array of objects
      {
        "service": "CSI",
        "params": [                    // Nested array of objects
          {
            "key": "c",                // ← These objects trigger the error
            "value": "WEB"
          }
        ]
      }
    ]
  }
}
```

## Minimal Reproduction

```json
{
  "services": [
    {
      "service": "CSI",
      "params": [
        {
          "key": "c",
          "value": "WEB"
        }
      ]
    }
  ]
}
```

## Solution Options

1. **Flatten arrays of objects during array processing**
   - Modify `flatten_object()` to recursively flatten arrays of objects
   - Convert arrays of objects to JSON strings or serialize differently

2. **Support nested objects in arrays**
   - Modify `json_to_schema_value()` to handle objects inside arrays
   - Flatten objects on-the-fly during value conversion

3. **Reject arrays of objects as invalid input**
   - Update error message to be more specific
   - Document that arrays must contain primitives only

## Recommendation

The current design assumes **tabular data** (flat structure). Arrays of objects inside other objects violates this assumption. The parser should either:

1. **Flatten arrays of objects** by converting them to JSON strings
2. **Reject the pattern** with a clear error message
3. **Recursively flatten** objects inside arrays using the nest separator

Option 3 seems most consistent with the existing flattening behavior.
