# Fiche Implementation Research - base-d

## File Locations

### Core fiche encode/decode:
- `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/fiche.rs` - Main fiche format (serialize/parse)

### JSON parsing/serialization:
- `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/parsers/json.rs` - JSON to IR
- `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/serializers/json.rs` - IR to JSON

### Types and CLI:
- `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/types.rs` - SchemaValue, FieldType, IR
- `/home/w3surf/work/personal/code/base-d/src/cli/handlers/fiche.rs` - CLI handler (thin wrapper)
- `/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/mod.rs` - Public API (encode_fiche, decode_fiche)

---

## How Nesting Currently Works

### 1. Nested OBJECTS (Flattening with `NEST_SEP`)

The system flattens nested objects using Georgian paragraph separator `჻` (U+10FB):

```rust
// parsers/json.rs line 249
fn flatten_object(obj: &Map<String, Value>, prefix: &str) -> HashMap<String, Value>
```

Input:
```json
{"user": {"profile": {"name": "alice"}}}
```

Flattened field names become:
```
user჻profile჻name
```

On decode, `unflatten_object()` (serializers/json.rs line 97) reconstructs nested structure.

**This works correctly for nested objects at any depth.**

### 2. Nested ARRAYS (Depth Markers)

Arrays use circled numbers as depth markers (fiche.rs lines 47-61):

```rust
const DEPTH_MARKERS: [char; 20] = [
    '①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩', ...
];
```

Example from tests:
```
@people┃name:str┃films:@┃vehicles:@
◉Luke┃①film/1①film/2┃∅
```

- `①` marks depth 1 array elements
- `②` would mark depth 2 (nested arrays)
- Empty arrays render as `∅`

The `value_to_str_depth()` function (fiche.rs line 308) tracks depth recursively.

---

## The Gap: Root Key with Metadata

### Current Behavior

The JSON parser (parsers/json.rs lines 132-166) handles objects in this priority:

1. **Single key + array of objects**: Treats key as `root_key`, array items as rows
   ```json
   {"users": [{"id": 1}, {"id": 2}]}
   ```
   Result: `root_key = "users"`, 2 rows

2. **Known wrapper keys** (results, data, items, records): Same treatment
   ```json
   {"results": [...], "count": 100}  // count gets LOST
   ```

3. **Single object**: Flatten and treat as 1 row

### The Problem

When JSON has **metadata alongside an array**, like:
```json
{
  "school_name": "Springfield High",
  "year": 2024,
  "students": [
    {"id": "A1", "name": "Jim"},
    {"id": "B2", "name": "Sara"}
  ]
}
```

Current parser sees this as a single object (not matching case 1 or 2), so it:
1. Flattens the whole thing as a single row
2. `students` becomes `students:@` with depth markers
3. **Loses the tabular structure** - students should be rows, not a single array field

### Where It Fails

In `parse_object()` (parsers/json.rs lines 132-226):

```rust
// Check if this is a wrapper object with one of the known keys
if obj.len() == 1 {
    // ... handles single-key wrappers
}

// Check for known wrapper patterns
for wrapper_key in WRAPPER_KEYS { ... }

// Falls through to: Single object - treat as single row
let flattened = flatten_object(&obj, "");
```

The fallthrough treats the entire object as ONE ROW with the students array as a single field value.

---

## Key Functions Summary

### Encoding Pipeline (JSON -> Fiche)

1. `JsonParser::parse()` - JSON string to IR
   - `flatten_object()` - Nested objects to dotted keys
   - `collect_field_names_ordered()` - Preserve key order
   - `infer_type()` / `infer_field_type()` - Type detection

2. `fiche::serialize()` - IR to fiche string
   - `field_type_to_str()` - FieldType to "int", "str", "@", etc.
   - `value_to_str_depth()` - Values to fiche format with depth markers

### Decoding Pipeline (Fiche -> JSON)

1. `fiche::parse()` - Fiche string to IR
   - `parse_field_def()` - "name:str" to FieldDef
   - `parse_value()` - Fiche value to SchemaValue
   - `split_by_depth_markers()` - Handle array element parsing

2. `JsonSerializer::serialize()` - IR to JSON
   - `schema_value_to_json()` - SchemaValue to serde_json Value
   - `unflatten_object()` - Dotted keys back to nested objects

---

## What Would Need to Change

To support metadata alongside arrays (like `school_name` + `students[]`):

1. **New IR capability**: Store top-level metadata separate from row data
   - Add `metadata: HashMap<String, SchemaValue>` to `SchemaHeader` or new struct

2. **Parser change**: Detect mixed pattern
   - If object has both scalar fields AND exactly one array-of-objects field
   - Extract scalars as metadata, array contents as rows

3. **Fiche format extension**: Encode metadata
   - Could use a metadata line before schema: `%school_name:Springfield▓High%year:2024`
   - Or embed in schema line: `@students[school_name=Springfield▓High,year=2024]┃id:str┃name:str`

4. **Serializer change**: Reconstruct combined structure
   - Merge metadata back with array under detected key

This is a significant change touching parser, types, fiche format, and serializer.
