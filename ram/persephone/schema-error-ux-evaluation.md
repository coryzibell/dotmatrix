# Schema Encoding Error UX Evaluation

**Date:** 2025-12-02
**Feature:** base-d schema encoding/decoding
**Repository:** /home/w3surf/work/personal/code/base-d

## Current State

### What's Good

The error messages are **technically accurate** and follow a clear pattern:
- Lowercase prefix identifies the category (`invalid input:`, `invalid frame:`, etc.)
- Structured details (Unicode codepoints, position numbers)
- Context about what was expected

Error framing is consistent:
```
{category}: {description}
```

### The Problem

These errors feel like they're written for the machine, not the human.

When a user pipes data through this tool and something breaks, they need to **quickly understand**:
1. What went wrong
2. What they should do about it
3. Whether the input or output is the problem

Current errors don't make this clear enough. Let me show you what it feels like.

---

## Error Scenarios (as Carmel)

### Invalid JSON Input

**Current:**
```
invalid input: Invalid JSON: expected value at line 1 column 1
```

**Experience:**
- I see "invalid input" and think: input to what? The schema encoder? The JSON parser?
- The serde error is nested: "Invalid JSON: expected value..." - that's redundant
- No guidance on what valid input looks like
- Exit code 1 (good - machine-parseable)

**What I need:**
- Clear that this is the *JSON parsing stage* that failed
- The actual input snippet that broke (first N chars)
- One-line hint about valid format

---

### Missing Frame Delimiters (Decode)

**Current:**
```
invalid frame: Missing start delimiter '𓍹' (U+13379)
```

**Experience:**
- Error is clear and scannable
- Unicode codepoint helpful for debugging display issues
- But: doesn't tell me if I'm trying to decode raw JSON vs encoded data
- If I'm a first-time user, I don't know what "frame delimiters" are

**What I need:**
- Recognition that I might be passing the wrong thing entirely
- Hint: "Expected encoded data starting with 𓍹...𓍺"
- Sample of what I *did* pass (first 20 chars)

---

### Invalid Characters in Encoded Payload

**Current:**
```
invalid character: Invalid character 'A' (U+0041) at position 0. Must be in display96 alphabet
```

**Experience:**
- Very good - tells me exactly what broke and where
- Position number helps locate the problem
- "display96 alphabet" is jargon but searchable
- Missing: what characters *are* valid? (URL? Reference?)

**What I need:**
- This is close to perfect
- Would be better with context: "character 'A' at position 0 (out of 3 chars)"
- Optional: hint about whether this looks like base64/hex/raw text

---

### Truncated/Corrupted Binary Data

**Current:**
```
unexpected end of data
```

**Experience:**
- This is the worst one. What data? Where was the end? How much is missing?
- No context about what stage of decoding failed
- No hint about whether input is malformed vs partially transmitted
- Feels like a low-level C error

**What I need:**
- "Decoding failed: ran out of data while reading {header/values/string/varint}"
- How many bytes received vs expected (if knowable)
- Suggestion: "Input may be truncated or corrupted"

---

## For LLM Agents

LLMs calling this tool need:
1. **Structured error categories** - prefix is good, but could be more specific
2. **Machine-parseable details** - position numbers, expected/actual counts (good)
3. **Actionable next steps** - missing

Current format works for parsing but doesn't guide recovery.

Ideal format for LLM consumption:
```
ERROR: {category}
Reason: {human description}
Location: {position/stage}
Received: {snippet of actual input}
Expected: {format description}
```

This lets both humans and LLMs quickly extract:
- Category (for routing/retry logic)
- Context (for debugging)
- Recovery hint (for self-correction)

---

## Specific Issues

### 1. Error Prefix Granularity

Current categories:
- `invalid input` - too broad (JSON parse vs format validation?)
- `invalid frame` - good
- `invalid character` - good
- `unexpected end of data` - vague

Better categories:
- `json parse error` - clear stage
- `schema error` - format validation
- `decode error` - binary unpacking
- `invalid frame` - keep
- `invalid character` - keep

### 2. Missing Context

None of the errors show what was actually received. This makes pipeline debugging hard:
```bash
cat data.json | base-d schema | base-d schema -d
# If this fails, which stage broke? What data made it through?
```

### 3. No Recovery Hints

Errors tell you what's wrong but not how to fix it:
- "Expected encoded data starting with 𓍹"
- "Hint: to encode JSON, omit the -d flag"
- "Tip: check that data wasn't corrupted in transit"

### 4. Tone

The tone is neutral-technical. Not hostile, but not helpful either.

Compare:
- Current: "invalid input: Invalid JSON: expected value at line 1 column 1"
- Better: "Couldn't parse input as JSON (expected value at line 1 column 1)"

Small shift from *blaming* the input to *explaining* the failure.

---

## Recommendations

### High Priority

1. **Add input preview to errors**
   - Show first 40 chars of received input
   - Truncate with "..." if longer
   - Helps diagnose wrong-tool-in-pipeline issues

2. **Improve "unexpected end of data"**
   - Add context: which decoding stage failed?
   - Show bytes received vs minimum expected
   - Suggest "truncated or corrupted input"

3. **Make JSON errors less nested**
   - Current: "invalid input: Invalid JSON: {serde error}"
   - Better: "Failed to parse JSON: {serde error}"

4. **Add recovery hints for common mistakes**
   - Trying to decode raw JSON: "Hint: omit -d to encode"
   - Trying to encode already-encoded data: "Hint: use -d to decode"

### Medium Priority

5. **Standardize error format for LLM parsing**
   ```
   Error: {category}
   Stage: {encode/decode/parse/unpack}
   Input: {first 40 chars}...
   Issue: {description}
   ```

6. **Add --verbose flag for debugging**
   - Show full input
   - Show binary hex dump
   - Show intermediate stages

### Low Priority

7. **Error reference URLs**
   - "invalid character: ... (see: base-d.io/errors/invalid-char)"
   - Helps new users understand display96, frame delimiters, etc.

8. **Suggest similar valid input**
   - "Did you mean to encode this JSON first?"
   - Requires heuristics, might be too clever

---

## Implementation Notes

Error display happens in two places:

1. **SchemaError::Display impl** (`src/encoders/algorithms/schema/types.rs`)
   - Core error messages
   - No access to original input

2. **CLI handler** (`src/cli/handlers/schema.rs`)
   - Has access to full input
   - Could wrap errors with context

**Approach:** Enhance both layers:
- SchemaError: better messages, more specific variants
- CLI handler: catch errors and add input preview

**Preserve:** Machine-parseable structure (exit codes, prefixes, position numbers)

---

## Next Steps

1. Implement high-priority changes
2. Test with real error scenarios
3. Verify LLM agents can parse and recover from errors
4. Consider adding examples to error messages

The goal: errors should make you feel **understood**, not **blamed**.
