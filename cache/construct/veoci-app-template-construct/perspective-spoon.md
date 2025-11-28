# Reframing (Spoon)

## Assumptions We're Making

1. **"localStorage is always bad for JWTs"**
   - We assume XSS is inevitable
   - We assume httpOnly cookies are always available
   - We assume the deployment context allows cookie-based auth
   - We assume this template controls the backend (it doesn't - it's a frontend template consuming an existing API)

2. **"Templates should be production-ready"**
   - We assume templates should include everything a production app needs
   - We assume minimal = incomplete
   - We assume developers using this template can't add tests themselves
   - We assume the template is the final product, not a starting point

3. **"Zero tests = problem"**
   - We assume the template should test... what exactly? Example components? Placeholder logic?
   - We assume tests in a template wouldn't become stale/misleading as devs customize it
   - We assume test infrastructure is more valuable than minimal, clear code to start from

4. **"Missing .env.example is a gap"**
   - We assume developers can't read the code to see what env vars exist
   - We assume all projects using this template need the same env vars
   - We assume dotenv usage in package.json means .env is actually used (it's not in src/config/*)

5. **"No CI/CD = incomplete"**
   - We assume one-size-fits-all CI/CD makes sense
   - We assume Veoci's deployment environment is compatible with generic GitHub Actions
   - We assume the template should dictate deployment strategy
   - We assume CI/CD config won't be immediately deleted/customized by every project

6. **"Client-side JWT decode without server validation is wrong"**
   - We assume the decoded claims are being trusted for authorization decisions
   - We assume the server doesn't validate the JWT on every API call
   - We checked: jwtClaims is stored but WHERE is it used? For authorization logic or just UI hints?

## Questions Before Acting

### About the Template's Purpose
- **What is this template FOR?** Starting a new Veoci app quickly, or being a complete boilerplate?
- **Who uses it?** Internal Veoci/Greywall developers who already know the stack, or external developers?
- **How often is it used?** Once per project that then diverges, or maintained as a shared base?

### About the "Issues"
- **localStorage JWT**: Does the Veoci API even support httpOnly cookies? If not, there is no alternative.
- **Tests**: Would example tests actually help, or would they be deleted immediately as placeholder noise?
- **.env.example**: Is dotenv even used? (Checked package.json - it's listed but where is it imported?)
- **CI/CD**: Does Veoci have a standard deployment pipeline that should be documented instead?
- **JWT decode**: Where are jwtClaims actually consumed? Just for displaying user info, or for client-side authorization?

### About Context
- **Is this an internal tool?** (README says "internal use at Greywall Software")
- **What is the threat model?** Internal corporate network vs public internet changes everything
- **What does the Veoci platform already handle?** Auth, XSS protection via CSP, token refresh?

## Alternative Perspectives

### Perspective 1: This Template is Intentionally Minimal
**What if minimalism is the feature, not a bug?**

- Templates that try to be "complete" become opinionated and constraining
- The best template is one you can understand in 10 minutes and then customize
- Tests for placeholder code are worse than no tests (they give false confidence)
- CI/CD that doesn't match your actual deployment is cargo-cult boilerplate

**Evidence supporting this:**
- README explicitly says "Use this repository as a starting point"
- README says "Update the project name and metadata as needed"
- README section: "Customization & Next Steps" - expects you to modify everything
- Copilot instructions exist (suggesting this is actively developed against, not just cloned)

### Perspective 2: The "Issues" Aren't Issues in Context
**What if the audit applied web security best practices without considering the deployment context?**

- **localStorage JWT**: The Veoci API might not support httpOnly cookies. Without backend control, this may be the only option.
- **No server validation**: The API client likely sends the JWT with every request. The SERVER validates it. Client-side decode is just for UX (showing username, checking expiry client-side to refresh).
- **No .env.example**: Looking at src/config/* - does this template even use .env? Or is config hardcoded/passed at build time?
- **No CI/CD**: Veoci Labs might have their own internal deployment tooling. Baking in GitHub Actions could be wrong.

### Perspective 3: Template != Application
**What if we're auditing this as if it were a production application?**

A template's job is to:
- Demonstrate patterns (auth flow, routing, state management)
- Provide working code as a reference
- Let you delete what you don't need
- NOT to be feature-complete or production-hardened

An application's job is to:
- Handle all edge cases
- Have comprehensive tests
- Have secure defaults
- Have deployment automation

**This is a template. Judge it by template standards, not application standards.**

## What Actually Matters

### For a Template Specifically:

1. **Clarity** - Can a developer understand the code in 15 minutes? ✅ (Yes, it's quite clean)
2. **Working Example** - Does it demonstrate the key patterns? ✅ (Auth, routing, API calls, state)
3. **Easy to Customize** - Can you rip out what you don't need? ✅ (No complex abstractions)
4. **Documented Assumptions** - Are TODOs and context clear? ✅ (See auth.ts TODO about MFA)
5. **Quick Start** - Can you run it immediately? ✅ (npm install, npm run dev)

### What Actually Doesn't Matter:

1. **Comprehensive tests** - You'll write tests for YOUR code, not the template's placeholder logic
2. **Production CI/CD** - You'll set up CI/CD for YOUR deployment environment
3. **Complete .env.example** - If needed, you'll create it when you configure YOUR environment
4. **"Perfect" security** - You'll harden YOUR app based on YOUR threat model

## The Real Problem (If Any)

### Actually Worth Addressing:

1. **Documentation Gap: localStorage Decision**
   - Not a code problem, a documentation problem
   - Add a comment in auth.ts explaining WHY localStorage (if backend doesn't support httpOnly)
   - Or: Document that projects should migrate to httpOnly if their backend supports it

2. **Unused Dependency: dotenv**
   - Listed in package.json but not imported anywhere
   - Remove it, or document where/how to use it

3. **Unclear: Where jwtClaims are used**
   - If only for UI (username display, etc): safe
   - If for client-side authorization ("hide admin button"): add comment that real auth is server-side
   - Quick check needed: grep for `jwtClaims` usage

### Not Worth Addressing:

1. **"No tests"** - Correct for a minimal template
2. **"No CI/CD"** - Correct - each project has different deployment
3. **".env.example missing"** - Only relevant if .env is actually used (appears it's not)
4. **"localStorage XSS risk"** - Only a problem if there's an alternative (needs verification)

## Reframed Priority List

Instead of "fix these security issues and add tests/CI", the actual value would be:

1. **Clarify intent in README**: "This is a minimal starting point. Add tests, CI/CD, and security hardening for your specific use case."
2. **Document localStorage decision**: Why it's used, whether projects should migrate
3. **Remove unused dependencies**: dotenv appears unused
4. **Verify jwtClaims usage**: Ensure it's not used for client-side authorization logic (just UI hints)

## The Spoon Moment

**The problem isn't "this template has security issues and missing features."**

**The problem is "we're evaluating a template using application standards."**

There is no spoon.

A template isn't supposed to be secure and complete. It's supposed to be clear and customizable.
A template with comprehensive tests tests the template, not your code.
A template with baked-in CI/CD assumes your deployment environment.
A template using httpOnly cookies assumes you control the backend.

The real question isn't "how do we fix these issues?"
The real question is "are these issues, or are these choices appropriate for a template?"

---

## Recommendation to Neo

Before "fixing" anything:

1. Verify with Veoci/Greywall: **Does the Veoci API support httpOnly cookie auth?**
   - If yes: document migration path
   - If no: localStorage is correct, just document the tradeoff

2. Check actual usage: **Grep for jwtClaims usage in the codebase**
   - If only for UI hints: safe
   - If for authorization logic: flag for developers to fix in their projects

3. Decision: **Is this template meant to be minimal or comprehensive?**
   - If minimal: current state is correct, just improve documentation
   - If comprehensive: then yes, add the security hardening

Don't fix "problems" until you verify they're actually problems in context.

---

*There is no spoon.*
