# Add .env.example with required environment variables

**Type:** `issue`
**Labels:** `identity:smith`, `blocker`, `dx`

## Context

From Construct review of `veoci-app-template-construct`. Multiple identities (Seraph, Morpheus, Persephone) flagged this as the #1 blocker for developer onboarding.

**Source:** `~/.matrix/cache/construct/veoci-app-template-construct/devex-review.md`

## Problem

The template requires `VEOCI_API_URL` for the dev proxy to function, but:
- No `.env.example` file exists
- No documentation of required variables
- Dev server starts successfully even with missing config
- First API call fails silently with confusing CORS/network errors
- Developers waste 30-60 minutes debugging before discovering the issue

Current developer experience:
```bash
npm install && npm run dev  # Opens browser, looks fine
# Enter credentials
# "Network Error" - no indication VEOCI_API_URL is missing
```

## Solution

1. Create `.env.example` documenting required variables
2. Add environment validation to `rsbuild.config.ts` that fails fast with clear instructions

## Implementation Steps

1. Create `.env.example` in project root:
   ```env
   # Veoci API Configuration
   # Copy this file to .env and update with your instance URL

   # Required: Your Veoci instance base URL
   VEOCI_API_URL=https://your-instance.veoci.com

   # Optional: Override dev server port (default: 3000)
   # PORT=3000
   ```

2. Add validation to top of `rsbuild.config.ts`:
   ```typescript
   // Validate required environment variables
   if (!process.env.VEOCI_API_URL) {
     console.error('')
     console.error('❌ Missing required environment variable: VEOCI_API_URL')
     console.error('')
     console.error('Quick fix:')
     console.error('  cp .env.example .env')
     console.error('  # Edit .env and set VEOCI_API_URL')
     console.error('')
     process.exit(1)
   }
   ```

3. Update README.md with Configuration section

## Acceptance Criteria

- [ ] `.env.example` exists with documented variables
- [ ] `npm run dev` fails immediately with helpful message if VEOCI_API_URL missing
- [ ] README includes environment setup instructions
- [ ] New developer can go from clone to running in <5 minutes (with credentials)

## Handoff

After Smith implements:
1. Morpheus reviews README changes
2. Seraph verifies first-run experience
