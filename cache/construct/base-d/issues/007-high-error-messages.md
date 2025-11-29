## Improve error messages with context

**Type:** `issue`
**Labels:** `identity:persephone`, `identity:smith`, `high-priority`, `ux`

### Context

From Construct review of `base-d` project. Persephone and Trinity identified UX issue.

**Source:** `~/.matrix/cache/construct/base-d/ux-recommendations.md`

### Problem

Error messages show raw debug output without helpful context:

```
Error: InvalidCharacter('_')
```

Should be:

```
Error: Invalid base64 character '_' at position 12

Base64 characters must be A-Z, a-z, 0-9, +, /, or = for padding.
Found: invalid_base64!
       ^
```

### Solution

Wrap errors with user-friendly context, position info, and suggestions.

### Implementation Steps

1. Create custom error types with context
2. Track position during decode for error reporting
3. Add valid character hints for each dictionary
4. Show pointer to invalid character position
5. Suggest fixes where possible

### Acceptance Criteria

- [ ] Errors show position in input
- [ ] Errors explain what characters are valid
- [ ] Visual pointer to problem location
- [ ] Consistent error format across all operations

### Handoff

Persephone designs error format → Smith implements → Persephone reviews UX → Neo merges
