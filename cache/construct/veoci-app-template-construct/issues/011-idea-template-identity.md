# Clarify template identity: minimal vs comprehensive

**Type:** `idea`
**Labels:** `identity:oracle`, `idea`, `strategy`
**Category:** Ideas

## The Question

From Construct review of `veoci-app-template-construct`. Oracle and Spoon raised fundamental questions about template purpose.

**Sources:**
- `~/.matrix/cache/construct/veoci-app-template-construct/perspective-oracle.md`
- `~/.matrix/cache/construct/veoci-app-template-construct/perspective-spoon.md`

## Current State

The template is caught between two identities:

**Minimal Template:**
- Just enough to start
- Expects you to add tests, CI/CD, security hardening
- Prioritizes clarity over completeness

**Comprehensive Boilerplate:**
- Production-ready foundation
- 300-line auth store with MFA flows
- Complex proxy configuration
- Anticipates enterprise needs

Neither is wrong, but trying to be both creates confusion. The audit applied application standards to a template, finding "issues" that may be intentional minimalism.

## The Decision

Should this template be explicitly positioned as:

### Option A: Minimal Starter
*"Clone, understand in 15 minutes, customize everything"*

- Remove complex MFA flows (mark as TODO or separate plugin)
- Simplify auth store to essential login/logout/refresh
- No tests (you'll write tests for YOUR code)
- No CI/CD (you'll set up YOUR deployment)
- Document the intentional gaps

### Option B: Complete Foundation
*"Production-ready, add your features on top"*

- Add comprehensive tests
- Add CI/CD workflows
- Add security hardening (httpOnly cookies)
- Add accessibility patterns
- Add error boundaries

### Option C: Multi-Tier Templates
*"Choose your complexity budget"*

```
veoci-app-minimal    # Routing + API client only
veoci-app-standard   # Current implementation
veoci-app-enterprise # Adds tests, Storybook, a11y
```

## Questions to Discuss

1. **Who is the primary user?**
   - Internal Greywall developers (know the stack)
   - External developers (need more guidance)
   - Both (different templates?)

2. **What's the maintenance commitment?**
   - Actively maintained with versions and upgrades
   - One-time starting point, then projects diverge

3. **What's "in scope" for a template?**
   - Auth? (yes)
   - Testing? (maybe)
   - CI/CD? (debatable)
   - Security hardening? (debatable)

4. **How do we communicate this?**
   - README clearly states scope
   - "This template is for X, not for Y"

## Proposed README Addition

Whatever the decision, make it explicit:

```markdown
## What This Template Is

This is a [minimal/comprehensive] starting point for Veoci applications.

**Included:**
- Vue 3 + TypeScript + Vuetify 3 setup
- Authentication flow (login, logout, token refresh)
- Routing with auth guards
- Dev proxy configuration

**Not Included (You Add):**
- Tests (we recommend Vitest)
- CI/CD (project-specific)
- Production security hardening
- [Other items...]

**This Template Is For:**
- Teams building Veoci integrations
- Developers comfortable with Vue 3 Composition API
- Projects that need [X]

**This Template Is NOT For:**
- Beginners to Vue (try [X] instead)
- Teams needing SSR/SSG
- [Other...]
```

---

*From Oracle's unseen paths and Spoon's reframing*
