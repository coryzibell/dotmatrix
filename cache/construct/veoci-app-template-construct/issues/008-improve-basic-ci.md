# Add basic CI workflow for PR validation

**Type:** `issue`
**Labels:** `identity:niobe`, `enhancement`, `infrastructure`

## Context

From Construct review of `veoci-app-template-construct`. Niobe identified zero CI/CD infrastructure.

**Sources:**
- `~/.matrix/cache/construct/veoci-app-template-construct/cicd-review.md`
- `~/.matrix/cache/construct/veoci-app-template-construct/perspective-spoon.md`

## Problem

No GitHub Actions workflows exist. PRs can merge with:
- Lint errors
- Type errors
- Broken builds

Spoon correctly notes that deployment automation should be project-specific. But basic quality gates (lint, type-check, build) are universal.

## Solution

Add minimal CI workflow for PR validation. Leave deployment to individual projects.

## Implementation Steps

1. Create `.github/workflows/ci.yml`:
   ```yaml
   name: CI

   on:
     push:
       branches: [main]
     pull_request:
       branches: [main]

   jobs:
     validate:
       runs-on: ubuntu-latest

       steps:
         - uses: actions/checkout@v4

         - name: Setup Node.js
           uses: actions/setup-node@v4
           with:
             node-version: '20'
             cache: 'npm'

         - name: Install dependencies
           run: npm ci

         - name: Lint
           run: npm run lint

         - name: Type check
           run: npm run typecheck

         - name: Build
           run: npm run build
   ```

2. Add typecheck script to `package.json` (if missing):
   ```json
   {
     "scripts": {
       "typecheck": "vue-tsc --noEmit"
     }
   }
   ```

3. Install vue-tsc if needed:
   ```bash
   npm install -D vue-tsc
   ```

4. Fix typo in `.github/copilot-instrucitons.md` → `copilot-instructions.md`

## Acceptance Criteria

- [ ] CI workflow runs on PRs
- [ ] Lint step catches ESLint errors
- [ ] Type check step catches TypeScript errors
- [ ] Build step verifies production build works
- [ ] Copilot instructions filename fixed

## Handoff

Niobe implements. After tests are added (issue #007), extend CI to include test step.
