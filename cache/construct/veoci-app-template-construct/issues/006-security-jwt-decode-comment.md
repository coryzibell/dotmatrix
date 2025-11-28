# Add security comment for client-side JWT decode

**Type:** `issue`
**Labels:** `identity:smith`, `security`, `P2`

## Context

From Construct review of `veoci-app-template-construct`. Cypher flagged during security audit.

**Source:** `~/.matrix/cache/construct/veoci-app-template-construct/security-findings.md`

## Problem

The auth store uses `jwt-decode` to extract claims from the token:
```typescript
import { jwtDecode } from 'jwt-decode'
// ...
const decoded = jwtDecode(token)
this.jwtClaims = decoded
```

`jwt-decode` does **not validate signatures**. If these claims are used for authorization decisions (e.g., hiding admin features), an attacker could forge tokens client-side.

This is safe IF claims are only used for UI hints (display username, check expiry). But developers may not realize the limitation.

## Solution

Add explicit warning comment to prevent misuse.

## Implementation Steps

1. Add comment above jwt-decode usage in `src/store/auth.ts`:
   ```typescript
   /**
    * WARNING: Client-side JWT decode does NOT validate signatures!
    *
    * jwt-decode only parses the token payload - it does NOT verify
    * the token is authentic or unmodified.
    *
    * USE ONLY FOR:
    * - Displaying user info (name, email)
    * - Checking token expiry for refresh timing
    * - UI hints (show/hide based on roles for UX, not security)
    *
    * DO NOT USE FOR:
    * - Authorization decisions (server must validate on every request)
    * - Access control logic
    * - Anything security-critical
    *
    * The server MUST validate the JWT signature on every API request.
    */
   const decoded = jwtDecode(token)
   ```

2. Review `jwtClaims` usage to ensure it's not used for authorization:
   ```bash
   grep -r "jwtClaims" src/
   ```

3. If any authorization logic found, refactor to server-side check

## Acceptance Criteria

- [ ] Warning comment added above jwt-decode usage
- [ ] Verified jwtClaims not used for authorization logic
- [ ] Any authorization-like usage documented as "UI hint only"

## Handoff

Smith adds comment and reviews usage. Cypher verifies no security issues remain.
