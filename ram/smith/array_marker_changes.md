# Array Marker Replacement: [] → ⟦⟧

## Summary
Replaced ASCII bracket array markers `[]` with mathematical brackets `⟦⟧` (U+27E6/U+27E7) in base-d's fiche implementation.

## Files Modified

### 1. **src/encoders/algorithms/schema/parsers/json.rs**
   - Changed `format!("{}[]", ...)` → `format!("{}⟦⟧", ...)`
   - Changed `ends_with("[]")` → `ends_with("⟦⟧")`
   - Updated test assertions in `test_homogeneous_array()` and `test_empty_array()`
   - 11 locations updated

### 2. **src/encoders/algorithms/schema/serializers/json.rs**
   - Changed `ends_with("[]")` → `ends_with("⟦⟧")`
   - Changed string slicing `&key[..key.len() - 2]` → `key.trim_end_matches("⟦⟧")`
   - Updated marker reconstruction logic
   - 4 locations updated

### 3. **src/encoders/algorithms/schema/fiche.rs**
   - Added backward compatibility: `s.strip_suffix("⟦⟧").or_else(|| s.strip_suffix("[]"))`
   - Updated doc comments to reference new syntax
   - Added test `test_arrays_new_bracket_syntax()` for new ⟦⟧ markers
   - Existing `test_arrays_legacy_syntax()` validates old [] markers still parse
   - 3 locations updated

## Unicode Characters
- **⟦** = U+27E6 (Mathematical Left White Square Bracket)
- **⟧** = U+27E7 (Mathematical Right White Square Bracket)
- UTF-8: 6 bytes each (0xE2 0x9F 0xA6 and 0xE2 0x9F 0xA7)

## Test Results

### Build Status
```
cargo build --release
   Compiling base-d v3.0.10
    Finished `release` profile [optimized] target(s) in 18.84s
```

### Test Suite
```
cargo test
test result: ok. 446 passed; 0 failed; 0 ignored
```

### Round-trip Tests

**Simple arrays:**
```bash
echo '{"tags":["a","b"],"items":[]}' | base-d fiche
# Output: @┃tags჻0:str┃tags჻1:str┃items⟦⟧:str┃tags⟦⟧:str
#         ◉a┃b┃∅┃∅

echo '{"tags":["a","b"],"items":[]}' | base-d fiche | base-d fiche -d
# Output: {"items":[],"tags":["a","b"]}  ✓
```

**Nested arrays:**
```bash
echo '[{"id":1,"scores":[10,20,30]},{"id":2,"scores":[15,25]}]' | base-d fiche | base-d fiche -d
# Output: [{"id":1,"scores":[10,20,30]},{"id":2,"scores":[15,25]}]  ✓
```

**Backward compatibility (old [] syntax):**
```bash
echo '@users┃id:int┃tags:str[]
◉1┃①admin①editor
◉2┃①viewer' | base-d fiche -d
# Output: {"users":[{"id":1,"tags":["admin","editor"]},{"id":2,"tags":["viewer"]}]}  ✓
```

**Complex nested structure:**
```json
{
  "metadata": "test",
  "users": [
    {
      "id": 1,
      "name": "Alice",
      "tags": ["admin", "user"],
      "scores": [95, 88, 92],
      "active": true
    },
    {
      "id": 2,
      "name": "Bob",
      "tags": ["user"],
      "scores": [],
      "active": false
    }
  ]
}
```

Encoded to fiche:
```
@users[metadata=test]┃active:bool┃id:int┃name:str┃scores჻0:int┃scores჻1:int┃scores჻2:int┃tags჻0:str┃tags჻1:str┃scores⟦⟧:str┃tags⟦⟧:str
◉true┃1┃Alice┃95┃88┃92┃admin┃user┃∅┃∅
◉false┃2┃Bob┃∅┃∅┃∅┃user┃∅┃∅┃∅
```

Round-trip verified: ✓

## Backward Compatibility

The fiche parser maintains backward compatibility:
- **New encoding**: Always uses `⟦⟧` for array markers
- **Old decoding**: Still accepts both `[]` and `⟦⟧` in type definitions
- **Parser**: `parse_type_str()` uses `.or_else()` to try both suffixes

## Implementation Notes

String handling is Unicode-aware:
- Used `trim_end_matches("⟦⟧")` instead of byte slicing
- Used `ends_with("⟦⟧")` for detection
- No assumptions about byte lengths (⟦⟧ is 6 bytes each in UTF-8, not 2)

All tests pass including:
- Unit tests (446 passed)
- Integration tests (28 passed)
- API tests (11 passed)
- Doc tests (14 passed)

