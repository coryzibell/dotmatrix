# Document localStorage JWT security tradeoff

**Type:** `issue`
**Labels:** `identity:morpheus`, `security`, `documentation`

## Context

From Construct review of `veoci-app-template-construct`. Cypher flagged localStorage usage; Spoon reframed as documentation issue rather than code change.

**Sources:**
- `~/.matrix/cache/construct/veoci-app-template-construct/security-findings.md`
- `~/.matrix/cache/construct/veoci-app-template-construct/perspective-spoon.md`

## Problem

The auth store uses localStorage for JWT tokens:
```typescript
authToken: localStorage.getItem('authToken'),
```

This is vulnerable to XSS attacks but may be the correct choice if:
- Veoci API doesn't support httpOnly cookies
- The template has no control over backend auth mechanism

**The issue isn't the code - it's the lack of documentation explaining the tradeoff.**

Developers using this template don't know:
- Why localStorage was chosen
- What the security implications are
- How to migrate to httpOnly cookies if their deployment supports it

## Solution

Add documentation explaining the security model and migration path.

## Implementation Steps

1. Add comment block in `src/store/auth.ts`:
   ```typescript
   /**
    * SECURITY NOTE: Token Storage
    *
    * This template stores JWT tokens in localStorage for simplicity.
    *
    * TRADEOFFS:
    * - Pros: Works across tabs, survives page refresh, no backend changes needed
    * - Cons: Vulnerable to XSS attacks (any injected script can steal tokens)
    *
    * FOR PRODUCTION APPS:
    * If your Veoci deployment supports httpOnly cookies, migrate token storage:
    * 1. Configure backend to set httpOnly, Secure, SameSite=Strict cookies
    * 2. Remove localStorage token storage
    * 3. Let browser handle token transmission automatically
    *
    * See: docs/security/token-storage.md for migration guide
    */
   ```

2. Create `docs/security/token-storage.md` with:
   - Current implementation explanation
   - XSS risk assessment
   - httpOnly cookie migration steps
   - CSP recommendations for XSS mitigation

3. Add security section to README linking to docs

## Acceptance Criteria

- [ ] Auth store has clear security comment
- [ ] Security documentation exists
- [ ] README links to security docs
- [ ] Developers understand tradeoff before shipping to production

## Handoff

Morpheus writes documentation. Cypher reviews for accuracy.
