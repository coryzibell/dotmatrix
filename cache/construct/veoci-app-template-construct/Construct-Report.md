# Project Review: veoci-app-template-construct

**Generated:** 2025-11-27
**Repository:** [Veoci-Labs/veoci-app-template-construct](https://github.com/Veoci-Labs/veoci-app-template-construct)
**Reviewed by:** Neo + Identities
**Platform:** Vue 3 + Vuetify 3 + Pinia + Rsbuild + TypeScript

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Findings](#findings)
   - [Blockers](#blockers)
   - [Security](#security)
   - [Developer Experience](#developer-experience)
   - [Testing](#testing)
   - [CI/CD](#cicd)
   - [Dependencies](#dependencies)
4. [Perspectives](#perspectives)
5. [Recommendations](#recommendations)
6. [Issues Created](#issues-created)
7. [Appendix: Methodology](#appendix-methodology)

---

## Executive Summary

**veoci-app-template-construct** is a **production-grade Vue 3 template** for building Veoci-integrated applications. It provides comprehensive authentication (including MFA support), modern tooling, and a well-structured codebase.

### Overall Assessment

| Category | Status | Summary |
|----------|--------|---------|
| **Architecture** | ✅ Good | Clean layered structure, proper separation of concerns |
| **Security** | ⚠️ Needs Documentation | localStorage JWT is acceptable with documented tradeoffs |
| **Developer Experience** | ❌ Blocked | Missing .env.example prevents first-run success |
| **Testing** | ❌ Missing | 0% coverage, no test framework installed |
| **CI/CD** | ❌ Missing | No GitHub Actions workflows |
| **Documentation** | ⚠️ Gaps | Architecture clear, but setup instructions incomplete |

### Key Finding

The template is caught between two identities:
- **Minimal starter** (expects you to add tests, CI/CD, security hardening)
- **Comprehensive boilerplate** (ships with 300-line auth store, MFA flows)

This creates confusion. Many audit "issues" are actually appropriate for a template's role (per Spoon's reframing), but the **developer onboarding blockers are genuine**.

### Verdict: **Iterate**

Fix the blockers before sharing externally. Document the intentional gaps.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                               │
├─────────────────────────────────────────────────────────────┤
│  Vue 3 Application                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Views     │  │ Components  │  │   Router    │         │
│  │  (Pages)    │  │   (UI)      │  │  (Guards)   │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Pinia Stores                        │   │
│  │  ┌─────────────┐  ┌─────────────┐                   │   │
│  │  │ Auth Store  │  │ User Store  │                   │   │
│  │  │ (300 lines) │  │  (minimal)  │                   │   │
│  │  └──────┬──────┘  └─────────────┘                   │   │
│  └─────────┼───────────────────────────────────────────┘   │
│            ▼                                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Services                           │   │
│  │  ┌─────────────┐  ┌─────────────┐                   │   │
│  │  │ API Client  │  │  VeociJS    │                   │   │
│  │  │  (axios)    │  │    SDK      │                   │   │
│  │  └──────┬──────┘  └──────┬──────┘                   │   │
│  └─────────┼────────────────┼──────────────────────────┘   │
│            └────────────────┘                               │
│                     │                                       │
├─────────────────────┼───────────────────────────────────────┤
│              Dev Proxy (Rsbuild)                            │
│   /api/v1/* → VEOCI_API_URL    /auth/* → VEOCI_API_URL     │
└─────────────────────┼───────────────────────────────────────┘
                      ▼
              ┌───────────────┐
              │  Veoci API    │
              │   Server      │
              └───────────────┘
```

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| Auth Store | `src/store/auth.ts` | Login, logout, token refresh, MFA (300 lines) |
| Router Guards | `src/router/index.ts` | Protect routes, redirect unauthenticated |
| API Client | `src/services/api-client.ts` | VeociJS SDK initialization |
| Dev Proxy | `rsbuild.config.ts` | Forward API calls, handle CORS |
| Login Flow | `src/views/login/*.vue` | Multi-step authentication UI |

---

## Findings

### Blockers

Issues that prevent developers from using the template effectively.

#### B-1: No .env.example
**Severity:** Critical
**Impact:** Developers cannot run the template without guessing configuration

The template requires `VEOCI_API_URL` but:
- No `.env.example` file exists
- Dev server starts successfully even with missing config
- First API call fails with confusing CORS/network errors

**Fix:** Create `.env.example`, add validation to `rsbuild.config.ts`
**GitHub Issue:** [#1](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/1)

#### B-2: Duplicate ESLint Configuration
**Severity:** Medium
**Impact:** Developer confusion

Both `.eslintrc.cjs` AND `eslint.config.js` exist. ESLint 9 uses flat config only.

**Fix:** Remove `.eslintrc.cjs`
**GitHub Issue:** [#2](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/2)

#### B-3: Package Name Mismatch
**Severity:** Medium
**Impact:** Confusion about template identity

`package.json` says `"name": "veoci-cardwall"` but this is a generic template.

**Fix:** Rename to `veoci-app-template`
**GitHub Issue:** [#3](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/3)

#### B-4: Unused dotenv Dependency
**Severity:** Low
**Impact:** Bundle bloat, developer confusion

`dotenv` is listed but never imported. It's a Node.js package that does nothing in browser code.

**Fix:** Remove dependency
**GitHub Issue:** [#4](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/4)

---

### Security

#### S-1: JWT Storage in localStorage
**Severity:** Context-dependent
**Source:** Cypher (audit), Spoon (reframe)

Auth tokens stored in localStorage are vulnerable to XSS attacks. However:
- This may be correct if Veoci API doesn't support httpOnly cookies
- Template has no control over backend auth mechanism
- XSS risk may be accepted for simplicity in a starting template

**Recommendation:** Document the tradeoff, don't change the code
**GitHub Issue:** [#5](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/5)

#### S-2: Client-Side JWT Decode
**Severity:** Low (if used correctly)
**Source:** Cypher

`jwt-decode` doesn't validate signatures. Safe for UI hints (display name, expiry), problematic if used for authorization.

**Recommendation:** Add warning comment
**GitHub Issue:** [#6](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/6)

---

### Developer Experience

#### Clone-to-Running Time

| Scenario | Current | Target |
|----------|---------|--------|
| With Veoci credentials | 30-60 min (guessing config) | 5 min |
| Without credentials | **Blocked** | 5 min (mock mode) |

#### Key DX Gaps

1. **No first-run guidance** - Developer sees login, has no credentials
2. **Silent config failures** - Missing VEOCI_API_URL causes confusing errors
3. **Debug view underutilized** - Doesn't show config status or connection test

**GitHub Issues:** [#1](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/1), [#9](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/9)

---

### Testing

**Current State:** 0% coverage, no test framework

| Aspect | Status |
|--------|--------|
| Test framework | ❌ Not installed |
| Unit tests | ❌ None |
| Integration tests | ❌ None |
| E2E tests | ❌ None |

**Spoon's Reframe:** Testing placeholder code in a template is cargo cult. BUT: test infrastructure setup IS valuable. One example test showing VeociJS mocking patterns would help.

**Recommendation:** Install Vitest, add ONE example test
**GitHub Issue:** [#7](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/7)

---

### CI/CD

**Current State:** No GitHub Actions workflows

| Aspect | Status |
|--------|--------|
| PR validation | ❌ None |
| Lint checks | ❌ None |
| Type checks | ❌ None |
| Build verification | ❌ None |
| Deployment | ❌ None |

**Spoon's Reframe:** Deployment automation should be project-specific. BUT: basic quality gates (lint, type-check, build) are universal.

**Recommendation:** Add basic CI workflow for PR validation
**GitHub Issue:** [#8](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/8)

---

### Dependencies

| Issue | Package | Action |
|-------|---------|--------|
| Unused | `dotenv` | Remove |
| Outdated | `axios` (1.9.0 → 1.13.2) | Update |
| Outdated | `eslint` (9.27.0 → 9.39.1) | Update |
| Outdated | `@rsbuild/core` (1.3.15 → 1.6.9) | Update |
| Large | `@mdi/font` (~600KB) | Consider `@mdi/js` for tree-shaking |

---

## Perspectives

### Sati (Fresh Eyes)
> *"This is production-grade, not minimal. That's both strength and weakness."*

The 300-line auth store is impressive but intimidating. New developers will struggle to understand the flow. Consider extracting MFA into a separate composable.

### Spoon (Reframing)
> *"We're applying application standards to a template."*

Key insight: Many "issues" are appropriate for a template's role. The real question is: **what IS this template's role?** Document the intentional gaps rather than filling them all.

### Oracle (Unseen Paths)
> *"The template is caught between being a platform and a snapshot."*

Without versioning, update strategy, and governance, the template becomes "useful once, then forgotten." The choice between platform vs snapshot hasn't been made.

Future possibilities:
- Extract to `@veoci/app-core` package
- Multi-template family (minimal, standard, enterprise)
- Template versioning with upgrade guides

---

## Recommendations

### Immediate (Do This Week)

| Priority | Action | Effort | Issue |
|----------|--------|--------|-------|
| 🔴 Critical | Create `.env.example` | 30 min | [#1](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/1) |
| 🔴 Critical | Remove duplicate ESLint config | 5 min | [#2](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/2) |
| 🔴 Critical | Fix package.json name | 30 min | [#3](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/3) |
| 🔴 Critical | Remove unused dotenv | 5 min | [#4](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/4) |

### Short-term (This Month)

| Priority | Action | Effort | Issue |
|----------|--------|--------|-------|
| 🟡 High | Document localStorage security tradeoff | 2 hrs | [#5](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/5) |
| 🟡 High | Add JWT decode warning comment | 30 min | [#6](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/6) |
| 🟡 High | Add Vitest with example test | 3 hrs | [#7](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/7) |
| 🟡 High | Add basic CI workflow | 1 hr | [#8](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/8) |
| 🟡 High | Enhance debug view | 2 hrs | [#9](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/9) |

### Medium-term (Discuss First)

| Priority | Action | Discussion |
|----------|--------|------------|
| 🔵 Medium | Add mock API mode (MSW) | [#10](https://github.com/Veoci-Labs/veoci-app-template-construct/discussions/10) |
| 🔵 Medium | Clarify template identity | [#11](https://github.com/Veoci-Labs/veoci-app-template-construct/discussions/11) |

---

## Issues Created

### GitHub Issues (9)

| # | Title | Labels |
|---|-------|--------|
| [#1](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/1) | Add .env.example with required environment variables | blocker, dx, identity:smith |
| [#2](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/2) | Remove duplicate ESLint configuration | blocker, dx, identity:smith |
| [#3](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/3) | Fix package.json name to reflect template purpose | blocker, dx, identity:smith |
| [#4](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/4) | Remove unused dotenv dependency | blocker, dx, identity:smith |
| [#5](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/5) | Document localStorage JWT security tradeoff | security, documentation, identity:morpheus |
| [#6](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/6) | Add security comment for client-side JWT decode | security, P2, identity:smith |
| [#7](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/7) | Add Vitest testing infrastructure with example test | enhancement, reliability, identity:deus |
| [#8](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/8) | Add basic CI workflow for PR validation | enhancement, infrastructure, identity:niobe |
| [#9](https://github.com/Veoci-Labs/veoci-app-template-construct/issues/9) | Enhance debug view with configuration diagnostics | enhancement, dx, identity:smith |

### GitHub Discussions (2)

| # | Title | Category |
|---|-------|----------|
| [#10](https://github.com/Veoci-Labs/veoci-app-template-construct/discussions/10) | Add mock API mode for development | Ideas |
| [#11](https://github.com/Veoci-Labs/veoci-app-template-construct/discussions/11) | Clarify template identity: minimal vs comprehensive | Ideas |

---

## Appendix: Methodology

### Construct Path

The Construct path is a multi-phase code review methodology using specialized identities:

| Phase | Identity | Focus |
|-------|----------|-------|
| 1 | Architect | System structure and data flows |
| 2 | Morpheus | Documentation gaps |
| 3 | Persephone | User experience and tone |
| 4 | Deus | Test coverage and quality |
| 5 | Cypher | Security vulnerabilities |
| 6 | Health Checks | Dependencies, CI/CD, errors, auth, DevEx |
| 7 | Perspectives | Fresh eyes, reframing, alternatives |
| 8 | Neo | Synthesis and prioritization |

### Identities Consulted

| Identity | Role | Key Contribution |
|----------|------|------------------|
| **Architect** | System design | Architecture diagram, component map |
| **Morpheus** | Documentation | Identified .env.example gap |
| **Persephone** | UX review | Login flow complexity, loading states |
| **Deus** | Testing | 0% coverage analysis, Vitest recommendation |
| **Cypher** | Security | localStorage XSS, JWT decode risks |
| **Apoc** | Dependencies | Unused dotenv, outdated packages |
| **Niobe** | CI/CD | No pipelines, comprehensive workflow design |
| **Keymaker** | Auth patterns | Token lifecycle review |
| **Seraph** | DevEx | Clone-to-running analysis |
| **Trinity** | Error handling | Error pattern documentation |
| **Sati** | Fresh eyes | "Production-grade, not minimal" |
| **Spoon** | Reframing | "Template standards vs app standards" |
| **Oracle** | Alternatives | Platform vs snapshot decision |

### Output Files

All construct outputs stored in:
```
~/.matrix/cache/construct/veoci-app-template-construct/
├── architecture.md
├── docs-recommendations.md
├── ux-recommendations.md
├── test-recommendations.md
├── security-findings.md
├── dependencies.md
├── cicd-review.md
├── error-handling.md
├── auth-review.md
├── devex-review.md
├── perspective-sati.md
├── perspective-spoon.md
├── perspective-oracle.md
├── synthesis.md
└── issues/
    ├── 001-blocker-env-example.yaml
    ├── ...
    └── 011-idea-template-identity.yaml
```

---

*Generated by the Construct methodology. Wake up, Neo.*
