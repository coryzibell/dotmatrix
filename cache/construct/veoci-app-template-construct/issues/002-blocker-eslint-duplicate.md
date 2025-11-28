# Remove duplicate ESLint configuration

**Type:** `issue`
**Labels:** `identity:smith`, `blocker`, `dx`

## Context

From Construct review of `veoci-app-template-construct`. Sati identified during fresh-eyes review.

**Source:** `~/.matrix/cache/construct/veoci-app-template-construct/perspective-sati.md`

## Problem

Both `.eslintrc.cjs` AND `eslint.config.js` exist in the repository. ESLint 9 uses the flat config format (`eslint.config.js`), making the legacy `.eslintrc.cjs` redundant and confusing.

Having both:
- Confuses developers about which config is active
- Suggests incomplete migration to ESLint 9
- May cause inconsistent linting if configs differ

## Solution

Remove `.eslintrc.cjs` and keep only `eslint.config.js` (flat config).

## Implementation Steps

1. Verify `eslint.config.js` has all necessary rules from `.eslintrc.cjs`
2. Run `npm run lint` to confirm flat config works
3. Delete `.eslintrc.cjs`
4. Commit with message: `chore: remove legacy eslint config, keep flat config only`

## Acceptance Criteria

- [ ] Only `eslint.config.js` exists
- [ ] `npm run lint` works correctly
- [ ] No lint errors in codebase

## Handoff

Quick fix - Smith handles directly.
