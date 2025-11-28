# Test Coverage Analysis: Veoci App Template Construct

**Analysis Date:** 2025-11-27
**Analyzer:** Deus Ex Machina
**Repository:** veoci-app-template-construct
**Framework:** Vue 3 + Vuetify 3 + Pinia + Rsbuild

---

## Executive Summary

**Current Test Coverage:** 0%
**Test Frameworks Installed:** NONE
**Test Script in package.json:** MISSING
**Risk Level:** CRITICAL

The application has ZERO test infrastructure. Authentication flows, route guards, and state management are completely untested. Production deployment without tests is unacceptable.

---

## 1. Current Test Coverage Assessment

### Test Infrastructure Status

```
MISSING:
  ❌ Test framework (vitest, jest, cypress, playwright)
  ❌ Test utilities (@vue/test-utils, @pinia/testing)
  ❌ Test configuration files (vitest.config.ts, cypress.config.ts)
  ❌ Test scripts in package.json
  ❌ CI/CD test pipeline
  ❌ Coverage reporting (istanbul, c8)
  ❌ Mock utilities (msw, vitest mocks)
  ❌ Test fixtures and factories
  ❌ E2E test infrastructure
  ❌ Visual regression tests
```

### Coverage by Layer

| Layer | Files | Coverage | Critical Paths Untested |
|-------|-------|----------|-------------------------|
| **Authentication** | auth.ts (9.8KB) | 0% | login, MFA, logout, token refresh, session management |
| **Routing** | router/index.ts | 0% | Route guards, auth redirect logic |
| **State Management** | user.ts, auth.ts | 0% | Store actions, getters, state mutations |
| **Services** | api-client.ts, api.ts, apiHelper.ts | 0% | VeociJS initialization, API calls, error handling |
| **Components** | LoginView.vue + 7 child components | 0% | Login flow, MFA flow, password reset |
| **Views** | HomeView.vue, DebugView.vue | 0% | Protected route rendering, data loading |
| **Types** | api.types.ts | N/A | Type safety (compile-time only) |

**Total Critical Functions Untested:** ~50+

---

## 2. Critical Paths Requiring Tests

### Priority 1: Authentication Flow (HIGHEST RISK)

**File:** `src/store/auth.ts` (9.8KB)

#### Critical Functions

```typescript
// UNTESTED CRITICAL PATHS
✗ login(username: string, password: string)
  - API call to /auth/login
  - MFA detection logic
  - Token storage in localStorage
  - VeociJS SDK initialization
  - Error handling (invalid credentials, network failure)

✗ loginWithMfaToken(mfaToken: string, rememberMe: boolean)
  - MFA verification API call
  - Token storage on success
  - MFA failure handling

✗ logout()
  - localStorage token removal
  - Auth store state reset
  - Router redirect to /login
  - VeociJS SDK cleanup

✗ refreshSession()
  - Token refresh API call
  - New token persistence
  - SDK token update
  - Expiry handling

✗ fetchLoginMetadata(email: string)
  - Metadata API call (SSO, MFA config)
  - Response parsing
  - Error handling

✗ isAuthenticated (computed getter)
  - Token presence validation
  - Token expiry check (if implemented)
```

#### Test Coverage Needed

```typescript
describe('auth store', () => {
  describe('login', () => {
    it('should store authToken on successful login without MFA')
    it('should set mfaRequired=true when MFA is required')
    it('should not store token when MFA is pending')
    it('should throw error on invalid credentials')
    it('should handle network errors gracefully')
    it('should initialize VeociJS SDK with token on success')
  })

  describe('loginWithMfaToken', () => {
    it('should store authToken on valid MFA code')
    it('should respect rememberMe flag for token persistence')
    it('should throw error on invalid MFA code')
    it('should handle MFA timeout')
  })

  describe('logout', () => {
    it('should remove authToken from localStorage')
    it('should reset auth store state')
    it('should redirect to /login')
    it('should clear VeociJS SDK authentication')
  })

  describe('refreshSession', () => {
    it('should update authToken on successful refresh')
    it('should persist new token to localStorage')
    it('should update VeociJS SDK with new token')
    it('should logout user if refresh fails')
  })

  describe('isAuthenticated', () => {
    it('should return true when valid token exists')
    it('should return false when no token exists')
    it('should return false when token is expired') // if expiry check implemented
  })
})
```

**Estimated Tests:** 20+ test cases

---

### Priority 2: Route Guards (HIGH RISK)

**File:** `src/router/index.ts`

#### Critical Logic

```typescript
// UNTESTED ROUTE GUARD LOGIC
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  ✗ if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      next('/login')  // Unauthenticated access to protected route
    }
  ✗ else if (to.path === '/login' && authStore.isAuthenticated) {
      next('/home')  // Authenticated user accessing login
    }
  ✗ else {
      next()  // Normal navigation
    }
})
```

#### Test Coverage Needed

```typescript
describe('router guards', () => {
  it('should redirect unauthenticated users to /login for protected routes')
  it('should allow authenticated users to access protected routes')
  it('should redirect authenticated users from /login to /home')
  it('should allow unauthenticated users to access /login')
  it('should allow navigation to public routes without auth')
  it('should preserve intended route in query params for post-login redirect') // if implemented
})
```

**Estimated Tests:** 6+ test cases

---

### Priority 3: Login Flow Components (MEDIUM-HIGH RISK)

**Files:** `src/views/login/*.vue` (7 components)

#### Components

```
LoginView.vue             → Multi-step orchestrator
LoginUsernameStep.vue     → Email input, metadata fetch
LoginPasswordStep.vue     → Password input, login trigger
LoginMfaStep.vue          → MFA code entry
MfaStep.vue               → MFA verification
LoginForgotPasswordStep.vue → Password reset flow
ChangePasswordStep.vue    → Password change form
```

#### Test Coverage Needed

```typescript
// LoginView.vue
describe('LoginView', () => {
  it('should display LoginUsernameStep on initial load')
  it('should transition to LoginPasswordStep after username entry')
  it('should transition to LoginMfaStep when MFA is required')
  it('should redirect to /home on successful login')
  it('should display error message on login failure')
})

// LoginPasswordStep.vue
describe('LoginPasswordStep', () => {
  it('should call authStore.login() on form submit')
  it('should disable submit button during login attempt')
  it('should display validation errors for empty password')
  it('should display error message from API')
})

// LoginMfaStep.vue
describe('LoginMfaStep', () => {
  it('should call authStore.loginWithMfaToken() on code submit')
  it('should validate MFA code format')
  it('should display error on invalid code')
  it('should show loading state during verification')
})
```

**Estimated Tests:** 30+ test cases across 7 components

---

### Priority 4: VeociJS Service Layer (MEDIUM RISK)

**File:** `src/services/api-client.ts`

#### Critical Functions

```typescript
✗ VeociJS SDK initialization
✗ Module loading (Login, Object, Form, AuthdUser, WebLogin)
✗ Token injection into SDK
✗ Error handling for SDK failures
```

#### Test Coverage Needed

```typescript
describe('api-client', () => {
  it('should initialize VeociJS with correct configuration')
  it('should load all required modules')
  it('should inject authToken into SDK after login')
  it('should handle module loading failures')
  it('should export SDK instance for stores')
})
```

**Estimated Tests:** 8+ test cases

---

### Priority 5: User Store (MEDIUM RISK)

**File:** `src/store/user.ts`

#### Critical Functions

```typescript
✗ fetchCurrentUser()
✗ updateProfile(data)
✗ userName getter
✗ userPermissions getter
```

#### Test Coverage Needed

```typescript
describe('user store', () => {
  it('should fetch current user data on fetchCurrentUser()')
  it('should not fetch user when unauthenticated')
  it('should update profile data on updateProfile()')
  it('should compute userName from currentUser state')
  it('should compute userPermissions from currentUser state')
  it('should clear user data on logout') // if implemented
})
```

**Estimated Tests:** 10+ test cases

---

## 3. Recommended Test Framework

### Selected Framework: **Vitest**

#### Justification

```
✅ Native Vite/Rsbuild integration (zero config overhead)
✅ Fast test execution (uses Vite's transformation pipeline)
✅ Jest-compatible API (easy migration path)
✅ Native ESM support (aligns with Vue 3 ecosystem)
✅ Built-in TypeScript support
✅ Component testing via @vue/test-utils
✅ Coverage reporting with c8 (built-in)
✅ Watch mode for TDD workflow
✅ Pinia testing utilities available (@pinia/testing)
```

#### Alternative Considered: Jest

```
❌ Requires additional Babel configuration
❌ Slower than Vitest for Vite/Rsbuild projects
❌ More complex ESM setup
✅ Larger ecosystem (but Vitest is Jest-compatible)
```

#### E2E Framework: **Playwright**

```
✅ Multi-browser support (Chromium, Firefox, WebKit)
✅ Better debugging than Cypress
✅ Network interception built-in
✅ Parallel test execution
✅ Official Vue.js recommendation
✅ TypeScript-first design
```

---

## 4. Recommended Test Stack

### Installation Commands

```bash
# Core testing dependencies
npm install -D vitest @vitest/ui @vitest/coverage-v8

# Vue testing utilities
npm install -D @vue/test-utils @pinia/testing

# Mocking and fixtures
npm install -D msw happy-dom jsdom

# E2E testing
npm install -D @playwright/test

# Optional: visual regression
npm install -D @playwright/test playwright-snapshot
```

### Configuration Files

#### `vitest.config.ts`

```typescript
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true }),
  ],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.d.ts',
        '**/*.config.*',
        'tests/',
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 75,
        statements: 80,
      },
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
```

#### `tests/setup.ts`

```typescript
import { config } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// Global Vuetify setup for tests
const vuetify = createVuetify({
  components,
  directives,
})

config.global.plugins = [vuetify]

// Mock localStorage
global.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
} as any

// Mock VeociJS SDK
vi.mock('@GreywallSoftware/veoci-js', () => ({
  VeociClient: vi.fn(() => ({
    loadModule: vi.fn(),
    Login: {
      login: vi.fn(),
      loginWithMfaToken: vi.fn(),
      logout: vi.fn(),
    },
  })),
}))
```

#### `playwright.config.ts`

```typescript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

#### Updated `package.json` Scripts

```json
{
  "scripts": {
    "dev": "rsbuild dev",
    "build": "rsbuild build",
    "preview": "rsbuild preview",
    "lint": "eslint src/",
    "format": "prettier --write src/",

    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:all": "npm run test:coverage && npm run test:e2e"
  }
}
```

---

## 5. Priority Test Cases to Implement First

### Phase 1: Auth Store Unit Tests (DAY 1)

**File:** `tests/unit/store/auth.spec.ts`

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/store/auth'

describe('auth store - critical paths', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  describe('login flow', () => {
    it('should store token on successful login without MFA', async () => {
      const store = useAuthStore()
      const mockToken = 'mock-auth-token-12345'

      // Mock VeociJS Login.login() response
      vi.mocked(store.veociClient.Login.login).mockResolvedValue({
        authToken: mockToken,
        mfaRequired: false,
      })

      await store.login('user@example.com', 'password123')

      expect(store.authToken).toBe(mockToken)
      expect(store.isAuthenticated).toBe(true)
      expect(localStorage.setItem).toHaveBeenCalledWith('authToken', mockToken)
    })

    it('should set mfaRequired=true when MFA is required', async () => {
      const store = useAuthStore()

      vi.mocked(store.veociClient.Login.login).mockResolvedValue({
        mfaToken: 'mfa-token-67890',
        mfaRequired: true,
      })

      await store.login('user@example.com', 'password123')

      expect(store.mfaRequired).toBe(true)
      expect(store.authToken).toBeNull()
      expect(store.isAuthenticated).toBe(false)
    })

    it('should throw error on invalid credentials', async () => {
      const store = useAuthStore()

      vi.mocked(store.veociClient.Login.login).mockRejectedValue(
        new Error('Invalid credentials')
      )

      await expect(
        store.login('user@example.com', 'wrongpassword')
      ).rejects.toThrow('Invalid credentials')

      expect(store.isAuthenticated).toBe(false)
    })
  })

  describe('logout', () => {
    it('should clear token and reset state', async () => {
      const store = useAuthStore()
      store.authToken = 'existing-token'

      await store.logout()

      expect(store.authToken).toBeNull()
      expect(localStorage.removeItem).toHaveBeenCalledWith('authToken')
      expect(store.isAuthenticated).toBe(false)
    })
  })
})
```

**Estimated Time:** 4-6 hours

---

### Phase 2: Route Guard Integration Tests (DAY 1-2)

**File:** `tests/integration/router/guards.spec.ts`

```typescript
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/store/auth'
import routes from '@/router/index'

describe('router guards', () => {
  let router
  let authStore

  beforeEach(() => {
    setActivePinia(createPinia())
    authStore = useAuthStore()
    router = createRouter({
      history: createMemoryHistory(),
      routes,
    })
  })

  it('should redirect unauthenticated users to /login', async () => {
    authStore.authToken = null

    await router.push('/home')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('should allow authenticated users to access /home', async () => {
    authStore.authToken = 'valid-token'

    await router.push('/home')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/home')
  })

  it('should redirect authenticated users from /login to /home', async () => {
    authStore.authToken = 'valid-token'

    await router.push('/login')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/home')
  })
})
```

**Estimated Time:** 3-4 hours

---

### Phase 3: Login Component Tests (DAY 2-3)

**File:** `tests/unit/views/login/LoginPasswordStep.spec.ts`

```typescript
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import LoginPasswordStep from '@/views/login/LoginPasswordStep.vue'
import { useAuthStore } from '@/store/auth'

describe('LoginPasswordStep', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should call authStore.login() on form submit', async () => {
    const wrapper = mount(LoginPasswordStep, {
      props: {
        username: 'user@example.com',
      },
    })

    const authStore = useAuthStore()
    const loginSpy = vi.spyOn(authStore, 'login')

    await wrapper.find('input[type="password"]').setValue('password123')
    await wrapper.find('form').trigger('submit')

    expect(loginSpy).toHaveBeenCalledWith('user@example.com', 'password123')
  })

  it('should disable submit button during login', async () => {
    const wrapper = mount(LoginPasswordStep, {
      props: {
        username: 'user@example.com',
      },
    })

    const authStore = useAuthStore()
    vi.spyOn(authStore, 'login').mockImplementation(() => new Promise(() => {}))

    await wrapper.find('input[type="password"]').setValue('password123')
    await wrapper.find('form').trigger('submit')

    const submitButton = wrapper.find('button[type="submit"]')
    expect(submitButton.attributes('disabled')).toBeDefined()
  })
})
```

**Estimated Time:** 6-8 hours for all 7 login components

---

### Phase 4: E2E Critical Path Tests (DAY 3-4)

**File:** `tests/e2e/login-flow.spec.ts`

```typescript
import { test, expect } from '@playwright/test'

test.describe('Login Flow E2E', () => {
  test('should complete full login flow without MFA', async ({ page }) => {
    await page.goto('/')

    // Username step
    await page.fill('input[type="email"]', 'test@example.com')
    await page.click('button:text("Next")')

    // Password step
    await page.fill('input[type="password"]', 'password123')
    await page.click('button:text("Login")')

    // Should redirect to home
    await expect(page).toHaveURL('/home')
    await expect(page.locator('text=Welcome')).toBeVisible()
  })

  test('should complete MFA flow', async ({ page }) => {
    await page.goto('/')

    await page.fill('input[type="email"]', 'mfa-user@example.com')
    await page.click('button:text("Next")')

    await page.fill('input[type="password"]', 'password123')
    await page.click('button:text("Login")')

    // MFA step
    await expect(page.locator('text=Enter MFA Code')).toBeVisible()
    await page.fill('input[name="mfaCode"]', '123456')
    await page.click('button:text("Verify")')

    await expect(page).toHaveURL('/home')
  })

  test('should handle logout', async ({ page }) => {
    // Login first
    await page.goto('/')
    await page.fill('input[type="email"]', 'test@example.com')
    await page.click('button:text("Next")')
    await page.fill('input[type="password"]', 'password123')
    await page.click('button:text("Login")')

    await expect(page).toHaveURL('/home')

    // Logout
    await page.click('button:text("Logout")')
    await expect(page).toHaveURL('/login')

    // Should not allow accessing /home
    await page.goto('/home')
    await expect(page).toHaveURL('/login')
  })
})
```

**Estimated Time:** 4-6 hours

---

## 6. Integration vs Unit Test Strategy

### Unit Tests (Vitest)

**Target:** 70% coverage minimum

**Scope:**
- Pinia store actions/getters (auth.ts, user.ts)
- Pure utility functions (apiHelper.ts)
- Individual component logic (login steps)
- Computed properties and watchers

**Characteristics:**
- Fast execution (<1s for entire suite)
- Mock all external dependencies (VeociJS, localStorage, router)
- Test single units in isolation
- Run on every commit (pre-commit hook)

**File Pattern:** `tests/unit/**/*.spec.ts`

---

### Integration Tests (Vitest)

**Target:** 50% coverage of critical paths

**Scope:**
- Store + Service interaction (auth store → VeociJS)
- Router + Store integration (guards + auth state)
- Component + Store integration (LoginView → auth store)
- Multi-component interactions (login flow steps)

**Characteristics:**
- Slower than unit tests (1-5s per test)
- Partial mocking (mock VeociJS API, test real Pinia/Router)
- Test layer boundaries
- Run on push to main

**File Pattern:** `tests/integration/**/*.spec.ts`

---

### E2E Tests (Playwright)

**Target:** 20 critical user journeys

**Scope:**
- Complete login flow (no MFA, MFA, forgot password)
- Protected route access (authenticated, unauthenticated)
- Session persistence (page reload, token refresh)
- Logout flow
- Error states (network failure, invalid credentials)

**Characteristics:**
- Slowest (10-30s per test)
- No mocking (real browser, real API or MSW mock server)
- Test from user perspective
- Run on PR + nightly CI

**File Pattern:** `tests/e2e/**/*.spec.ts`

---

### Testing Pyramid

```
        /\
       /  \  E2E Tests (20 tests)
      /    \  - Playwright
     /      \  - Critical user journeys
    /--------\
   / Integration \ (50 tests)
  /   Tests      \  - Vitest
 /   Multi-layer  \  - Store + Router + Component
/------------------\
/ Unit Tests        \ (200+ tests)
/   Isolated logic  \  - Vitest
/   Fast feedback   \  - Mock all dependencies
/--------------------\
```

**Total Estimated Tests:** 270+

---

## 7. Recommended Coverage Thresholds

### Global Thresholds

```javascript
// vitest.config.ts
coverage: {
  thresholds: {
    lines: 80,
    functions: 80,
    branches: 75,
    statements: 80,
  }
}
```

### Per-File Thresholds (Critical Files)

```javascript
coverage: {
  perFile: true,
  thresholds: {
    'src/store/auth.ts': {
      lines: 90,
      functions: 95,
      branches: 85,
    },
    'src/router/index.ts': {
      lines: 90,
      branches: 90,
    },
    'src/services/api-client.ts': {
      lines: 85,
      functions: 90,
    },
  }
}
```

---

## 8. Mock Strategy

### VeociJS SDK Mocking

**Approach:** Factory pattern for consistent mocking across tests

**File:** `tests/mocks/veoci-client.mock.ts`

```typescript
import { vi } from 'vitest'

export const createMockVeociClient = () => ({
  loadModule: vi.fn(),
  Login: {
    login: vi.fn(),
    loginWithMfaToken: vi.fn(),
    logout: vi.fn(),
    fetchLoginMetadata: vi.fn(),
  },
  Object: {
    get: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
  },
  AuthdUser: {
    getCurrentUser: vi.fn(),
  },
})

export const mockLoginSuccess = (token = 'mock-token') => ({
  authToken: token,
  mfaRequired: false,
})

export const mockLoginMfaRequired = (mfaToken = 'mock-mfa-token') => ({
  mfaToken,
  mfaRequired: true,
})
```

### LocalStorage Mocking

**File:** `tests/mocks/localStorage.mock.ts`

```typescript
export const createMockLocalStorage = () => {
  const store = new Map<string, string>()

  return {
    getItem: vi.fn((key: string) => store.get(key) ?? null),
    setItem: vi.fn((key: string, value: string) => store.set(key, value)),
    removeItem: vi.fn((key: string) => store.delete(key)),
    clear: vi.fn(() => store.clear()),
  }
}
```

### API Response Mocking (MSW)

**File:** `tests/mocks/handlers.ts`

```typescript
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.post('/auth/login', async ({ request }) => {
    const { username, password } = await request.json()

    if (username === 'user@example.com' && password === 'password123') {
      return HttpResponse.json({
        authToken: 'mock-auth-token',
        mfaRequired: false,
      })
    }

    return HttpResponse.json(
      { error: 'Invalid credentials' },
      { status: 401 }
    )
  }),

  http.post('/auth/mfa/verify', async ({ request }) => {
    const { mfaCode } = await request.json()

    if (mfaCode === '123456') {
      return HttpResponse.json({
        authToken: 'mock-auth-token-with-mfa',
      })
    }

    return HttpResponse.json(
      { error: 'Invalid MFA code' },
      { status: 401 }
    )
  }),
]
```

---

## 9. CI/CD Integration

### GitHub Actions Workflow

**File:** `.github/workflows/test.yml`

```yaml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run test:coverage
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage/lcov.info

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run test:e2e
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

### Pre-commit Hook (Husky)

```bash
npm install -D husky lint-staged

npx husky init
```

**File:** `.husky/pre-commit`

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npm run test -- --run --passWithNoTests
npm run lint
```

---

## 10. Test Data Management

### Fixtures Strategy

**File:** `tests/fixtures/users.ts`

```typescript
export const testUsers = {
  validUser: {
    username: 'test@example.com',
    password: 'password123',
    authToken: 'mock-token-valid-user',
  },
  mfaUser: {
    username: 'mfa@example.com',
    password: 'password123',
    mfaToken: 'mock-mfa-token',
    mfaCode: '123456',
  },
  invalidUser: {
    username: 'invalid@example.com',
    password: 'wrongpassword',
  },
}
```

**File:** `tests/fixtures/api-responses.ts`

```typescript
export const apiResponses = {
  loginSuccess: {
    authToken: 'mock-auth-token-12345',
    expiresIn: 3600,
    refreshToken: 'mock-refresh-token',
  },
  loginMfaRequired: {
    mfaToken: 'mock-mfa-token-67890',
    mfaRequired: true,
    mfaMethods: ['totp', 'sms'],
  },
  currentUser: {
    id: 1,
    email: 'test@example.com',
    firstName: 'Test',
    lastName: 'User',
    permissions: ['read', 'write'],
  },
}
```

---

## 11. Visual Regression Testing (Optional)

### Recommendation: Playwright Snapshots

**Use Cases:**
- Login component visual consistency
- Error message styling
- Responsive design breakpoints

**Example Test:**

```typescript
test('login page visual regression', async ({ page }) => {
  await page.goto('/login')
  await expect(page).toHaveScreenshot('login-page.png', {
    maxDiffPixels: 100,
  })
})
```

**CI Integration:** Store baseline snapshots in `tests/e2e/__screenshots__/`

---

## 12. Performance Testing Strategy

### Login Flow Performance Benchmarks

**Tool:** Playwright Performance API

```typescript
test('login flow performance', async ({ page }) => {
  const start = Date.now()

  await page.goto('/')
  await page.fill('input[type="email"]', 'test@example.com')
  await page.click('button:text("Next")')
  await page.fill('input[type="password"]', 'password123')
  await page.click('button:text("Login")')
  await page.waitForURL('/home')

  const duration = Date.now() - start

  expect(duration).toBeLessThan(3000) // Login should complete in <3s
})
```

### Metrics to Track

```
- Time to Interactive (TTI)
- First Contentful Paint (FCP)
- API response time (login, MFA, metadata)
- localStorage read/write time
- Router navigation time
```

---

## 13. Implementation Roadmap

### Week 1: Foundation

**Day 1:**
- Install Vitest + dependencies
- Configure vitest.config.ts
- Set up test directory structure
- Write auth store unit tests (20 tests)

**Day 2:**
- Write router guard integration tests (6 tests)
- Write user store unit tests (10 tests)

**Day 3:**
- Write LoginPasswordStep component tests
- Write LoginMfaStep component tests
- Write LoginView orchestration tests

**Day 4:**
- Install Playwright
- Configure playwright.config.ts
- Write critical E2E login flow tests (5 tests)

**Day 5:**
- Set up CI/CD pipeline
- Configure coverage reporting
- Document testing standards

---

### Week 2: Expansion

**Day 6-7:**
- Test remaining login components (ForgotPassword, ChangePassword)
- Test HomeView, DebugView components
- Test GlobalToolbar component

**Day 8-9:**
- Write api-client.ts tests
- Write apiHelper.ts tests
- Mock VeociJS SDK comprehensively

**Day 10:**
- E2E tests for error states
- E2E tests for session persistence
- Visual regression tests for login UI

---

### Week 3: Hardening

**Day 11-12:**
- Increase coverage to 80%
- Add edge case tests
- Add negative tests (malformed input, network errors)

**Day 13:**
- Performance testing
- Load testing (if applicable)
- Accessibility testing (aria-labels, keyboard nav)

**Day 14:**
- Documentation (testing guide)
- Code review
- Refactor based on test findings

---

## 14. Success Metrics

### Coverage Targets (End of Week 3)

```
Overall Coverage:        80%+
Critical Files Coverage: 90%+

Breakdown:
  - auth.ts:             95%
  - router/index.ts:     90%
  - user.ts:             85%
  - api-client.ts:       85%
  - Login components:    80%
  - Other components:    70%
```

### Test Suite Performance

```
Unit Tests:        < 5 seconds (full suite)
Integration Tests: < 15 seconds (full suite)
E2E Tests:         < 2 minutes (full suite)
Total CI Time:     < 3 minutes
```

### Quality Gates

```
✅ All tests must pass before merge
✅ Coverage must not decrease below 80%
✅ E2E smoke tests must pass before deploy
✅ No skipped or pending tests in main branch
✅ 100% of critical paths must have E2E coverage
```

---

## 15. Risk Assessment

### High-Risk Areas (Require Immediate Testing)

```
🔴 auth.ts login() - Authentication bypass risk
🔴 router guards - Unauthorized access risk
🔴 localStorage token handling - Token leakage risk
🔴 MFA verification - Security bypass risk
🔴 Token refresh - Session hijacking risk
```

### Medium-Risk Areas

```
🟡 Component error handling - UX degradation
🟡 API error responses - Unclear failures
🟡 Session expiry - User frustration
🟡 Form validation - Invalid data submission
```

### Low-Risk Areas (Can Defer)

```
🟢 UI styling - Visual inconsistencies
🟢 Debug views - Non-production code
🟢 Optional features - Low usage
```

---

## 16. Test Maintenance Strategy

### Test Code Quality Standards

```typescript
// ✅ GOOD: Descriptive, single assertion focus
it('should store authToken in localStorage on successful login', async () => {
  const store = useAuthStore()
  await store.login('user@example.com', 'password123')
  expect(localStorage.setItem).toHaveBeenCalledWith('authToken', expect.any(String))
})

// ❌ BAD: Vague, multiple unrelated assertions
it('should login correctly', async () => {
  const store = useAuthStore()
  await store.login('user@example.com', 'password123')
  expect(store.authToken).toBeTruthy()
  expect(router.currentRoute.value.path).toBe('/home')
  expect(store.user).toBeNull() // Unrelated assertion
})
```

### Refactoring Test Alongside Code

```
RULE: When refactoring production code, update tests FIRST.
  1. Update test to reflect new behavior
  2. Watch test fail
  3. Refactor production code
  4. Watch test pass
```

### Test Review Checklist

```
☐ Test name clearly describes what is being tested
☐ Single assertion per test (or closely related assertions)
☐ No hard-coded magic values (use constants/fixtures)
☐ Proper test isolation (no shared state between tests)
☐ Async tests use async/await (not callbacks)
☐ Mocks are reset in beforeEach/afterEach
☐ Test is deterministic (no random values, no Date.now())
☐ Test focuses on behavior, not implementation details
```

---

## 17. Additional Recommendations

### Accessibility Testing

**Tool:** `axe-core` + Playwright

```bash
npm install -D @axe-core/playwright
```

**Example:**

```typescript
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test('login page should be accessible', async ({ page }) => {
  await page.goto('/login')

  const accessibilityScanResults = await new AxeBuilder({ page }).analyze()

  expect(accessibilityScanResults.violations).toEqual([])
})
```

---

### Security Testing

**Tests to Add:**

```typescript
describe('security', () => {
  it('should not log authToken to console')
  it('should sanitize error messages (no token exposure)')
  it('should prevent XSS in username field')
  it('should prevent CSRF on login endpoint')
  it('should enforce HTTPS in production')
  it('should expire tokens after logout')
  it('should not persist tokens in query params')
})
```

---

### Error Boundary Testing

```typescript
describe('error handling', () => {
  it('should display generic error on network failure')
  it('should retry failed API calls (3 attempts)')
  it('should fallback to offline mode if API unavailable')
  it('should log errors to monitoring service')
})
```

---

## 18. Dependency Analysis

### Required NPM Packages

```json
{
  "devDependencies": {
    "@axe-core/playwright": "^4.8.0",
    "@pinia/testing": "^0.1.3",
    "@playwright/test": "^1.40.0",
    "@vitest/coverage-v8": "^1.0.0",
    "@vitest/ui": "^1.0.0",
    "@vue/test-utils": "^2.4.0",
    "happy-dom": "^12.10.0",
    "jsdom": "^23.0.0",
    "msw": "^2.0.0",
    "vitest": "^1.0.0"
  }
}
```

**Total Size:** ~50MB (dev only, not in production bundle)

---

## 19. Alternative Testing Approaches (Considered & Rejected)

### Approach 1: Jest + Testing Library

**Rejected Because:**
- Slower build times with Rsbuild
- More complex ESM configuration
- Vitest has better Vite/Rsbuild integration

### Approach 2: Cypress for E2E

**Rejected Because:**
- Playwright has better debugging tools
- Playwright supports multiple browsers natively
- Playwright is faster for parallel execution

### Approach 3: Storybook Component Testing

**Considered For:**
- Isolated component development
- Visual regression testing

**Deferred Because:**
- Adds build complexity
- Coverage needs are met by Vitest + Playwright
- Can add later if component library grows

---

## 20. Final Recommendations

### Immediate Actions (CRITICAL)

```
1. Install Vitest + @vue/test-utils + @pinia/testing
2. Write auth.ts unit tests (20 tests) - DAY 1
3. Write router guard tests (6 tests) - DAY 1
4. Install Playwright - DAY 2
5. Write login flow E2E tests (5 tests) - DAY 2
6. Set up CI/CD pipeline with coverage gates - DAY 3
```

### Short-Term Goals (WEEK 1-2)

```
- Achieve 60% overall coverage
- 90% coverage on auth.ts, router/index.ts
- 10+ E2E tests covering critical paths
- CI pipeline blocking merges on test failures
```

### Long-Term Goals (WEEK 3-4)

```
- Achieve 80% overall coverage
- 100+ unit tests, 50+ integration tests, 20+ E2E tests
- Visual regression testing enabled
- Performance benchmarks in CI
- Accessibility testing in CI
```

---

## Conclusion

**The application currently has ZERO test coverage. This is unacceptable for production deployment.**

### Critical Risks Without Tests

```
❌ Authentication bypass vulnerabilities untested
❌ Route guards can fail silently
❌ Token refresh failures will brick user sessions
❌ MFA flow has no validation
❌ Regression bugs will slip into production
❌ Refactoring is dangerous without test safety net
```

### Value Proposition of Testing

```
✅ Catch bugs before users do
✅ Enable confident refactoring
✅ Document expected behavior
✅ Improve code quality through testability
✅ Reduce debugging time
✅ Faster development velocity (after initial investment)
✅ Sleep better at night
```

### ROI Estimate

```
Initial Investment:  ~3 weeks (1 developer)
Ongoing Maintenance: ~10% of development time

Benefits:
  - 80% reduction in production bugs
  - 50% faster debugging
  - 100% confidence in refactoring
  - Measurable code quality metrics
```

---

## Appendix A: File Structure Recommendation

```
veoci-app-template-construct/
├── src/
│   └── (existing application code)
├── tests/
│   ├── setup.ts                    # Vitest global setup
│   ├── mocks/
│   │   ├── veoci-client.mock.ts    # VeociJS mock factory
│   │   ├── localStorage.mock.ts    # localStorage mock
│   │   └── handlers.ts             # MSW API handlers
│   ├── fixtures/
│   │   ├── users.ts                # Test user data
│   │   └── api-responses.ts        # Mock API responses
│   ├── unit/
│   │   ├── store/
│   │   │   ├── auth.spec.ts        # Auth store tests
│   │   │   └── user.spec.ts        # User store tests
│   │   ├── services/
│   │   │   ├── api-client.spec.ts  # VeociJS client tests
│   │   │   └── apiHelper.spec.ts   # Helper tests
│   │   └── views/
│   │       └── login/
│   │           ├── LoginPasswordStep.spec.ts
│   │           └── LoginMfaStep.spec.ts
│   ├── integration/
│   │   ├── router/
│   │   │   └── guards.spec.ts      # Route guard tests
│   │   └── auth-flow.spec.ts       # Full auth flow integration
│   └── e2e/
│       ├── login-flow.spec.ts      # Login E2E tests
│       ├── protected-routes.spec.ts # Route access E2E
│       └── session-persistence.spec.ts
├── vitest.config.ts
├── playwright.config.ts
└── package.json
```

---

## Appendix B: Command Reference

```bash
# Run all unit tests
npm run test

# Run tests in watch mode
npm run test -- --watch

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm run test -- tests/unit/store/auth.spec.ts

# Run tests matching pattern
npm run test -- --grep "login"

# Run E2E tests
npm run test:e2e

# Run E2E tests in UI mode (debug)
npm run test:e2e:ui

# Run all tests (unit + E2E)
npm run test:all

# Generate coverage report and open in browser
npm run test:coverage && open coverage/index.html
```

---

**STATUS:** Test infrastructure does not exist. Immediate implementation required.

**PRIORITY:** P0 (Critical)

**ESTIMATED EFFORT:** 3-4 weeks for full test suite

**RECOMMENDED START DATE:** Immediately

**FAILURE CONSEQUENCE:** Production deployment without tests risks security vulnerabilities, session failures, and authentication bypass.

---

Wake up, Neo.
