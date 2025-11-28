# Add Vitest testing infrastructure with example test

**Type:** `issue`
**Labels:** `identity:deus`, `enhancement`, `reliability`

## Context

From Construct review of `veoci-app-template-construct`. Deus flagged 0% test coverage; Spoon reframed that testing placeholder code is cargo cult, but test infrastructure is valuable.

**Sources:**
- `~/.matrix/cache/construct/veoci-app-template-construct/test-recommendations.md`
- `~/.matrix/cache/construct/veoci-app-template-construct/perspective-spoon.md`

## Problem

The template has zero test infrastructure:
- No test framework installed
- No test scripts in package.json
- No example of how to test Veoci integrations
- Developers don't know how to mock VeociJS SDK

This doesn't mean we need comprehensive tests for placeholder code. But the template should demonstrate HOW to test.

## Solution

Install Vitest with Vue/Pinia support and add ONE example test showing mocking patterns.

## Implementation Steps

1. Install dependencies:
   ```bash
   npm install -D vitest @vue/test-utils @pinia/testing happy-dom
   ```

2. Create `vitest.config.ts`:
   ```typescript
   import { defineConfig } from 'vitest/config'
   import vue from '@vitejs/plugin-vue'

   export default defineConfig({
     plugins: [vue()],
     test: {
       globals: true,
       environment: 'happy-dom',
       setupFiles: ['./tests/setup.ts'],
     },
     resolve: {
       alias: {
         '@': '/src',
       },
     },
   })
   ```

3. Create `tests/setup.ts`:
   ```typescript
   import { config } from '@vue/test-utils'
   import { createTestingPinia } from '@pinia/testing'

   // Global test setup
   config.global.plugins = [createTestingPinia()]
   ```

4. Create example test `tests/unit/stores/auth.spec.ts`:
   ```typescript
   import { describe, it, expect, vi, beforeEach } from 'vitest'
   import { setActivePinia, createPinia } from 'pinia'
   import { useAuthStore } from '@/store/auth'

   // Mock VeociJS SDK
   vi.mock('@GreywallSoftware/veoci-js', () => ({
     VeociSDK: vi.fn().mockImplementation(() => ({
       auth: {
         login: vi.fn().mockResolvedValue({ authToken: 'mock-token' }),
         logout: vi.fn().mockResolvedValue(undefined),
       },
     })),
   }))

   describe('Auth Store', () => {
     beforeEach(() => {
       setActivePinia(createPinia())
       localStorage.clear()
     })

     it('should initialize as not authenticated', () => {
       const store = useAuthStore()
       expect(store.isAuthenticated).toBe(false)
     })

     it('should store token in localStorage on login', async () => {
       const store = useAuthStore()
       // This test demonstrates the pattern - actual implementation
       // depends on store structure
       expect(localStorage.getItem('authToken')).toBeNull()
     })
   })
   ```

5. Add scripts to `package.json`:
   ```json
   {
     "scripts": {
       "test": "vitest",
       "test:run": "vitest run",
       "test:coverage": "vitest run --coverage"
     }
   }
   ```

6. Add to README:
   ```markdown
   ## Testing

   ```bash
   npm run test        # Watch mode
   npm run test:run    # Single run
   npm run test:coverage  # With coverage
   ```

   See `tests/unit/stores/auth.spec.ts` for example of mocking VeociJS SDK.
   ```

## Acceptance Criteria

- [ ] Vitest installed and configured
- [ ] `npm run test` works
- [ ] Example test demonstrates VeociJS mocking pattern
- [ ] README documents testing approach
- [ ] Coverage report available via `npm run test:coverage`

## Handoff

Deus implements and verifies test infrastructure works correctly.
