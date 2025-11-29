## Fix Base32 padding to comply with RFC 4648

**Type:** `issue`
**Labels:** `identity:smith`, `blocker`, `compliance`

### Context

From Construct review of `base-d` project. Lock identified RFC compliance violation.

**Source:** `~/.matrix/cache/construct/base-d/compliance.md`

### Problem

Base32 encoder pads output to multiples of 4 characters instead of RFC 4648 Section 6 required multiples of 8.

This breaks interoperability with compliant implementations.

### Solution

Correct padding logic per RFC 4648 Section 6:
- Base32 output must be padded to multiples of 8 characters
- Use `=` padding character

### Implementation Steps

1. Locate Base32 padding logic in encoder
2. Change padding calculation: `(8 - (len % 8)) % 8`
3. Update tests to verify 8-character alignment
4. Test against reference implementations (openssl, coreutils)

### Acceptance Criteria

- [ ] All Base32 output is padded to multiples of 8
- [ ] Decode handles both padded and unpadded input
- [ ] Tests verify RFC compliance
- [ ] Interop tested with external tools

### Handoff

After Smith implements → Lock re-verifies compliance → Neo merges
