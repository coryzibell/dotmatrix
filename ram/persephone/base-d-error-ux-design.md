# base-d Error Message UX Design

**Issue:** #80 - Improve error messages with context
**Status:** Design phase (Persephone)
**Handoff:** Smith for implementation

---

## Design Principles

1. **Position matters** - Show WHERE the problem is, not just WHAT
2. **Context aids recovery** - Tell users what they can do differently
3. **Brevity is kindness** - CLI users want answers, not essays
4. **Visual anchors** - A pointer says more than a paragraph

---

## Error Formats

### 1. Invalid Character During Decode

**Current:**
```
Error: InvalidCharacter('_')
```

**Proposed:**
```
error: invalid character '_' at position 12

  SGVsbG9faW52YWxpZA==
             ^

hint: base64 allows: A-Z a-z 0-9 + / =
```

**Components:**
- **Header:** `error:` prefix (lowercase, matches rust/cargo convention)
- **Message:** character in single quotes, position as 1-indexed offset
- **Visual:** 2-space indent, full input (truncated if >60 chars), caret pointer
- **Hint:** valid character summary for this dictionary

**For multi-byte characters:**
```
error: invalid character (U+1F4A9) at position 7

  SGVsbG8=
         ^

hint: base64 allows: A-Z a-z 0-9 + / =
```

**For truncated input (>60 chars):**
```
error: invalid character '_' at position 47

  ...aW5nX3ZlcnlfbG9uZ19pbnB1dF9zdHJpbmc...
                                     ^

hint: base64 allows: A-Z a-z 0-9 + / =
```

---

### 2. Invalid Input Length

**Current:**
```
Error: Invalid padding
```

**Proposed (chunked mode):**
```
error: invalid length for base64 decode

  input is 13 characters, expected multiple of 4

hint: base64 input should be 4, 8, 12, 16... characters
      add padding (=) or check for missing characters
```

**Proposed (byte range mode with incomplete sequence):**
```
error: incomplete character sequence

  input ends with partial UTF-8 sequence

hint: byte-range encoding requires complete characters
```

---

### 3. Dictionary Not Found

**Current:**
```
Dictionary 'bas64' not found. Use --list to see available dictionaries.
```

**Proposed:**
```
error: dictionary 'bas64' not found

hint: did you mean 'base64'?
      run `base-d --list` to see all dictionaries
```

**With multiple close matches:**
```
error: dictionary 'base6' not found

hint: similar dictionaries: base64, base62, base58, base16
      run `base-d --list` to see all dictionaries
```

**With no close matches:**
```
error: dictionary 'foobar' not found

hint: run `base-d --list` to see available dictionaries
      or define custom dictionaries in ~/.config/base-d/dictionaries.toml
```

---

### 4. Ambiguous Detection

**Current:**
```
Could not detect dictionary - no matches found.
The input may not be encoded data, or uses an unknown dictionary.
```

**Proposed (no matches):**
```
error: could not detect encoding

  no dictionaries match this input

hint: the input may be plain text or use an unsupported encoding
      try --decode=<dictionary> to decode with a specific dictionary
```

**Proposed (ambiguous - multiple high confidence):**
```
error: ambiguous encoding detected

  multiple dictionaries match with similar confidence:
    base64     92%
    base64url  91%

hint: use --decode=base64 or --decode=base64url explicitly
      or use --show-candidates=5 to see more options
```

**Proposed (low confidence best match):**
```
warning: low confidence detection (47%)

  best match: base85
  decoded output may be incorrect

hint: use --decode=base85 to confirm, or try a different dictionary
```

---

## Color Scheme (when terminal supports it)

| Element | Color | ANSI |
|---------|-------|------|
| `error:` | red | `\x1b[31m` |
| `warning:` | yellow | `\x1b[33m` |
| `hint:` | cyan | `\x1b[36m` |
| pointer `^` | red | `\x1b[31m` |
| quoted values | bold | `\x1b[1m` |

Respect `--no-color` flag and `NO_COLOR` environment variable.

---

## Implementation Notes for Smith

### New Error Type Structure

```rust
pub struct DecodeErrorContext {
    pub kind: DecodeErrorKind,
    pub position: Option<usize>,      // 0-indexed
    pub input_snippet: Option<String>,
    pub dictionary_name: Option<String>,
    pub valid_chars_hint: Option<String>,
}

pub enum DecodeErrorKind {
    InvalidCharacter(char),
    EmptyInput,
    InvalidPadding,
    InvalidLength { actual: usize, expected_multiple: usize },
}
```

### Character Position Tracking

Track position during decode loop. For multi-byte chars, count grapheme clusters not bytes.

### Hint Generation

For invalid character errors:
- base16: `0-9 A-F` (or `0-9 a-f` for lowercase variant)
- base32: `A-Z 2-7 =`
- base58: `1-9 A-H J-N P-Z a-k m-z` (note: no 0, I, O, l)
- base64: `A-Z a-z 0-9 + / =`
- base64url: `A-Z a-z 0-9 - _ =`

For ByteRange mode:
- `Unicode range U+{start:04X} to U+{start+255:04X}`

### Dictionary Name Suggestions

Use edit distance (Levenshtein) with threshold of 3 for "did you mean" suggestions.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Decode/encode error (invalid input) |
| 2 | Configuration error (bad dictionary, etc) |
| 3 | I/O error (file not found, etc) |

---

## Review Checklist (for Persephone)

- [ ] Error messages fit in 80-column terminal
- [ ] Visual pointer aligns correctly with problem character
- [ ] Hints are actionable, not just informative
- [ ] Color degrades gracefully to plain text
- [ ] Messages don't leak internal implementation details
- [ ] Tone is helpful, not condescending

---

*The finishing kiss: These errors should feel like a helpful colleague pointing at your screen, not a compiler shouting at you.*
