# Error Handling Analysis: veoci-app-template-construct

**Analysis Date:** 2025-11-27
**Analyst:** Trinity
**Scope:** Auth Store, API Helper, Router Guards, Component Error Patterns

---

## Executive Summary

The error handling is **inconsistent and incomplete**. While try/catch blocks exist in auth operations, there's no unified error strategy. Recovery paths are unclear, user-facing messages are generic, and debugging is hampered by insufficient error context.

**Overall Grade:** D+
**Critical Gaps:** 4
**High Priority:** 5
**Medium Priority:** 3

---

## 1. Error Handling Coverage

### Auth Store (`src/store/auth.ts`)

**Covered Operations:**
- ✅ `login(username, password)` - try/catch present
- ✅ `loginWithMfaToken(mfaToken, rememberMe)` - try/catch present
- ✅ `logout()` - try/catch present
- ✅ `refreshSession()` - try/catch present

**Pattern Observed:**
```typescript
async login(username: string, password: string) {
  try {
    const response = await veociApi.login(username, password);
    if (response.mfaRequired) {
      this.mfaRequired = true;
      this.mfaToken = response.mfaToken;
    } else {
      this.authToken = response.token;
      localStorage.setItem('authToken', response.token);
    }
  } catch (error) {
    console.error('Login failed:', error);
    throw error; // Re-throws without transformation
  }
}
```

**Issues:**
- **No error classification** - All errors treated identically
- **Raw re-throw** - Components receive backend error objects directly
- **localStorage cleanup inconsistent** - Not all catch blocks clear stale tokens
- **No retry logic** - Network failures = instant failure

---

### API Helper (`src/services/apiHelper.ts`)

**Pattern:**
```typescript
export async function callApi(
  endpoint: string,
  options: RequestOptions,
  errorMessage: string = 'API request failed'
) {
  try {
    const response = await fetch(endpoint, options);
    if (!response.ok) {
      throw new Error(`${errorMessage}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error(errorMessage, error);
    throw error;
  }
}
```

**Issues:**
- **Generic error messages** - `errorMessage` parameter is too vague ("Login failed", "Request failed")
- **No status code handling** - 400 vs 401 vs 500 all throw same error
- **No response body parsing** - Backend may return structured errors (ignored)
- **No timeout handling** - Hangs indefinitely on slow networks

---

### Router Guards (`src/router/index.ts`)

**Pattern:**
```typescript
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  const userStore = useUserStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login');
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/home');
  } else {
    try {
      await userStore.fetchCurrentUser(); // May throw
      next();
    } catch (error) {
      if (error.status === 401) {
        authStore.logout();
        next('/login');
      } else {
        console.error('Route guard error:', error);
        next(); // Proceeds despite error!
      }
    }
  }
});
```

**Issues:**
- **Inconsistent error handling** - 401 redirects to login, all other errors proceed
- **Silent failures** - Non-401 errors allow navigation but leave user in broken state
- **No loading state** - User sees blank screen during `fetchCurrentUser()`
- **No retry on network errors** - Temporary network blip = broken app state

---

### Component Error Handling

**LoginView.vue (inferred):**
```typescript
async handleLogin() {
  this.loading = true;
  try {
    await authStore.login(this.username, this.password);
    this.$router.push('/home');
  } catch (error) {
    // What happens here? Unclear from architecture docs
    // Likely: error displayed but how?
  } finally {
    this.loading = false;
  }
}
```

**Issues:**
- **No error state management** - `this.loading` exists, but `this.error`?
- **Unknown user feedback** - How are errors displayed? Snackbar? Inline message?
- **No error differentiation** - "Wrong password" vs "Server down" same UX?

---

## 2. Error Recovery Paths

### Current Recovery Mechanisms

| Error Type | Detection | Recovery Path | User Impact |
|------------|-----------|---------------|-------------|
| 401 Unauthorized | Router guard checks `error.status === 401` | `authStore.logout()` + redirect to `/login` | ✅ Forced logout, clear feedback |
| Network failure | **Not detected** | **No recovery** | ❌ App hangs or silent failure |
| 500 Server error | **Not differentiated** | **No recovery** | ❌ Generic error, no retry |
| MFA required | Checked in login response | Sets `mfaRequired = true`, shows MFA step | ✅ Correct flow |
| Token expired | **Not explicitly handled** | **No auto-refresh trigger** | ❌ User sees API errors until manual logout |
| Validation errors (400) | **Not detected** | **No recovery** | ❌ Generic error message |

### Missing Recovery Paths

1. **Token Refresh Failure**
   - **Current:** Throws error, app breaks
   - **Should:** Auto-logout + redirect to login with message "Session expired"

2. **Network Timeout**
   - **Current:** Indefinite hang
   - **Should:** Timeout after 30s, show "Check your connection" + retry button

3. **MFA Code Invalid**
   - **Current:** Generic error
   - **Should:** Clear MFA input, show "Invalid code. X attempts remaining"

4. **Concurrent Logout (Multiple Tabs)**
   - **Current:** Other tabs show API errors
   - **Should:** Listen to localStorage changes, sync logout across tabs

---

## 3. User-Facing Error Messages

### Current Approach

**Auth Store Errors:**
```typescript
catch (error) {
  console.error('Login failed:', error);
  throw error; // Raw backend error object
}
```

**Component Consumption (assumed):**
```typescript
catch (error) {
  this.errorMessage = error.message; // Displays backend error directly
}
```

### Problems

| Backend Response | User Sees | Should See |
|------------------|-----------|------------|
| `{ error: "invalid_credentials" }` | "invalid_credentials" | "Incorrect username or password" |
| `{ error: "Network request failed" }` | "Network request failed" | "Connection lost. Check your internet." |
| `{ error: "Internal server error" }` | "Internal server error" | "Something went wrong. Try again later." |
| `{ error: "mfa_token_expired" }` | "mfa_token_expired" | "MFA code expired. Start over." |
| `503 Service Unavailable` | (Unknown - app may crash) | "Service temporarily unavailable. Retry in a moment." |

### Recommended Error Message Mapping

```typescript
// In apiHelper.ts or auth store
function getUserMessage(error: any): string {
  // Network errors
  if (error.message?.includes('fetch') || error.message?.includes('network')) {
    return 'Connection lost. Check your internet and try again.';
  }

  // HTTP status codes
  if (error.status === 401) {
    return 'Incorrect username or password.';
  }
  if (error.status === 403) {
    return 'Access denied.';
  }
  if (error.status === 429) {
    return 'Too many attempts. Please wait before trying again.';
  }
  if (error.status >= 500) {
    return 'Service temporarily unavailable. Try again later.';
  }

  // Veoci-specific error codes (if backend returns them)
  if (error.code === 'mfa_required') {
    return 'Multi-factor authentication required.';
  }
  if (error.code === 'mfa_invalid') {
    return 'Invalid MFA code. Please try again.';
  }
  if (error.code === 'account_locked') {
    return 'Account locked due to multiple failed attempts. Contact support.';
  }

  // Fallback
  return 'An unexpected error occurred. Please try again.';
}
```

---

## 4. Logging Patterns

### Current Logging

**Auth Store:**
```typescript
catch (error) {
  console.error('Login failed:', error);
  throw error;
}
```

**Router Guards:**
```typescript
catch (error) {
  console.error('Route guard error:', error);
  next(); // Continues despite error
}
```

### Issues

1. **No structured logging** - `console.error` loses context in production
2. **No error correlation** - Can't trace error across auth store → router → component
3. **No environment awareness** - Same logging in dev and prod (see Security L-1)
4. **No sanitization** - May log sensitive data (tokens, passwords if error contains them)

### Recommended Logging Strategy

```typescript
// services/logger.ts
interface LogContext {
  userId?: string;
  action: string;
  component: string;
  timestamp: number;
  environment: 'dev' | 'prod';
}

function logError(error: any, context: LogContext) {
  const sanitizedError = {
    message: error.message,
    status: error.status,
    code: error.code,
    // NEVER log: tokens, passwords, full request bodies
  };

  if (import.meta.env.MODE === 'development') {
    console.error('[ERROR]', context, sanitizedError, error); // Full error in dev
  } else {
    console.error('[ERROR]', context, sanitizedError); // Sanitized in prod
    // Send to error tracking service (Sentry, Rollbar, etc.)
    // sendToErrorTracking(sanitizedError, context);
  }
}

// Usage in auth store:
catch (error) {
  logError(error, {
    action: 'login',
    component: 'auth-store',
    userId: this.username, // Only username, not password
    timestamp: Date.now(),
    environment: import.meta.env.MODE
  });
  throw transformError(error); // Throw user-friendly error
}
```

---

## 5. Debuggability

### Current State

**Debugging Features:**
- ✅ DebugView.vue exists (line 23 in architecture.md)
- ✅ VeociJS SDK exposed on `window.veociApi` in dev mode (Security C-3)
- ✅ Pinia devtools integration (Vue DevTools)

**Debugging Challenges:**
1. **Opaque errors** - Generic "Login failed" doesn't indicate root cause
2. **Lost error context** - Error thrown in VeociJS, logged in auth store, displayed in component (context lost)
3. **No request/response logging** - Can't see what was sent to API
4. **No error history** - Single failed login = lost forever (no error list)

### Recommended Debugging Enhancements

**1. Request/Response Interceptor**
```typescript
// services/api-client.ts (VeociJS wrapper)
if (import.meta.env.MODE === 'development') {
  veociClient.interceptors.request.use(request => {
    console.log('[API Request]', {
      method: request.method,
      url: request.url,
      headers: request.headers, // Careful: may contain token
      body: request.body
    });
    return request;
  });

  veociClient.interceptors.response.use(
    response => {
      console.log('[API Response]', {
        status: response.status,
        url: response.url,
        data: response.data
      });
      return response;
    },
    error => {
      console.error('[API Error]', {
        status: error.status,
        url: error.config?.url,
        message: error.message,
        response: error.response?.data
      });
      return Promise.reject(error);
    }
  );
}
```

**2. Error History Store**
```typescript
// store/errors.ts
export const useErrorStore = defineStore('errors', {
  state: () => ({
    history: [] as Array<{
      timestamp: number;
      message: string;
      context: any;
      error: any;
    }>
  }),
  actions: {
    logError(message: string, context: any, error: any) {
      this.history.push({
        timestamp: Date.now(),
        message,
        context,
        error: import.meta.env.MODE === 'development' ? error : sanitize(error)
      });
      // Keep last 50 errors only
      if (this.history.length > 50) {
        this.history.shift();
      }
    }
  }
});

// DebugView.vue can display this history
```

**3. Enhanced DebugView**
```vue
<!-- DebugView.vue -->
<template>
  <div>
    <h2>Error History</h2>
    <div v-for="err in errorStore.history" :key="err.timestamp">
      <strong>{{ new Date(err.timestamp).toISOString() }}</strong>
      {{ err.message }}
      <details>
        <summary>Details</summary>
        <pre>{{ JSON.stringify(err, null, 2) }}</pre>
      </details>
    </div>

    <h2>Auth State</h2>
    <pre>{{ authStore.$state }}</pre>

    <h2>VeociJS SDK</h2>
    <button @click="testConnection">Test API Connection</button>
  </div>
</template>
```

---

## 6. Critical Gaps Summary

### Gap 1: No Error Classification
**Impact:** All errors treated identically, no context-specific recovery
**Location:** All try/catch blocks
**Fix:**
```typescript
class AppError extends Error {
  constructor(
    public code: string,
    public userMessage: string,
    public originalError?: any,
    public retryable: boolean = false
  ) {
    super(userMessage);
  }
}

// Usage:
catch (error) {
  if (error.status === 401) {
    throw new AppError('AUTH_FAILED', 'Incorrect credentials', error, false);
  } else if (error.message.includes('network')) {
    throw new AppError('NETWORK_ERROR', 'Connection lost', error, true);
  } else {
    throw new AppError('UNKNOWN', 'Something went wrong', error, false);
  }
}
```

### Gap 2: No Timeout Handling
**Impact:** App hangs on slow networks
**Location:** `apiHelper.ts`, all fetch calls
**Fix:**
```typescript
export async function callApi(endpoint: string, options: RequestOptions, timeout = 30000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(endpoint, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error.name === 'AbortError') {
      throw new AppError('TIMEOUT', 'Request timed out', error, true);
    }
    throw error;
  }
}
```

### Gap 3: No Cross-Tab Logout Sync
**Impact:** Multiple tabs show inconsistent auth state
**Location:** Auth store
**Fix:**
```typescript
// In auth store setup
if (typeof window !== 'undefined') {
  window.addEventListener('storage', (event) => {
    if (event.key === 'authToken' && event.newValue === null) {
      // Another tab logged out
      this.$reset(); // Clear store
      router.push('/login');
    }
  });
}
```

### Gap 4: No Retry Logic
**Impact:** Transient network errors = permanent failure
**Location:** All API calls
**Fix:**
```typescript
async function retryableRequest(
  fn: () => Promise<any>,
  maxRetries = 3,
  delayMs = 1000
): Promise<any> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (!error.retryable || i === maxRetries - 1) {
        throw error;
      }
      await new Promise(resolve => setTimeout(resolve, delayMs * Math.pow(2, i))); // Exponential backoff
    }
  }
}

// Usage in auth store:
await retryableRequest(() => veociApi.login(username, password));
```

---

## 7. Recommendations by Priority

### Critical (Implement Immediately)

1. **Add Error Classification**
   - File: `src/types/errors.ts`
   - Create `AppError` class with codes, user messages, retryability
   - Transform all caught errors to `AppError` instances

2. **Add Timeout Handling**
   - File: `src/services/apiHelper.ts`
   - Wrap all fetch calls with `AbortController` timeout
   - Default: 30 seconds

3. **Add User Message Mapping**
   - File: `src/utils/errorMessages.ts`
   - Map error codes/statuses to user-friendly messages
   - Use in all component error displays

4. **Add Cross-Tab Logout Sync**
   - File: `src/store/auth.ts`
   - Listen to localStorage changes
   - Auto-logout when another tab logs out

### High Priority

5. **Add Retry Logic**
   - File: `src/services/apiHelper.ts`
   - Implement exponential backoff for retryable errors
   - Max 3 retries for network errors

6. **Add Error History Store**
   - File: `src/store/errors.ts`
   - Log all errors with context
   - Display in DebugView

7. **Add Request/Response Logging**
   - File: `src/services/api-client.ts`
   - Dev-only interceptors
   - Log all API requests/responses

8. **Improve Router Guard Error Handling**
   - File: `src/router/index.ts`
   - Don't proceed on non-401 errors
   - Show error page or retry prompt

9. **Add Component Error States**
   - Files: All view components
   - Add `this.error` state alongside `this.loading`
   - Display errors consistently (Vuetify snackbar or alert)

### Medium Priority

10. **Sanitize Production Errors**
    - File: `src/utils/logger.ts`
    - Remove stack traces, sensitive data in prod
    - Keep full errors in dev

11. **Add Error Boundary (Vue ErrorCaptured)**
    - File: `App.vue`
    - Catch unhandled component errors
    - Display fallback UI instead of blank screen

12. **Add Session Expiry Handling**
    - File: `src/store/auth.ts`
    - Detect token expiry before API calls
    - Auto-refresh or prompt re-login

---

## 8. Code Examples

### Unified Error Handler

```typescript
// src/utils/errorHandler.ts
import { AppError } from '@/types/errors';
import { useErrorStore } from '@/store/errors';
import { getUserMessage } from '@/utils/errorMessages';

export function handleError(
  error: any,
  context: { action: string; component: string }
): AppError {
  const errorStore = useErrorStore();

  // Classify error
  let appError: AppError;
  if (error instanceof AppError) {
    appError = error;
  } else if (error.status === 401) {
    appError = new AppError('AUTH_FAILED', getUserMessage(error), error, false);
  } else if (error.name === 'AbortError' || error.message?.includes('network')) {
    appError = new AppError('NETWORK_ERROR', getUserMessage(error), error, true);
  } else if (error.status >= 500) {
    appError = new AppError('SERVER_ERROR', getUserMessage(error), error, true);
  } else {
    appError = new AppError('UNKNOWN', getUserMessage(error), error, false);
  }

  // Log error
  errorStore.logError(appError.userMessage, context, appError);

  // Production error reporting (if configured)
  if (import.meta.env.PROD && window.errorReporter) {
    window.errorReporter.captureException(appError);
  }

  return appError;
}

// Usage in auth store:
catch (error) {
  const appError = handleError(error, {
    action: 'login',
    component: 'auth-store'
  });
  throw appError; // Components receive AppError, not raw error
}
```

### Component Error Display

```vue
<!-- LoginView.vue -->
<template>
  <v-container>
    <v-alert v-if="error" type="error" dismissible @click:close="error = null">
      {{ error.userMessage }}
      <v-btn v-if="error.retryable" text @click="retry">Retry</v-btn>
    </v-alert>

    <v-form @submit.prevent="handleLogin">
      <!-- Login form fields -->
      <v-btn type="submit" :loading="loading">Login</v-btn>
    </v-form>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/store/auth';
import { AppError } from '@/types/errors';

const authStore = useAuthStore();
const loading = ref(false);
const error = ref<AppError | null>(null);

async function handleLogin() {
  loading.value = true;
  error.value = null;

  try {
    await authStore.login(username.value, password.value);
    router.push('/home');
  } catch (err) {
    if (err instanceof AppError) {
      error.value = err;
    } else {
      error.value = new AppError('UNKNOWN', 'An unexpected error occurred', err);
    }
  } finally {
    loading.value = false;
  }
}

function retry() {
  handleLogin();
}
</script>
```

---

## 9. Testing Error Handling

### Current State
**Unknown** - No test files mentioned in architecture docs

### Recommended Tests

```typescript
// tests/store/auth.spec.ts
import { setActivePinia, createPinia } from 'pinia';
import { useAuthStore } from '@/store/auth';
import { AppError } from '@/types/errors';

describe('Auth Store Error Handling', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('should throw AUTH_FAILED on 401', async () => {
    const authStore = useAuthStore();
    mockApi.login.mockRejectedValue({ status: 401 });

    await expect(authStore.login('user', 'pass')).rejects.toThrow(AppError);
    await expect(authStore.login('user', 'pass')).rejects.toMatchObject({
      code: 'AUTH_FAILED',
      retryable: false
    });
  });

  it('should throw NETWORK_ERROR on network failure', async () => {
    const authStore = useAuthStore();
    mockApi.login.mockRejectedValue(new TypeError('Failed to fetch'));

    await expect(authStore.login('user', 'pass')).rejects.toMatchObject({
      code: 'NETWORK_ERROR',
      retryable: true
    });
  });

  it('should retry on retryable errors', async () => {
    const authStore = useAuthStore();
    mockApi.login
      .mockRejectedValueOnce({ status: 503 }) // First call fails
      .mockResolvedValueOnce({ token: 'abc' }); // Second call succeeds

    await authStore.login('user', 'pass');
    expect(mockApi.login).toHaveBeenCalledTimes(2);
  });

  it('should clean up localStorage on logout error', async () => {
    const authStore = useAuthStore();
    authStore.authToken = 'abc';
    localStorage.setItem('authToken', 'abc');
    mockApi.logout.mockRejectedValue(new Error('Server error'));

    await authStore.logout();
    expect(localStorage.getItem('authToken')).toBeNull();
  });
});
```

---

## 10. Comparison to Best Practices

| Best Practice | Current Implementation | Gap |
|---------------|------------------------|-----|
| **Classify errors by type** | ❌ All errors generic | Need `AppError` class |
| **User-friendly messages** | ❌ Raw backend errors displayed | Need message mapping |
| **Retry transient failures** | ❌ No retry logic | Need exponential backoff |
| **Timeout long requests** | ❌ No timeout | Need `AbortController` |
| **Log with context** | ⚠️ Basic console.error | Need structured logging |
| **Sanitize production logs** | ❌ Same in dev/prod | Need environment check |
| **Global error boundary** | ❌ Not present | Need Vue ErrorCaptured |
| **Error state in components** | ⚠️ `loading` exists, `error` unclear | Need consistent pattern |
| **Cross-tab sync** | ❌ Not implemented | Need localStorage listener |
| **Error tracking service** | ❌ Not integrated | Optional: Sentry, Rollbar |

---

## Conclusion

The error handling is **functional but fragile**. It works for the happy path but breaks down under:
- Network instability
- Concurrent sessions (multiple tabs)
- Backend errors that aren't 401
- Slow API responses

**The system needs a unified error handling strategy** with:
1. Error classification (retryable vs fatal)
2. User-friendly messages
3. Automatic retries for transient failures
4. Timeouts to prevent hangs
5. Structured logging for debugging

**Before production:**
- Implement Critical recommendations (1-4)
- Add error state to all components
- Test error scenarios (network failure, timeout, 500 errors)
- Add error boundary to catch unhandled errors

---

## File References

Analysis based on:
- `/home/w3surf/.claude/cache/construct/veoci-app-template-construct/architecture.md`
- `/home/w3surf/.claude/cache/construct/veoci-app-template-construct/security-findings.md`
- User-provided context about auth store, API helper, router guards

Specific line references:
- L306-322: Auth store state and actions
- L255-284: Service layer architecture
- L189-206: Router guard logic
- L444-464: Token lifecycle (affects error recovery)

---

Wake up, Neo.
