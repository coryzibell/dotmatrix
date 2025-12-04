# Schema Error UX Improvements - Complete

**Date:** 2025-12-02
**Repository:** /home/w3surf/work/personal/code/base-d
**Status:** IMPLEMENTED AND TESTED

## Summary

Improved error messages for the `base-d schema` encoding/decoding feature to make them more helpful for both humans and LLM agents. The errors now provide context, show what was received, and offer recovery hints.

## Changes Made

### 1. Enhanced Error Type Signatures (types.rs)

Added context and position information to error variants:

**Before:**
```rust
UnexpectedEndOfData,
InvalidVarint,
InvalidUtf8(std::string::FromUtf8Error),
```

**After:**
```rust
UnexpectedEndOfData { context: String, position: usize },
InvalidVarint { context: String, position: usize },
InvalidUtf8 { context: String, error: std::string::FromUtf8Error },
InvalidTypeTag { tag: u8, context: Option<String> },
```

Also improved Display impl to show:
- What stage failed (reading header, decoding varint, etc.)
- Byte position where error occurred
- Helpful explanations ("appears to be truncated or corrupted")

### 2. Frame Delimiter Errors (frame.rs)

**Missing Start Delimiter:**
```
Missing start delimiter '𓍹' (U+13379).
Expected encoded data starting with 𓍹...𓍺, but received:
  no delimiters here
Hint: To encode JSON, omit the -d flag.
```

**Missing End Delimiter:**
```
Missing end delimiter '𓍺' (U+1337A).
Expected encoded data ending with 𓍺, but received:
  𓍹incomplete
The data may be truncated or corrupted.
```

Key improvements:
- Shows preview of actual input (first 40 chars)
- Explains what was expected
- Provides actionable hint (omit -d flag)
- Suggests likely cause (truncation/corruption)

### 3. Invalid Character Errors (frame.rs)

**Before:**
```
invalid character: Invalid character 'A' (U+0041) at position 0. Must be in display96 alphabet
```

**After:**
```
Invalid character 'A' (U+0041) at position 0 of 3 (looks like Base64/hex - this is not the correct encoding).
Expected only display96 alphabet characters (box drawing, blocks, geometric shapes).
```

Improvements:
- Shows total length context (position X of Y)
- Detects common wrong encodings (Base64, hex, ASCII)
- Explains what display96 actually is
- More helpful than just "must be in alphabet"

### 4. Binary Unpacker Errors (binary_unpacker.rs)

Updated all UnexpectedEndOfData call sites to provide context:

```rust
// Reading single byte
SchemaError::UnexpectedEndOfData {
    context: "reading single byte".to_string(),
    position: self.pos,
}

// Reading multiple bytes
SchemaError::UnexpectedEndOfData {
    context: format!("reading {} bytes (only {} available)", count, self.remaining()),
    position: self.pos,
}
```

Results in errors like:
```
Unexpected end of data at byte 1: reading single byte.
The encoded data appears to be truncated or corrupted.
```

### 5. JSON Parse Errors (parsers/json.rs)

**Invalid JSON Syntax:**
```
Invalid JSON syntax: expected value at line 1 column 1
Ensure the input is valid JSON.
```

**Wrong Type at Root:**
```
Expected JSON object or array at root level.
Schema encoding works with:
- Single object: {"name": "value"}
- Array of objects: [{"id": 1}, {"id": 2}]
- Object with array: {"users": [{"id": 1}]}
```

Shows examples of what actually works, not just what failed.

## Testing Results

All error scenarios tested and verified:

### 1. Invalid JSON Input
```bash
echo 'invalid json{' | base-d schema
# Error: Invalid JSON syntax: expected value at line 1 column 1
```
✓ Clear, points to exact location

### 2. Missing Frame Delimiters
```bash
echo 'no delimiters here' | base-d schema -d
# Error: Missing start delimiter, shows what was received, hints to omit -d
```
✓ Shows input preview, provides recovery hint

### 3. Invalid Characters
```bash
echo '𓍹ABC𓍺' | base-d schema -d
# Error: Detects Base64/hex, explains display96 alphabet
```
✓ Intelligent detection, helpful context

### 4. Truncated Data
```bash
echo '𓍹━𓍺' | base-d schema -d
# Error: Unexpected end at byte 1 while reading single byte
```
✓ Shows exact position and what was being read

### 5. Wrong JSON Type
```bash
echo '"just a string"' | base-d schema
# Error: Shows examples of valid inputs
```
✓ Educational, not just rejecting

### 6. Missing End Delimiter
```bash
echo '𓍹incomplete' | base-d schema -d
# Error: Shows what was received, suggests truncation
```
✓ Helpful diagnosis

### 7. Successful Roundtrip
```bash
echo '{"users":[{"id":1,"name":"alice"}]}' | base-d schema | base-d schema -d
# Output: {"users":[{"id":1,"name":"alice"}]}
```
✓ No regression, still works perfectly

## UX Principles Applied

### 1. Scannable
- First line contains the core problem
- Details follow on separate lines
- Clear visual structure with newlines

### 2. Contextual
- Shows what was received vs expected
- Provides position/location information
- Explains the stage where failure occurred

### 3. Actionable
- "Hint: To encode JSON, omit the -d flag"
- Shows examples of valid input
- Suggests likely causes (truncation, wrong encoding)

### 4. Respectful Tone
- "Failed to parse" not "Invalid input"
- "Expected... but received" not "You provided wrong"
- Explains, doesn't blame

### 5. Machine-Parseable
- Consistent format
- Exit codes (1 for errors)
- Position numbers and categories
- LLMs can extract key info

## For LLM Agents

Error messages now provide:
1. **Category** - First word (Missing/Invalid/Unexpected/Failed)
2. **Context** - What stage/operation failed
3. **Position** - Byte offset where applicable
4. **Received** - Preview of actual input
5. **Expected** - What format was anticipated
6. **Hint** - Recovery suggestion

Example LLM-parseable structure:
```
[Category]: [detail]
[Explanation line]
  [Input preview]
[Optional hint]
```

This allows LLMs to:
- Route to correct recovery logic by category
- Understand what went wrong from context
- Self-correct with hints
- Debug with input previews

## Files Modified

1. **/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/types.rs**
   - Enhanced error enum variants with context
   - Improved Display impl messages

2. **/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/frame.rs**
   - Added input preview to frame errors
   - Intelligent character type detection
   - Recovery hints

3. **/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/binary_unpacker.rs**
   - Updated all error call sites
   - Added context and position to all errors

4. **/home/w3surf/work/personal/code/base-d/src/encoders/algorithms/schema/parsers/json.rs**
   - Enhanced JSON parse errors (already done)
   - Added examples to type mismatch errors

## Before/After Comparison

### Invalid JSON
**Before:** `invalid input: Invalid JSON: expected value at line 1 column 1`
**After:** `Invalid JSON syntax: expected value at line 1 column 1\nEnsure the input is valid JSON.`

Improvement: Clearer prefix, helpful guidance

### Missing Delimiter
**Before:** `invalid frame: Missing start delimiter '𓍹' (U+13379)`
**After:** Shows delimiter + input preview + hint to omit -d flag

Improvement: 3x more context, actionable

### Invalid Character
**Before:** `invalid character: Invalid character 'A' (U+0041) at position 0. Must be in display96 alphabet`
**After:** Adds position context (0 of 3), detects Base64, explains alphabet

Improvement: Smarter, more educational

### Truncated Data
**Before:** `unexpected end of data`
**After:** `Unexpected end of data at byte 1: reading single byte.\nThe encoded data appears to be truncated or corrupted.`

Improvement: From cryptic to diagnostic

## Impact

**For humans:**
- Errors feel understanding, not blaming
- Quick to scan and identify issue
- Clear next steps

**For LLM agents:**
- Structured, parseable format
- Enough context to self-correct
- Category-based routing possible

**For pipelines:**
- Exit codes work correctly
- stderr contains full context
- Can detect stage of failure

## What Makes These Errors Good

1. **They show empathy** - "may be truncated" not "you broke it"
2. **They teach** - Examples of valid input, explanation of display96
3. **They diagnose** - Position, stage, what was being read
4. **They guide** - Hints for recovery, suggestions
5. **They respect time** - Scannable first line, details below

The goal was: **errors should make you feel understood, not blamed.**

Mission accomplished.
