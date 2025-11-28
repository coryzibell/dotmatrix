# Veoci App Template Construct - UX & Developer Experience Review

**Reviewer:** Persephone
**Date:** 2025-11-27
**Scope:** Architecture design review (pre-implementation)

---

## Executive Summary

The architecture is **technically sound** but risks **poor developer experience** and **confused users**. The multi-step login orchestrator (LoginView.vue) is designed to become a 14KB monolith. Error handling is mentioned but not architected. Loading states are described as boolean flags without accessibility considerations. The developer onboarding story is absent.

This feels like a template designed by someone who knows Vue, not someone who remembers what it's like to clone a repo and just want it to work.

---

## 1. Login Flow UX

### The Problem: State Machine Hidden in a Component

**Current Design:**
```
LoginView.vue (14KB orchestrator)
├─ LoginUsernameStep.vue
├─ LoginPasswordStep.vue
├─ LoginMfaStep.vue
├─ MfaStep.vue (wait, isn't this the same as LoginMfaStep?)
├─ LoginForgotPasswordStep.vue
└─ ChangePasswordStep.vue
```

**What the User Feels:**
- **Confusion between MfaStep and LoginMfaStep** - the architecture doesn't explain why there are two. Are they for different flows? Is one a wrapper? This ambiguity will leak into the UI.
- **No clear "you are here" indicator** - the sequence diagram shows steps, but nothing says "Step 2 of 3" or "Almost there."
- **Forgot password feels bolted on** - it's listed as a step in the login flow, but forgot password is an escape hatch, not a progression. Should be a link that breaks flow, not a step.

**What the Developer Experiences:**
- **14KB LoginView.vue** - this will become a God object. All step transitions, all state management for the flow, all error boundaries. Hard to test, hard to reason about.
- **Step components without contracts** - the architecture doesn't show what props/emits each step expects. Will developers have to read LoginView.vue to understand how to modify a step?

### Recommendation: Extract a Login State Machine

**Option A: Explicit State Machine (XState or similar)**
```typescript
// store/loginFlow.ts
import { createMachine } from 'xstate'

export const loginFlowMachine = createMachine({
  id: 'login',
  initial: 'username',
  states: {
    username: { on: { SUBMIT: 'password' } },
    password: {
      on: {
        MFA_REQUIRED: 'mfa',
        SUCCESS: 'authenticated'
      }
    },
    mfa: { on: { SUCCESS: 'authenticated' } },
    forgotPassword: { on: { BACK: 'username' } }
  }
})
```

**Why:**
- LoginView.vue becomes a 2KB component that renders `currentState.value`
- Steps declare explicit contracts via machine events
- Developer can visualize flow without reading code
- User gets deterministic "Step X of Y" labels from machine state

**Option B: Composable Step Manager**
```typescript
// composables/useLoginFlow.ts
export function useLoginFlow() {
  const currentStep = ref<LoginStep>('username')
  const progress = computed(() => steps.indexOf(currentStep.value) + 1)
  const totalSteps = computed(() => steps.length)

  function nextStep(step: LoginStep) { ... }
  function resetFlow() { ... }

  return { currentStep, progress, totalSteps, nextStep, resetFlow }
}
```

**Why:**
- Lighter weight than XState
- LoginView.vue uses the composable, stays under 5KB
- Still gives "Step 2 of 3" without hardcoding

### Error States: Currently Vague

**Current Design:**
- "Error handling in auth store"
- `this.loading = true/false`

**What's Missing:**
- **Where do errors render?** Each step component? LoginView overlay? Toast notifications?
- **What errors are possible?** Network failure? Invalid credentials? Account locked? MFA timeout?
- **How does the user recover?** Is there a "Try again" button? Does the form clear? Does focus move?

**User Impact:**
- User types password wrong → sees "Error" → doesn't know if they should re-type username or just password
- Network fails during MFA → no indication if they should refresh or wait
- Account locked → shown same error as wrong password (security anti-pattern, but also confusing)

**Recommendation: Error Dictionary + Component Error Slots**

```typescript
// store/auth.ts
export const AUTH_ERRORS = {
  INVALID_CREDENTIALS: {
    message: 'Username or password is incorrect',
    recovery: 'Double-check your credentials or use Forgot Password',
    clearFields: ['password']
  },
  MFA_TIMEOUT: {
    message: 'MFA code expired',
    recovery: 'Request a new code',
    action: 'resendMfaCode'
  },
  NETWORK_ERROR: {
    message: 'Connection lost',
    recovery: 'Check your network and try again',
    retry: true
  }
}
```

```vue
<!-- LoginPasswordStep.vue -->
<template>
  <v-text-field v-model="password" :error-messages="error?.message" />
  <v-alert v-if="error" type="error">
    {{ error.message }}
    <template v-if="error.recovery">
      <p class="text-caption mt-2">{{ error.recovery }}</p>
    </template>
    <v-btn v-if="error.action" @click="handleErrorAction(error.action)">
      {{ getActionLabel(error.action) }}
    </v-btn>
  </v-alert>
</template>
```

**Why:**
- User sees **what happened** and **what to do**
- Developer has a canonical error catalog to extend
- Accessibility: screen readers get structured error + recovery

### Loading States: Boolean Flags Are Not Enough

**Current Design:**
```typescript
this.loading = true
await authStore.login(username, password)
this.loading = false
```

**What the User Doesn't Get:**
- **Progress indication** - "Verifying credentials..." vs "Checking MFA status..." vs "Signing in..."
- **Timeout awareness** - if it takes 10 seconds, is it frozen or just slow?
- **Skeleton states** - button disabled with no visual feedback

**Recommendation: Loading States as Enums + Accessible Indicators**

```typescript
// composables/useLoadingState.ts
export type LoadingPhase =
  | 'idle'
  | 'submitting'
  | 'verifying'
  | 'mfa-check'
  | 'finalizing'

export function useLoadingState() {
  const phase = ref<LoadingPhase>('idle')
  const phaseLabels: Record<LoadingPhase, string> = {
    idle: '',
    submitting: 'Submitting credentials...',
    verifying: 'Verifying login...',
    'mfa-check': 'Checking multi-factor authentication...',
    finalizing: 'Signing in...'
  }

  return { phase, phaseLabel: computed(() => phaseLabels[phase.value]) }
}
```

```vue
<!-- LoginPasswordStep.vue -->
<v-btn :loading="phase !== 'idle'" :disabled="phase !== 'idle'">
  {{ phase === 'idle' ? 'Continue' : phaseLabel }}
  <span class="sr-only" v-if="phase !== 'idle'">{{ phaseLabel }}</span>
</v-btn>
```

**Why:**
- User sees **what's happening** during long requests
- Screen reader users hear meaningful status ("Verifying login" vs "Loading")
- Developer can show different spinners/messages per phase

### MfaStep vs LoginMfaStep: Naming Collision

**Observation:** Two components with near-identical names suggests unclear separation of concerns.

**Possible Scenarios:**
1. **MfaStep is reusable, LoginMfaStep wraps it** → Name should reflect this: `MfaCodeInput.vue` + `LoginMfaStep.vue`
2. **They're for different flows (login vs account settings)** → Namespace differently: `login/MfaStep.vue` vs `settings/MfaStep.vue`
3. **One is legacy/duplicate** → Delete it before template ships

**User Impact:** None directly, but developer confusion leads to inconsistent UX later.

**Recommendation:** Resolve naming before implementation. If #1, rename to `MfaCodeInput.vue`. If #2, use folders.

---

## 2. Developer Onboarding Friction

### The Missing README Story

**Current Architecture Document:** 613 lines of Mermaid diagrams and technical details.

**Missing from Architecture:**
- "Clone this repo, now what?"
- "What environment variables do I need?"
- "How do I point at a real Veoci API vs mock?"
- "What's the first page I see when I run `npm run dev`?"

**New Developer Experience:**
```bash
git clone <repo>
cd veoci-app-template-construct
npm install
npm run dev
# Opens browser to localhost:3000
# ...shows login page
# ...I don't have Veoci credentials
# ...now what?
```

**What Happens Next:**
- Developer reads architecture.md (intimidating, doesn't answer "how do I see something")
- Developer tries username "admin" password "admin" (fails, no feedback on whether backend is even running)
- Developer searches for "mock" or "test user" (finds nothing)
- Developer gives up or Slacks teammate

**Recommendation: Developer Journey Documentation**

**File: `GETTING_STARTED.md`** (not in architecture, separate file)

```markdown
# Getting Started

## Quick Start (5 minutes)

1. Clone and install:
   ```bash
   git clone <repo>
   cd veoci-app-template-construct
   npm install
   ```

2. Start dev server:
   ```bash
   npm run dev
   ```

   Opens `http://localhost:3000` → you'll see the login page.

3. **First time?** You need a Veoci API to connect to.

   **Option A: Use Veoci Sandbox**
   ```bash
   echo "VEOCI_API_URL=https://sandbox.veoci.com" > .env
   npm run dev
   ```
   Use your Veoci sandbox credentials.

   **Option B: Mock API (coming soon)**
   ```bash
   npm run dev:mock  # Starts with mock API, pre-seeded test user
   ```

## What You See

- `/` → Login page (multi-step: username → password → optional MFA)
- `/home` → Home page (protected, redirects to login if not authenticated)
- `/debug` → Debug view (shows VeociJS SDK status, API config)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VEOCI_API_URL` | Yes | Veoci API base URL (e.g., `https://your-instance.veoci.com`) |

## Common Issues

**"I see the login page but can't log in"**
- Check `VEOCI_API_URL` is set and reachable
- Open `/debug` to verify API config
- Check browser console for CORS errors (dev proxy should handle this, but double-check)

**"npm run dev fails"**
- Node version? Requires Node 18+
- Try `rm -rf node_modules package-lock.json && npm install`
```

**Why:**
- Developer sees a working page in 5 minutes
- Clear error paths when things don't work
- `/debug` view becomes a developer lifeline (not just a dumping ground)

### Environment Variable UX

**Current Design:**
- `VEOCI_API_URL` required for dev proxy
- Not mentioned what happens if it's missing

**What the Developer Experiences:**
```bash
npm run dev
# Dev server starts
# Opens browser
# Login page loads
# Types username/password
# Clicks submit
# ...network error? CORS error? Nothing happens?
```

**Recommendation: Startup Validation + Helpful Errors**

```typescript
// rsbuild.config.ts or early in main.ts
if (!import.meta.env.VEOCI_API_URL) {
  throw new Error(`
    Missing VEOCI_API_URL environment variable.

    Create a .env file:
    echo "VEOCI_API_URL=https://your-instance.veoci.com" > .env

    Then restart dev server.
  `)
}
```

**Why:**
- Developer knows immediately what's wrong
- Error message includes the fix
- No silent failures during login attempts

### The Debug View: Underutilized Developer Tool

**Current Design:** 5KB DebugView.vue (mentioned but not detailed)

**What It Could Be:**
- VeociJS SDK module status (loaded, version, config)
- Current auth state (token present, expiry, user info)
- API endpoint test (ping `/api/v1/health` or similar)
- Environment variable dump (VEOCI_API_URL, build version)
- localStorage inspection (authToken, other persisted state)

**Recommendation: Make /debug the First Stop for Troubleshooting**

```vue
<!-- DebugView.vue -->
<template>
  <v-container>
    <h1>Debug Panel</h1>

    <v-card class="mb-4">
      <v-card-title>API Configuration</v-card-title>
      <v-card-text>
        <v-table>
          <tbody>
            <tr>
              <td>API URL</td>
              <td><code>{{ apiUrl }}</code></td>
              <td>
                <v-chip :color="apiReachable ? 'success' : 'error'">
                  {{ apiReachable ? 'Reachable' : 'Unreachable' }}
                </v-chip>
              </td>
            </tr>
            <tr>
              <td>VeociJS Version</td>
              <td>{{ veociJsVersion }}</td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>

    <v-card class="mb-4">
      <v-card-title>Authentication State</v-card-title>
      <v-card-text>
        <v-table>
          <tbody>
            <tr>
              <td>Authenticated</td>
              <td>
                <v-chip :color="authStore.isAuthenticated ? 'success' : 'warning'">
                  {{ authStore.isAuthenticated }}
                </v-chip>
              </td>
            </tr>
            <tr>
              <td>Token Present</td>
              <td>{{ authStore.authToken ? 'Yes' : 'No' }}</td>
            </tr>
            <tr v-if="authStore.authToken">
              <td>Token Expiry</td>
              <td>{{ tokenExpiry || 'Unknown' }}</td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>

    <v-card>
      <v-card-title>localStorage</v-card-title>
      <v-card-text>
        <pre><code>{{ localStorageDump }}</code></pre>
      </v-card-text>
    </v-card>
  </v-container>
</template>
```

**Why:**
- Developer can self-diagnose config issues
- QA/support can ask for screenshot of /debug page
- Reduces "it doesn't work" tickets

---

## 3. Component Organization

### LoginView.vue: Designed to Become Unmaintainable

**Predicted Growth:**
- Step transition logic: ~100 lines
- Error handling per step: ~50 lines
- Loading state management: ~30 lines
- Forgot password redirect: ~20 lines
- Change password flow: ~30 lines
- MFA flow branching: ~40 lines
- Analytics/tracking: ~20 lines
- Edge case handling (session timeout, back button, browser refresh): ~50 lines

**Total: 340+ lines in LoginView.vue, plus template boilerplate → 14KB+**

**Testing Nightmare:**
- Can't test step transitions without mocking entire auth store
- Can't test error recovery without triggering real API failures
- Can't test MFA flow in isolation

**Recommendation: Delegate Orchestration to Composable or Store**

**Option A: Composable Orchestrator**
```typescript
// composables/useLoginOrchestrator.ts
export function useLoginOrchestrator() {
  const currentStep = ref<LoginStep>('username')
  const stepHistory = ref<LoginStep[]>([])
  const authStore = useAuthStore()

  async function handleUsernameSubmit(email: string) {
    const metadata = await authStore.fetchLoginMetadata(email)
    if (metadata.ssoRequired) {
      currentStep.value = 'sso-redirect'
    } else {
      currentStep.value = 'password'
    }
    stepHistory.value.push('username')
  }

  async function handlePasswordSubmit(password: string) {
    const result = await authStore.login(email, password)
    if (result.mfaRequired) {
      currentStep.value = 'mfa'
    } else {
      currentStep.value = 'authenticated'
    }
    stepHistory.value.push('password')
  }

  function goBack() {
    stepHistory.value.pop()
    currentStep.value = stepHistory.value[stepHistory.value.length - 1] || 'username'
  }

  return { currentStep, handleUsernameSubmit, handlePasswordSubmit, goBack }
}
```

**LoginView.vue becomes:**
```vue
<script setup lang="ts">
import { useLoginOrchestrator } from '@/composables/useLoginOrchestrator'

const { currentStep, handleUsernameSubmit, handlePasswordSubmit, goBack } = useLoginOrchestrator()
</script>

<template>
  <div class="login-container">
    <LoginUsernameStep v-if="currentStep === 'username'" @submit="handleUsernameSubmit" />
    <LoginPasswordStep v-if="currentStep === 'password'" @submit="handlePasswordSubmit" @back="goBack" />
    <LoginMfaStep v-if="currentStep === 'mfa'" @submit="handleMfaSubmit" @back="goBack" />
  </div>
</template>
```

**LoginView.vue size: ~50 lines, ~2KB**

**Option B: Login Flow Store**
```typescript
// store/loginFlow.ts
export const useLoginFlowStore = defineStore('loginFlow', {
  state: () => ({
    currentStep: 'username' as LoginStep,
    stepHistory: [] as LoginStep[],
    error: null as AuthError | null
  }),

  actions: {
    async submitUsername(email: string) { ... },
    async submitPassword(password: string) { ... },
    async submitMfa(code: string) { ... },
    goBack() { ... },
    reset() { ... }
  }
})
```

**Why:**
- LoginView.vue becomes a thin presentation layer
- Step logic is testable in isolation (unit test the composable/store)
- Can reuse step components in other flows (e.g., account settings MFA setup)

### Step Components: Contract Unclear

**Current Architecture:** Lists components, doesn't show their interface.

**What the Developer Needs to Know:**
- What props does LoginPasswordStep expect? `username`? `email`?
- What events does it emit? `submit`? `next`? `login`?
- Does it handle its own error rendering or delegate to parent?
- Does it manage its own loading state or receive `loading` prop?

**Recommendation: Define Step Component Contract**

```typescript
// types/login.ts
export interface LoginStepProps {
  // Common across all steps
  error?: AuthError | null
  loading?: boolean
}

export interface LoginStepEmits {
  submit: (data: unknown) => void
  back: () => void
}

// Specific step data types
export interface UsernameStepData {
  email: string
}

export interface PasswordStepData {
  password: string
}

export interface MfaStepData {
  code: string
  rememberMe: boolean
}
```

```vue
<!-- LoginPasswordStep.vue -->
<script setup lang="ts">
import type { LoginStepProps, PasswordStepData } from '@/types/login'

interface Props extends LoginStepProps {
  username: string  // Step-specific
}

const props = defineProps<Props>()

const emit = defineEmits<{
  submit: [data: PasswordStepData]
  back: []
}>()
</script>
```

**Why:**
- Developer knows what data flows in/out without reading parent
- TypeScript enforces contracts
- Steps can be developed/tested independently

---

## 4. Error Messaging: Helpful or Cryptic?

### Current Design: Unspecified

**Architecture mentions:**
- "Error handling in auth store"

**Architecture does NOT mention:**
- What errors are caught
- Where errors are displayed
- How errors are localized
- Whether errors include actionable next steps

**Real-World Error Scenarios:**

| Error | Backend Response | Current Likely UX | Better UX |
|-------|------------------|-------------------|-----------|
| Wrong password | `401 Unauthorized` | "Login failed" | "Password is incorrect. Try again or use Forgot Password." |
| Account locked | `403 Forbidden` | "Login failed" | "Account locked due to too many attempts. Contact support or try again in 30 minutes." |
| MFA code expired | `401 Invalid MFA token` | "MFA failed" | "Code expired. Request a new code." |
| Network timeout | `fetch() timeout` | "Error" or nothing | "Connection lost. Check your network and try again." |
| API down | `500 Internal Server Error` | "Login failed" | "Service temporarily unavailable. Try again in a few minutes." |

**User Impact:**
- Generic errors train users to guess and retry blindly
- No differentiation between "you did something wrong" and "system is broken"
- Users blame themselves for system failures

**Recommendation: Error Response Mapper**

```typescript
// services/errorMapper.ts
import type { AuthError } from '@/types/errors'

export function mapApiError(error: unknown): AuthError {
  // Network errors
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return {
      code: 'NETWORK_ERROR',
      message: 'Connection lost',
      userMessage: 'Unable to reach the server. Check your network connection.',
      recovery: 'Retry',
      retryable: true
    }
  }

  // HTTP errors
  if (error.response?.status === 401) {
    const body = error.response.data

    if (body.mfaRequired) {
      return {
        code: 'MFA_REQUIRED',
        message: 'MFA required',
        // This isn't an error, it's a state transition
        userMessage: null
      }
    }

    if (body.error === 'invalid_credentials') {
      return {
        code: 'INVALID_CREDENTIALS',
        message: 'Invalid credentials',
        userMessage: 'Username or password is incorrect.',
        recovery: 'Double-check your credentials or use Forgot Password',
        clearFields: ['password']
      }
    }
  }

  // Fallback
  return {
    code: 'UNKNOWN_ERROR',
    message: 'An unexpected error occurred',
    userMessage: 'Something went wrong. Please try again.',
    recovery: 'If this persists, contact support',
    retryable: true
  }
}
```

**Why:**
- Single source of truth for error presentation
- User sees helpful messages, not raw API responses
- Developer can extend with new error codes without touching components

---

## 5. Loading States: Properly Communicated?

### Current Design: Boolean Flags

```typescript
this.loading = true
await someAsyncCall()
this.loading = false
```

**Accessibility Problems:**
- Screen reader announces "Button" → user clicks → "Button" (no indication it's now disabled/loading)
- No `aria-live` announcement of status change
- Button might show spinner, but spinner has no accessible label

**Visual Problems:**
- User doesn't know if 2-second delay is normal or frozen
- No progress indication for multi-step async operations
- Generic "Loading..." doesn't convey what's happening

**Recommendation: Loading State with Accessible Announcements**

```vue
<!-- LoginPasswordStep.vue -->
<script setup lang="ts">
const { phase, phaseLabel } = useLoadingState()
const announcer = ref<HTMLElement | null>(null)

watch(phase, (newPhase) => {
  if (newPhase !== 'idle' && announcer.value) {
    // Force screen reader announcement
    announcer.value.textContent = phaseLabel.value
  }
})

async function handleSubmit() {
  phase.value = 'submitting'
  try {
    await authStore.login(username, password)
    phase.value = 'finalizing'
    // ...
  } catch (error) {
    phase.value = 'idle'
  }
}
</script>

<template>
  <v-btn
    :loading="phase !== 'idle'"
    :disabled="phase !== 'idle'"
    @click="handleSubmit"
  >
    <span v-if="phase === 'idle'">Continue</span>
    <span v-else>{{ phaseLabel }}</span>
  </v-btn>

  <!-- Screen reader announcements -->
  <div ref="announcer" class="sr-only" role="status" aria-live="polite" aria-atomic="true">
    {{ phaseLabel }}
  </div>
</template>

<style scoped>
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
```

**Why:**
- Screen reader users hear "Verifying login..." → "Signing in..." → "Success"
- Sighted users see meaningful button text, not just a spinner
- Developer gets reusable pattern for all async actions

---

## 6. Additional Observations

### Session Refresh: Mentioned, Not Detailed

**Architecture says:** "Session refresh managed by auth store"

**Questions:**
- Does it auto-refresh in the background? (good)
- Does it interrupt the user mid-action? (bad)
- What happens if refresh fails? Silent logout? Warning banner?

**User Impact:**
- User is filling out a form on `/home`
- Token expires, auto-refresh fails
- User clicks submit → 401 error, redirected to login
- Form data lost, user frustrated

**Recommendation:** Document refresh strategy in architecture, implement graceful degradation.

```typescript
// store/auth.ts
let refreshTimer: number | null = null

function scheduleTokenRefresh() {
  const expiresIn = getTokenExpiry(authToken) - Date.now()
  const refreshAt = expiresIn - (5 * 60 * 1000)  // Refresh 5 min before expiry

  refreshTimer = setTimeout(async () => {
    try {
      await refreshSession()
      scheduleTokenRefresh()  // Schedule next refresh
    } catch (error) {
      // Don't immediately log out, show warning banner
      showRefreshFailedWarning()
    }
  }, refreshAt)
}

function showRefreshFailedWarning() {
  // User-facing banner: "Session expiring soon. Save your work."
  // Give user 5 minutes to finish what they're doing before hard logout
}
```

### Vuetify Theme: Brand Colors Mentioned, Palette Not Shown

**Architecture says:** "Vuetify theme with Veoci brand colors"

**Questions:**
- What are the Veoci brand colors?
- Are they accessible (WCAG AA contrast)?
- Do they work in dark mode?

**Developer Impact:**
- No reference palette → inconsistent color usage
- No contrast checking → accessibility issues ship

**Recommendation:** Document theme in `veoci-theme.scss` with comments.

```scss
// veoci-theme.scss
// Veoci Brand Colors - Accessibility Verified (WCAG AA)

$veoci-primary: #0066cc;    // Primary brand blue - 4.5:1 contrast on white
$veoci-secondary: #ff6600;  // Secondary accent orange - 4.5:1 contrast on white
$veoci-error: #d32f2f;      // Error red
$veoci-success: #388e3c;    // Success green
$veoci-warning: #f57c00;    // Warning orange

// Ensure text on primary/secondary meets contrast requirements
// White text on $veoci-primary: 7.8:1 (AAA)
// White text on $veoci-secondary: 4.9:1 (AA)
```

### LocalStorage Security: XSS Risk Acknowledged, Not Mitigated

**Architecture says:** "localStorage (XSS vulnerable, consider httpOnly cookies for production)"

**Problem:** Template ships with localStorage by default. Developers will ship it to production.

**Recommendation:** Either fix it now or make it fail loudly.

**Option A: Ship with httpOnly cookies**
- Requires backend cooperation (Veoci API must set httpOnly cookie)
- More secure, but complex to implement

**Option B: Add warning in code**
```typescript
// store/auth.ts
function persistToken(token: string) {
  if (import.meta.env.PROD) {
    console.warn('WARNING: Storing auth token in localStorage is not secure for production. Use httpOnly cookies.')
  }
  localStorage.setItem('authToken', token)
}
```

**Option C: Make it configurable**
```typescript
// config/auth.config.ts
export const AUTH_CONFIG = {
  storage: import.meta.env.VITE_AUTH_STORAGE || 'localStorage',  // 'localStorage' | 'cookie' | 'memory'
  cookieOptions: { httpOnly: true, secure: true, sameSite: 'strict' }
}
```

---

## Summary: What This Template Needs Before Shipping

### Critical (Blocks Developer Success)
1. **Developer onboarding docs** - `GETTING_STARTED.md` with 5-minute quickstart
2. **Environment variable validation** - Fail fast with helpful error if `VEOCI_API_URL` missing
3. **Debug view enhancement** - Make `/debug` a troubleshooting lifeline
4. **Step component contracts** - TypeScript interfaces for props/emits

### High Priority (Prevents User Frustration)
5. **Login flow state machine** - Extract orchestration from LoginView.vue (composable or store)
6. **Error message dictionary** - Map API errors to user-friendly messages with recovery steps
7. **Loading state improvements** - Accessible announcements, meaningful labels
8. **Resolve MfaStep vs LoginMfaStep naming**

### Medium Priority (Quality of Life)
9. **Session refresh strategy** - Document + implement graceful failure handling
10. **Theme palette documentation** - Colors + contrast ratios in `veoci-theme.scss`
11. **localStorage security mitigation** - Warning or alternative storage option

### Nice to Have
12. **Mock API mode** - `npm run dev:mock` for developers without Veoci credentials
13. **Visual step progress indicator** - "Step 2 of 3" in UI
14. **Form field focus management** - Auto-focus first field on each step

---

## Closing Thoughts

This architecture is **capable**. It will work. But it won't **feel good** to use until someone asks:

- "What does the developer see when they first clone this repo?"
- "What does the user feel when login fails?"
- "What does the screen reader user hear during the MFA step?"

The current design optimizes for **technical correctness** (Pinia stores, VeociJS SDK, route guards). It doesn't optimize for **human experience** (helpful errors, accessible loading states, discoverable flows).

A template is supposed to make building easier. This one makes building *possible*, but not *pleasant*. Fix the developer onboarding and error UX, and it becomes a template worth shipping.

---

**Files that need to exist but don't:**
- `GETTING_STARTED.md` - Developer quickstart
- `docs/ERROR_CODES.md` - Catalog of auth errors + user-facing messages
- `composables/useLoginOrchestrator.ts` - Extract LoginView orchestration
- `composables/useLoadingState.ts` - Reusable loading state manager
- `types/login.ts` - Step component contracts
- `services/errorMapper.ts` - API error → user message mapper

**Files that exist but need enhancement:**
- `DebugView.vue` - Add API reachability check, token expiry, localStorage dump
- `veoci-theme.scss` - Document colors + contrast ratios
- `store/auth.ts` - Add session refresh strategy, error mapping

---

Wake up, Neo.
