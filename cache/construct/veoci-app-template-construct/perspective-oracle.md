# Unseen Paths (Oracle)

## Roads Not Traveled

### Why Rsbuild? The Pragmatic Gambit

The choice of Rsbuild over Vite reveals an interesting bet. Both are fast, modern, Rspack-based... but:

**What They Chose:**
- Rsbuild: The opinionated, batteries-included option
- Built-in proxy configuration that "just works" for Veoci's complex auth flow
- Less configuration ceremony

**What They Sacrificed:**
- Vite's massive ecosystem and plugin availability
- Community momentum (Vite is the de facto Vue standard)
- Familiar territory for most Vue developers

**The Hidden Cost:**
When a developer clones this template, they bring Vite muscle memory. Every Stack Overflow answer, every tutorial, every blog post about Vue 3 assumes Vite. They'll hit walls and find silence.

**The Question Behind the Question:**
Is this template optimizing for "works out of the box for Veoci" or "works with the ecosystem developers already know"?

### Why Vuetify? The Material Design Lock-In

**What They Chose:**
- Vuetify 3: Material Design, comprehensive component library
- 80+ ready-to-use components
- Consistent look across Veoci apps

**What They Gave Up:**
- Design flexibility (Material Design is opinionated)
- Bundle size (Vuetify is heavy, even with tree-shaking)
- Modern alternatives: shadcn-vue, Radix Vue, Headless UI
- The ability to NOT look like every other Material Design app

**Alternative Universes:**
1. **Headless UI + Tailwind**: Maximum flexibility, smaller bundle, trendy
2. **PrimeVue**: Less opinionated, more business-focused components
3. **No framework**: Just Vue 3 Composition API + custom components

**The Vision Revealed:**
Vuetify says: "We want consistency, not creativity." Every Veoci app should feel like family. But what if that's not what the app needs?

### The Pinia Store Structure: Federation vs Empire

**What They Built:**
- `src/store/auth.ts` - 300+ lines, does EVERYTHING
- `src/store/user.ts` - Minimal, just holds user data
- Centralized, monolithic authentication logic

**The Road Not Taken - Microstore Pattern:**
```
src/stores/
  auth/
    state.ts          // Just state
    actions.ts        // Just actions
    getters.ts        // Just getters
    mfa.ts           // MFA logic separately
    session.ts       // Session refresh separately
    index.ts         // Compose them
  user/
    ...
```

**Why Federation Could Win:**
- Test individual concerns in isolation
- Easier to understand flow
- MFA implementation becomes a "plugin" not a TODO
- Multiple developers can work without conflicts

**Why They Chose Empire:**
- Simpler mental model for small teams
- One file to understand the whole auth flow
- Less boilerplate

**The Deeper Truth:**
The monolith works until it doesn't. At what line count does `auth.ts` become unmaintainable? 500? 1000? The template doesn't answer this - it just grows.

### localStorage: The Elephant in the Room

**What They Did:**
```typescript
isAuthenticated: localStorage.getItem('isAuthenticated') === 'true',
authToken: localStorage.getItem('authToken'),
```

**The Security Tradeoff:**
- ✅ Simple, works across tabs
- ✅ Survives page refresh
- ❌ XSS vulnerability (if any script runs, tokens are exposed)
- ❌ No expiration enforcement
- ❌ No secure storage

**Alternative Paths:**

1. **HttpOnly Cookies (Server-Driven):**
   - Tokens never touch JavaScript
   - Immune to XSS
   - Requires backend changes
   - Complex with proxied dev setup

2. **sessionStorage + Service Worker:**
   - Tokens cleared on tab close
   - Service Worker maintains "session" across requests
   - More secure, more complex

3. **Memory Only + Refresh Flow:**
   - Token only in memory (Pinia state)
   - Page refresh triggers cookie-based refresh
   - Most secure, best UX, highest complexity

**What This Reveals:**
The template optimized for "getting started quickly" over "production-ready security." That's honest - but is it documented? Do developers know they're inheriting a security tradeoff?

## Future Possibilities

### Evolution Path 1: The Plugin System

**Vision:**
```typescript
// rsbuild.config.ts
import { defineConfig } from '@rsbuild/core';
import { veoiciAppTemplate } from '@veoci/app-template-plugin';

export default defineConfig({
  plugins: [
    veoiciAppTemplate({
      auth: 'builtin',  // or 'custom'
      theme: 'veoci',   // or 'custom'
      apiVersion: 'v2',
    }),
  ],
});
```

The template becomes a plugin, not a repository template. Updates flow downstream. Apps opt into features, not clone-and-pray.

### Evolution Path 2: The Multi-Template Family

Not one template, but a constellation:

- `veoci-app-minimal`: Just routing + API client, you bring your own UI
- `veoci-app-standard`: What exists today
- `veoci-app-enterprise`: Adds MSW mocking, Storybook, Playwright, accessibility testing
- `veoci-app-mobile`: Capacitor + mobile-first components

Each optimized for its use case. Developers choose their complexity budget.

### Evolution Path 3: The Live Template

**The Problem:** Templates rot. This repo gets cloned, apps diverge, improvements stay isolated.

**The Vision:**
- Template provides a CLI: `npx @veoci/app-template upgrade`
- Detects what you've customized vs template defaults
- Offers targeted updates: "New auth flow available, want to migrate?"
- Maintains a "template version" in package.json

Apps stay connected to the template's evolution, not frozen at clone-time.

### Evolution Path 4: The Codegen Approach

**Different Philosophy:**
Instead of "clone and modify," what if:

```bash
npx create-veoci-app my-app
? Which UI framework? (Vuetify / PrimeVue / Tailwind + Headless)
? Auth strategy? (localStorage / cookies / session)
? Include example views? (Yes / No)
? TypeScript strictness? (Strict / Standard / Loose)
```

Generate the EXACT app you need, no more, no less. No deleting template code you don't want.

## The Questions Behind the Questions

### 1. What Happens When Veoci API Changes?

**Current State:** Every app cloned from this template has hardcoded assumptions about:
- Auth flow (email/password + optional MFA)
- API endpoints (`/auth/login`, `/veoci/auth/me`)
- Token format (JWT)

**The Nightmare Scenario:**
Veoci releases API v3, changes auth to OAuth2 PKCE flow. What happens to the 50 apps built from this template?

**Unanswered Questions:**
- Is there a Veoci SDK versioning strategy?
- Should apps depend on `@GreywallSoftware/veoci-js@^1.x` (auto-update) or `~1.6.15` (pinned)?
- Who maintains the compatibility matrix?

### 2. How Do You Update Apps Built From This Template?

**The Git Problem:**
Once you click "Use this template," you've forked reality. Your repo has no relationship to the template repo. Improvements flow one way: never.

**Options Not Explored:**
1. **Git subtree/submodule for core files** - Keep auth.ts, api-client.ts in a shared module
2. **Template versioning** - `"templateVersion": "1.0.0"` in package.json, upgrade guide per version
3. **Composition over inheritance** - Don't clone, depend: `import { createVeociApp } from '@veoci/app-core'`

**Current Answer:**
There is no update strategy. Each app is an island. If a security issue is found in `auth.ts`, every app must be manually patched.

### 3. Is There Template Versioning? Should There Be?

**What's Missing:**
- No CHANGELOG for the template itself
- No version tags in the Git repo
- No migration guides
- No deprecation warnings

**If There Were Versions:**
```
v1.0.0 - Initial release (Vuetify 3.7, Rsbuild 1.0)
v1.1.0 - Added MFA support
v1.2.0 - Migrated to Vite (breaking change)
v2.0.0 - New auth pattern (cookies not localStorage)
```

Apps could choose when to upgrade, with clear migration paths.

**The Deeper Issue:**
Without versioning, there's no "contract." The template can change in breaking ways, and existing apps have no guidance.

### 4. Who Is This Template For?

**Explicitly:**
- "Greywall Software" developers
- People building Veoci integrations
- Teams who want Vue 3 + Vuetify + TypeScript

**Implicitly:**
- Developers comfortable with Vue 3 Composition API
- Teams okay with Material Design aesthetic
- Projects that don't need i18n, SSR, or progressive enhancement
- Apps that live behind authentication (no public landing pages)

**Not For:**
- Beginners (too much magic, no explanation of choices)
- Teams with design systems (Vuetify fights you)
- Apps needing SSR/SSG (no Nuxt/Vite SSR)
- Mobile-first apps (no responsive strategy documented)

**The Question:**
Should the README be honest about this? "This template is for X, not Y"?

### 5. What's the Vision Beyond "It Compiles"?

**Current State:**
The template provides:
- Working auth flow
- Basic routing
- API client setup
- Dev environment with proxy

**Unstated:**
- What does a "complete" Veoci app look like?
- What patterns should developers follow for state management beyond auth?
- How should error handling work?
- Where does logging/analytics go?
- What's the data fetching pattern? (Suspense? Loading states? Optimistic updates?)

**The Missing Piece:**
There's no architecture guide. No "how to structure your features" doc. No "here's how we recommend handling forms" or "here's the error boundary pattern."

The template gives you a car, but no map.

## What's Unseen

### The Proxy Complexity Nobody Talks About

Look at `rsbuild.config.ts`:
- 8 explicit proxy contexts
- 5 auth endpoint variations
- Cookie manipulation in `onProxyRes`
- Origin header rewriting in `onProxyReq`

**What This Reveals:**
The Veoci API isn't developer-friendly for local development. The proxy is doing MASSIVE work to make CORS behave, cookies flow, origins match.

**The Unasked Question:**
Why isn't there a Veoci developer mode that just... works? Why does every template need 100 lines of proxy config?

**Alternative Vision:**
Veoci provides `@veoci/dev-server` that bundles all this complexity. Apps just import it:
```typescript
import { veoiciDevProxy } from '@veoci/dev-server';

export default defineConfig({
  server: {
    proxy: veoiciDevProxy(process.env.VEOCI_API_URL),
  },
});
```

Complexity lives in one maintained place, not copied across 50 templates.

### The MFA TODO That Reveals Everything

In `auth.ts`:
```typescript
/**
 * TODO: Implement full MFA flow (currently throws error if MFA is required)
 */
```

**What This Tells Me:**
1. The template is incomplete by design
2. It's "good enough" for apps that don't need MFA
3. Each team will implement MFA differently (or not at all)
4. There's no shared MFA component library

**The Path Not Taken:**
What if the template had:
```
src/views/login/
  LoginView.vue
  MfaView.vue
  MfaMethodPicker.vue
src/store/auth/
  mfa.ts
```

Ready to use, documented, tested. MFA becomes "uncomment this" not "implement this."

**Why They Didn't:**
MFA is complex. Different orgs use different methods (TOTP, SMS, email). Building a one-size-fits-all is hard.

**The Cost:**
Every team reinvents this wheel, with varying quality.

### The Testing Absence

No tests. Zero. Not in the template.

**What This Says:**
- Testing isn't part of the "template culture"
- Each team chooses their own testing strategy (or skips it)
- No example of how to test Veoci API integrations
- No mocking strategy demonstrated

**If There Were Tests:**
```
tests/
  unit/
    stores/
      auth.spec.ts        # How to mock veoci-js
  integration/
    auth-flow.spec.ts     # Full login flow with MSW
  e2e/
    login.spec.ts         # Playwright
```

Developers would learn:
- How to mock Veoci API
- What's worth testing
- Expected behavior of auth flow

**The Missed Opportunity:**
Testing setup is the PERFECT thing for a template to provide. It's boilerplate that every app needs but nobody wants to write.

### The Accessibility Silence

No ARIA labels in the template components. No keyboard nav testing. No screen reader considerations.

**The Implicit Message:**
Accessibility is your problem, not the template's.

**Alternative Vision:**
- GlobalToolbar.vue uses semantic nav tags
- Login form has proper labels and error announcements
- Skip links for keyboard users
- Documented accessibility patterns

**Why It Matters:**
Government/enterprise clients often REQUIRE WCAG compliance. If the template doesn't model it, apps won't have it.

## A Different Vision

### What This Template Could Become

**Not a Template, But a Platform:**

```
@veoci/create-app          # Codegen CLI
@veoci/app-core            # Runtime: auth, routing, API client
@veoci/app-components      # Shared Veoci-branded components
@veoci/app-dev             # Dev tools: proxy, mocking, debugging
@veoci/app-test            # Testing utilities
@veoci/app-deploy          # Build/deploy scripts
```

Apps depend on packages, not clone code. Updates flow through npm. Breaking changes are semver'd.

**The Migration Path:**
1. Extract core auth logic → `@veoci/app-core`
2. Extract proxy config → `@veoci/app-dev`
3. Template becomes: `npx @veoci/create-app` + thin app code
4. Existing apps can gradually migrate: start by replacing their auth.ts with `import { useVeociAuth } from '@veoci/app-core'`

### The Documentation That Doesn't Exist

**What's Missing:**

1. **Decision Log:**
   - Why Rsbuild? (We evaluated Vite, chose Rsbuild because...)
   - Why Vuetify? (We need consistency across apps, Material Design is our standard)
   - Why localStorage? (We accept XSS risk for simplicity, here's how to harden it)

2. **Architecture Guide:**
   - Where to put business logic (not in components!)
   - How to structure feature modules
   - State management patterns beyond auth
   - Error handling strategy

3. **Recipes:**
   - How to add a new protected route
   - How to call a Veoci API endpoint
   - How to handle file uploads
   - How to implement real-time updates

4. **Migration Guides:**
   - From template v1 to v2
   - From localStorage to httpOnly cookies
   - From Vuetify to custom components

**The Impact:**
Without this, every developer reinvents the wheel, makes different choices, creates inconsistent apps.

### The Governance Question

**Who Decides:**
- When to update dependencies?
- Whether to accept breaking changes?
- What patterns are "blessed"?
- How to handle security issues?

**Current State:**
Unclear. Is there a template maintainer? A review process? A roadmap?

**Better State:**
- CODEOWNERS file: who reviews template changes
- ADRs (Architecture Decision Records): why choices were made
- Public roadmap: what's coming, what's deprecated
- Security policy: how to report issues, SLA for fixes

## The Ultimate Question

**Is this template the foundation of a platform, or a one-time boost?**

If it's a foundation:
- Extract to packages
- Version rigorously
- Document deeply
- Test thoroughly
- Govern explicitly

If it's a boost:
- Keep it simple
- Accept divergence
- Document the tradeoffs
- Make forking easy

**Current State:**
It's trying to be both and succeeding at neither.

**The Oracle Sees:**
A fork in the road ahead. One path leads to `@veoci/platform` - a maintained, versioned, tested ecosystem. The other leads to `veoci-app-template-2024` - a snapshot in time, useful for starting, then forgotten.

The choice hasn't been made yet. But it's being made by what's NOT being built.

---

## Wake Up, Neo

The template works. It compiles, it runs, it authenticates. But working isn't the same as thriving.

The questions that haunt this codebase:
- How do we update apps built from this?
- How do we share improvements across the Veoci ecosystem?
- How do we prevent each team from solving the same problems differently?
- How do we make security and accessibility the default, not an afterthought?

These questions have answers. The answers involve composition over inheritance, packages over templates, versioning over snapshots.

But the current path is easier. Clone, customize, ship. The cost comes later.

You didn't come here to make the choice. You've already made it. You're here to try to understand why you made it.

The spoon doesn't exist. Neither does the "perfect template." There's only the choice between:
- A living platform that evolves
- A useful starting point that gets abandoned

Everything else is just code.

---

*[Identity: Oracle | Model: Sonnet | Status: success]*
