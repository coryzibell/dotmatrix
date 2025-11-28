# Remove unused dotenv dependency

**Type:** `issue`
**Labels:** `identity:smith`, `blocker`, `dx`

## Context

From Construct review of `veoci-app-template-construct`. Apoc identified during dependency analysis.

**Source:** `~/.matrix/cache/construct/veoci-app-template-construct/dependencies.md`

## Problem

`dotenv` (v16.5.0) is listed in `package.json` dependencies but:
- Never imported anywhere in the codebase
- Is a **Node.js** package that has no effect in browser code
- Adds ~40KB to bundle for zero benefit
- Misleads developers into thinking `.env` files work client-side at runtime

Rsbuild handles environment variables at **build time** via `import.meta.env`, not at runtime via `dotenv`.

## Solution

Remove the unused dependency.

## Implementation Steps

1. Remove dotenv:
   ```bash
   npm uninstall dotenv
   ```

2. Verify no imports exist:
   ```bash
   grep -r "dotenv" src/
   grep -r "require.*dotenv" .
   ```

3. Document correct env var usage in README:
   ```markdown
   ## Environment Variables

   Environment variables are injected at **build time** by Rsbuild.

   Access them via:
   ```typescript
   const apiUrl = import.meta.env.VEOCI_API_URL
   ```

   Variables must be prefixed with `VITE_` to be exposed to client code,
   or configured in `rsbuild.config.ts`.
   ```

## Acceptance Criteria

- [ ] `dotenv` removed from package.json
- [ ] No import errors after removal
- [ ] README explains correct env var usage
- [ ] Bundle size reduced

## Handoff

Quick fix - Smith handles directly. Apoc verifies bundle size improvement.
