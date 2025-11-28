# Construct Synthesis: veoci-app-template-construct

**Generated:** 2025-11-27
**Repository:** Veoci-Labs/veoci-app-template-construct
**Platform:** Vue 3 + Vuetify 3 + Pinia + Rsbuild + TypeScript
**Purpose:** Authentication template for Veoci applications

---

## Executive Summary

This is a **production-grade starting point**, not a minimal template. It provides comprehensive authentication (including MFA support), modern tooling (Rsbuild, ESLint 9, Husky), and a well-structured Vue 3 Composition API codebase. However, it has **critical gaps** that block developer adoption and present security considerations for production use.

**The template is caught between two identities:**
- A minimal starting point (expects you to add your own tests, CI/CD, security hardening)
- A complete boilerplate (ships with 300-line auth store, MFA flows, complex proxy config)

Spoon's reframing is correct: many "issues" are appropriate for a template's role. But several blockers are genuine and should be addressed.

---

## Blockers (Must Fix Before Sharing)

### B-1: No Environment Variable Documentation
**Source:** Seraph, Morpheus, Persephone
**Impact:** Developers cannot run the template without guessing configuration

The template requires `VEOCI_API_URL` for the dev proxy, but:
- No `.env.example` file exists
- No documentation of required variables
- Dev server starts successfully even with missing config, then fails silently on first API call

**Fix:**
1. Create `.env.example`:
   ```env
   # Required: Veoci API endpoint
   VEOCI_API_URL=https://your-instance.veoci.com
   ```
2. Add environment validation to `rsbuild.config.ts` that fails fast with clear instructions

**Effort:** 30 minutes

---

### B-2: No First-Run Experience
**Source:** Seraph, Sati, Persephone
**Impact:** Template unusable without Veoci credentials

A developer clones, runs `npm run dev`, sees login page, has no credentials, and is stuck. No mock mode, no demo credentials, no guidance.

**Fix Options:**
1. **Quick:** Add README section explaining how to get Veoci sandbox access
2. **Better:** Add MSW mock API mode (`npm run dev:mock`) with demo credentials
3. **Best:** Interactive setup script (`npm run setup`)

**Effort:** 2-4 hours (MSW approach)

---

### B-3: Duplicate ESLint Configuration
**Source:** Sati
**Impact:** Developer confusion, potential conflicting rules

Both `.eslintrc.cjs` AND `eslint.config.js` exist. ESLint 9 uses flat config; having both is confusing and suggests incomplete migration.

**Fix:** Remove `.eslintrc.cjs`, keep only `eslint.config.js`

**Effort:** 5 minutes

---

### B-4: Package Name Mismatch
**Source:** Sati
**Impact:** Confusion about template identity

`package.json` says `"name": "veoci-cardwall"` but this is a generic template. New projects will inherit the wrong name.

**Fix:**
1. Rename to `veoci-app-template` or similar
2. Add template initialization script to rename for new projects

**Effort:** 30 minutes

---

## Security Considerations

### S-1: JWT Storage in localStorage
**Severity:** Context-dependent (see Spoon's reframing)
**Source:** Cypher, Keymaker

**The Issue:** Auth tokens stored in localStorage are vulnerable to XSS attacks.

**Spoon's Reframe:** This may be correct if:
- Veoci API doesn't support httpOnly cookies
- Template has no control over backend auth mechanism
- XSS risk is accepted for simplicity in a template

**Questions to Answer:**
1. Does Veoci API support httpOnly cookie authentication?
2. If not, localStorage is the only option - document the tradeoff
3. If yes, document migration path for production apps

**Recommendation:** Add comment in `auth.ts` explaining the choice and linking to httpOnly cookie migration guide if backend supports it.

---

### S-2: Client-Side JWT Decode Without Validation
**Severity:** Low (if used correctly)
**Source:** Cypher

**The Issue:** `jwt-decode` doesn't validate signatures. If decoded claims are used for authorization, it's bypassable.

**Investigation Needed:** Where are `jwtClaims` used?
- If only for UI (display username, format expiry) → Safe
- If for authorization logic (hide admin features) → Problematic

**Recommendation:** Add explicit comment:
```typescript
// WARNING: jwt-decode does NOT validate signatures
// Use ONLY for UI hints (display name, expiry check)
// Server MUST validate token on every API request
```

---

### S-3: window.veociApi Exposure in Dev Mode
**Severity:** Low (dev only)
**Source:** Cypher

The VeociJS SDK is exposed on `window` in development. Not a production issue, but:
- Could train developers to rely on it
- Accidental production deployment risk

**Recommendation:** Add build-time check to ensure it's not in production bundle, or gate behind explicit debug flag.

---

## Improvements (Should Fix)

### I-1: Zero Test Coverage
**Source:** Deus
**Spoon's Reframe:** Tests in a template test placeholder code that will be deleted

**The Balance:**
- Full test suite for template code is indeed cargo cult
- BUT: Test infrastructure setup IS valuable
- Example tests showing HOW to test Veoci integrations would help

**Recommendation:**
1. Install Vitest + @vue/test-utils
2. Add ONE example test for auth store (shows mocking pattern)
3. Add vitest.config.ts with proper Vue/Pinia setup
4. Add `npm run test` script (even if suite is minimal)

**Effort:** 2-3 hours

---

### I-2: No CI/CD Pipeline
**Source:** Niobe
**Spoon's Reframe:** Each project has different deployment; baked-in Actions may be wrong

**The Balance:**
- Generic GitHub Actions may not fit Veoci Labs' deployment
- BUT: Basic PR checks (lint, type-check, build) are universal

**Recommendation:**
1. Add `.github/workflows/ci.yml` with lint + type-check + build
2. Leave deployment to individual projects
3. Document that teams should add their own deployment pipeline

**Effort:** 1 hour

---

### I-3: Unused dotenv Dependency
**Source:** Apoc, Spoon
**Impact:** Bundle bloat, developer confusion

`dotenv` is in package.json but never imported. It's a Node.js package that does nothing in browser code.

**Recommendation:** Remove it
```bash
npm uninstall dotenv
```

**Effort:** 5 minutes

---

### I-4: Debug View Underutilized
**Source:** Persephone, Seraph
**Impact:** Debugging is harder than it should be

`/debug` exists but doesn't help diagnose common issues. Should show:
- API URL configuration
- Connection status (reachable/unreachable)
- Auth state (token present, expiry)
- localStorage dump (redacted)

**Effort:** 1-2 hours

---

### I-5: Documentation Gaps
**Source:** Morpheus
**Impact:** Onboarding friction

Missing:
- Environment setup guide
- Troubleshooting section (CORS errors, 401, proxy issues)
- Customization guide (adding pages, changing themes)
- JSDoc comments on store actions

**Effort:** 2-4 hours

---

## Ideas (Could Explore Later)

### ID-1: Extract to Package Ecosystem
**Source:** Oracle

Transform template into maintained packages:
```
@veoci/app-core        # Auth, routing
@veoci/app-components  # Shared components
@veoci/app-dev         # Proxy, mocking
```

Apps depend on packages instead of forking. Updates flow through npm.

**Assessment:** Good long-term vision, but requires significant investment. Consider after template stabilizes.

---

### ID-2: Template Versioning
**Source:** Oracle

Add:
- Version tags in Git
- CHANGELOG.md
- Migration guides between versions
- `"templateVersion": "1.0.0"` in package.json

**Assessment:** Valuable if template will be maintained long-term. Defer until governance model is established.

---

### ID-3: Multi-Template Family
**Source:** Oracle, Sati

Create variants:
- `veoci-app-minimal` - Just routing + API client
- `veoci-app-standard` - Current implementation
- `veoci-app-enterprise` - Adds testing, Storybook, a11y

**Assessment:** May be over-engineering. Consider after "standard" template is solid.

---

### ID-4: Login State Machine
**Source:** Persephone

Extract multi-step login orchestration from LoginView.vue (14KB risk) into composable or XState machine.

**Assessment:** Good refactoring target for v2. Current implementation works.

---

### ID-5: Accessibility Audit
**Source:** Zee (not dispatched, but implied by Persephone/Oracle)

Add:
- ARIA labels on login forms
- Keyboard navigation patterns
- Screen reader announcements for loading states
- Skip links

**Assessment:** Important for enterprise/government clients. Consider for v2.

---

## Perspectives Summary

### Sati (Fresh Eyes)
*This is production-grade, not minimal. That's both strength and weakness.*

Key insight: The template is sophisticated but intimidating. New developers will struggle with the 300-line auth store.

### Spoon (Reframing)
*We're applying application standards to a template.*

Key insight: Many "issues" (no tests, no CI/CD, localStorage) are appropriate for a template's role. The real question is: what IS this template's role?

### Oracle (Unseen Paths)
*The template is caught between being a platform and a snapshot.*

Key insight: Without versioning, update strategy, and governance, the template becomes "useful once, then forgotten." The choice between platform vs snapshot hasn't been made.

---

## Prioritized Action List

### Phase 1: Unblock Developers (4-6 hours)
1. ✅ Create `.env.example` with VEOCI_API_URL
2. ✅ Add environment validation in rsbuild.config.ts
3. ✅ Remove duplicate .eslintrc.cjs
4. ✅ Fix package.json name
5. ✅ Add README environment setup section
6. ✅ Remove unused dotenv dependency

### Phase 2: Improve Quality (6-8 hours)
7. ⬜ Add Vitest with example auth store test
8. ⬜ Add basic CI workflow (lint, type-check, build)
9. ⬜ Enhance /debug view
10. ⬜ Add JSDoc comments to auth.ts
11. ⬜ Document localStorage security tradeoff

### Phase 3: Polish (4-6 hours)
12. ⬜ Add MSW mock API mode
13. ⬜ Add npm run setup script
14. ⬜ Add troubleshooting guide
15. ⬜ Add .vscode/extensions.json

### Deferred
- Package ecosystem extraction
- Template versioning
- Multi-template family
- Login state machine refactor
- Full accessibility audit

---

## Decision Points for kautau

1. **Template Identity:** Is this meant to be minimal (just enough to start) or comprehensive (production-ready foundation)?
   - Current: Trying to be both
   - Recommendation: Explicitly define scope in README

2. **Security Posture:** Should the template ship with "secure by default" (httpOnly cookies) or "simple by default" (localStorage)?
   - Depends on: Whether Veoci API supports httpOnly cookies
   - If yes: Consider making cookies the default
   - If no: Document the tradeoff clearly

3. **Maintenance Model:** Will this template be actively maintained with versions and upgrades, or is it a one-time starting point?
   - If maintained: Add versioning, CHANGELOG, governance
   - If one-time: Accept divergence, focus on initial clarity

4. **Testing Strategy:** Should the template include example tests, or leave testing to individual projects?
   - Recommendation: Include infrastructure + 1-2 example tests showing patterns
   - Don't test placeholder code that will be deleted

---

## Construct Methodology Applied

| Phase | Identity | Output | Key Finding |
|-------|----------|--------|-------------|
| 1 | Architect | architecture.md | Well-structured layers, comprehensive auth flow |
| 2 | Morpheus | docs-recommendations.md | Missing .env.example, env setup docs |
| 3 | Persephone | ux-recommendations.md | LoginView.vue complexity, loading state gaps |
| 4 | Deus | test-recommendations.md | 0% coverage, needs Vitest setup |
| 5 | Cypher | security-findings.md | localStorage XSS, client-side JWT decode |
| 6a | Apoc | dependencies.md | Unused dotenv, outdated packages |
| 6b | Niobe | cicd-review.md | No pipelines, no deployment automation |
| 6c | Keymaker | auth-review.md | Token lifecycle comprehensive |
| 6d | Seraph | devex-review.md | Clone-to-running blocked without credentials |
| 6e | Trinity | error-handling.md | Error patterns need documentation |
| 7a | Sati | perspective-sati.md | Production-grade template, intimidating complexity |
| 7b | Spoon | perspective-spoon.md | Reframe: template standards vs app standards |
| 7c | Oracle | perspective-oracle.md | Platform vs snapshot choice unmade |

---

## Conclusion

**Ship/Iterate/Revisit:** **Iterate**

The template has solid technical foundations but genuine blockers preventing adoption. Fix Phase 1 items before sharing externally. The security considerations are context-dependent - document the tradeoffs rather than mandating changes that may not fit the deployment context.

The philosophical question (platform vs snapshot) can be deferred. For now, make it work well as a starting point.

---

*Wake up, Neo.*
