# Add mock API mode for development without Veoci credentials

**Type:** `idea`
**Labels:** `identity:sati`, `idea`, `dx`
**Category:** Ideas

## The Opportunity

From Construct review of `veoci-app-template-construct`. Seraph and Sati noted developers can't try the template without Veoci credentials.

**Source:** `~/.matrix/cache/construct/veoci-app-template-construct/devex-review.md`

## Current State

A developer clones the template, runs `npm run dev`, sees the login page, and... is stuck. Without Veoci credentials, they can't:
- Evaluate the template
- Demo to stakeholders
- Develop UI components in isolation
- Run automated tests

## The Vision

Add MSW (Mock Service Worker) for a `npm run dev:mock` mode:

```bash
npm run dev:mock
# Browser console: "Mock API enabled - use demo@veoci.com / demo"
```

Login with demo credentials, see the full app flow, develop without backend dependency.

## Possible Implementation

1. Install MSW:
   ```bash
   npm install -D msw
   ```

2. Create mock handlers:
   ```typescript
   // src/mocks/handlers.ts
   import { http, HttpResponse } from 'msw'

   export const handlers = [
     http.post('/auth/login', async ({ request }) => {
       const { username, password } = await request.json()
       if (username === 'demo@veoci.com' && password === 'demo') {
         return HttpResponse.json({
           authToken: 'mock-jwt-token',
           user: { id: 1, email: 'demo@veoci.com', name: 'Demo User' }
         })
       }
       return HttpResponse.json({ error: 'Invalid credentials' }, { status: 401 })
     }),

     http.get('/api/v1/user/current', () => {
       return HttpResponse.json({
         id: 1, email: 'demo@veoci.com', name: 'Demo User'
       })
     }),
   ]
   ```

3. Enable in dev mode:
   ```typescript
   // src/index.ts
   if (import.meta.env.DEV && import.meta.env.VITE_USE_MOCK_API === 'true') {
     const { worker } = await import('./mocks/browser')
     await worker.start()
     console.log('Mock API enabled - use demo@veoci.com / demo')
   }
   ```

4. Add script:
   ```json
   {
     "scripts": {
       "dev:mock": "VITE_USE_MOCK_API=true rsbuild dev --open"
     }
   }
   ```

## Questions to Discuss

1. **Scope:** How much of the Veoci API should be mocked?
   - Minimal: Just login/logout
   - Standard: Auth + basic user data
   - Full: All API endpoints used by template

2. **MFA:** Should mock mode simulate MFA flow?

3. **Realism:** Should mock data be realistic or obviously fake?

4. **Tests:** Should the same mocks be used for automated tests?

## Benefits

- Developers can try template without credentials
- UI development decoupled from backend
- Demos work offline
- Tests can use consistent mock data
- Faster feedback loop

## Concerns

- Maintenance burden keeping mocks in sync with real API
- Risk of mocks diverging from production behavior
- Additional complexity for a "simple" template

---

*From Sati's fresh eyes and Seraph's DevEx review*
