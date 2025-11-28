# Dependency Analysis: veoci-app-template-construct

**Analysis Date:** 2025-11-27
**Identity:** Apoc

---

## Executive Summary

**Critical Issues:** 1
**Warnings:** 4
**Info:** 3

### Key Findings
- **dotenv in client-side code** - Security/architectural concern
- **Multiple outdated packages** - Potential bug fixes and features missed
- **No vulnerabilities detected** in currently specified versions (based on known CVEs as of Jan 2025)
- **Version ranges look healthy** - No obvious peer dependency conflicts

---

## 1. Outdated Packages

### Production Dependencies

| Package | Current | Latest | Gap | Notes |
|---------|---------|--------|-----|-------|
| `vue` | ^3.5.13 | 3.5.25 | Minor | 12 patch releases behind - bug fixes available |
| `vuetify` | ^3.8.7 | 3.11.0 | Minor | Significant update - new components, fixes |
| `axios` | ^1.9.0 | 1.13.2 | Minor | 4 minor versions - includes security patches |
| `vue-router` | ^4.5.1 | 4.6.3 | Minor | 2 minor versions behind |
| `pinia` | ^3.0.2 | 3.0.4 | Patch | 2 patch releases |
| `qs` | ^6.14.0 | Current | ✓ | Up to date |
| `jwt-decode` | ^4.0.0 | Current | ✓ | Likely current |
| `vue3-password-strength-meter` | ^1.7.9 | Unknown | ? | Check manually |
| `@mdi/font` | ^7.4.47 | Unknown | ? | Icon library - check for latest |

### Development Dependencies

| Package | Current | Latest | Gap | Notes |
|---------|---------|--------|-----|-------|
| `typescript` | ^5.8.3 | 5.9.3 | Minor | 1 minor version behind |
| `eslint` | ^9.27.0 | 9.39.1 | Minor | 12 minor versions - important linting improvements |
| `prettier` | ^3.5.3 | 3.6.2 | Minor | 1 minor version behind |
| `@rsbuild/core` | ^1.3.15 | 1.6.9 | Minor | Significant updates to build tool |
| `@rsbuild/plugin-sass` | ^1.3.1 | Unknown | ? | Check against @rsbuild/core version |
| `@rsbuild/plugin-vue` | ^1.0.7 | Unknown | ? | Check against @rsbuild/core version |
| `@typescript-eslint/*` | ^8.32.1 | Current | ✓ | Recent version |
| `lint-staged` | ^16.0.0 | Current | ✓ | Up to date |
| `husky` | ^9.1.7 | Current | ✓ | Up to date |

**Recommendation:** Update all packages, especially:
1. **axios** (security patches)
2. **eslint** (12 versions behind - likely fixes)
3. **vuetify** (3 minor versions - component fixes)
4. **@rsbuild/core** (significant build improvements)

---

## 2. Known Vulnerabilities

Based on package versions and CVE database (as of Jan 2025):

**No critical vulnerabilities detected** in the specified version ranges.

### Notes:
- `axios` versions prior to 1.6.0 had prototype pollution issues - **current ^1.9.0 is safe**
- `vue` 3.x is generally secure - no recent CVEs
- Run `npm audit` after `npm install` to verify current state

### Recommended Actions:
```bash
npm audit
npm audit fix  # Apply automatic fixes
npm audit fix --force  # For breaking changes (review carefully)
```

---

## 3. Unnecessary Dependencies

### 🚨 CRITICAL: `dotenv` in Client-Side Code

**Package:** `dotenv ^16.5.0`
**Issue:** This is a **Node.js** environment variable loader. It has **no effect** in browser/client-side code.

**Why it's a problem:**
1. **Adds ~40KB to bundle** for no benefit
2. **Misleading** - developers may think `.env` files work client-side
3. **Security risk** - may encourage exposing secrets in client build
4. **Build-time vs Runtime confusion**

**What happens:**
- Rsbuild/Vite inject env vars at **build time** via `import.meta.env`
- `dotenv` tries to load `.env` files at **runtime** in Node.js
- In browser, `dotenv` does nothing but waste bytes

**Correct approach:**
```bash
# Remove dotenv
npm uninstall dotenv

# Use Rsbuild's built-in env handling
# .env file:
VITE_API_URL=https://api.example.com

# Access in code:
const apiUrl = import.meta.env.VITE_API_URL
```

**Action:** Remove `dotenv` from dependencies.

---

### Potentially Redundant: `@mdi/font`

**Package:** `@mdi/font ^7.4.47`
**Issue:** Vuetify 3.x includes Material Design Icons via `mdi-svg` by default

**Check:**
- If using `<v-icon>mdi-home</v-icon>` - you need this
- If using `<v-icon icon="mdi-home" />` - Vuetify handles it
- If using custom icon set - this may be unnecessary

**Size impact:** ~600KB (full icon font)

**Optimization:**
```typescript
// Use tree-shakeable SVG icons instead
import { mdiAccount, mdiHome } from '@mdi/js'

// Vuetify config
import { aliases, mdi } from 'vuetify/iconsets/mdi-svg'

export default createVuetify({
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: { mdi }
  }
})
```

**Action:** Review icon usage. Consider switching to `@mdi/js` for tree-shaking.

---

## 4. Version Conflicts

### Peer Dependency Analysis

**No conflicts detected**, but verify these after updates:

| Package | Peer Dependencies | Status |
|---------|-------------------|--------|
| `vuetify ^3.8.7` | vue ^3.4.0 | ✓ Compatible (3.5.13) |
| `vue-router ^4.5.1` | vue ^3.2.0 | ✓ Compatible |
| `pinia ^3.0.2` | vue ^3.4.0 | ✓ Compatible |
| `@rsbuild/plugin-vue` | @rsbuild/core 1.x | ✓ Compatible (1.3.15) |
| `eslint-plugin-vue` | eslint ^9.0.0, vue ^3.0.0 | ✓ Compatible |

**After updating to latest:**
- `vuetify 3.11.0` requires `vue ^3.4.0` - current 3.5.13 → 3.5.25 is fine
- `@rsbuild/core 1.6.9` - verify plugin versions are compatible

---

## 5. Missing Peer Dependencies

**All required peers appear satisfied.**

### Recommendations:
Run after updates:
```bash
npm ls
# Look for "UNMET PEER DEPENDENCY" warnings
```

If you see warnings, install the missing peers or adjust versions.

---

## 6. Dependency Health Metrics

### Bundle Size Estimates (Production)

| Category | Estimated Size | Notes |
|----------|----------------|-------|
| Vue core | ~130KB | vue + vue-router + pinia |
| Vuetify | ~280KB | Component library + styles |
| Axios | ~40KB | HTTP client |
| @mdi/font | ~600KB | **Optimize this** |
| Other | ~50KB | jwt-decode, qs, password meter |
| **Total** | **~1.1MB** | Before tree-shaking/compression |

**After gzip:** ~300-400KB (typical 70% reduction)

### Optimization Opportunities:
1. **Remove dotenv** → -40KB
2. **Switch @mdi/font to @mdi/js** → -500KB (use only needed icons)
3. **Tree-shake Vuetify** → -100KB (import only used components)
4. **Code splitting** → Lazy load routes

**Target:** <200KB gzipped initial bundle

---

## 7. Recommended Actions

### Immediate (Critical)
```bash
# 1. Remove dotenv
npm uninstall dotenv

# 2. Update code that uses dotenv
# Change: require('dotenv').config()
# To: Use import.meta.env.VITE_* directly
```

### High Priority (Security/Stability)
```bash
# Update packages with important fixes
npm install axios@latest
npm install eslint@latest
npm install vue@latest vue-router@latest
npm install vuetify@latest
npm install @rsbuild/core@latest @rsbuild/plugin-vue@latest @rsbuild/plugin-sass@latest
```

### Medium Priority (Optimization)
```bash
# Evaluate icon strategy
npm uninstall @mdi/font
npm install @mdi/js

# Update Vuetify config to use mdi-svg (see section 3)
```

### Verification
```bash
npm audit
npm ls
npm outdated
npm run build  # Verify no breaking changes
npm run lint
```

---

## 8. Version Upgrade Strategy

### Safe Path (Recommended):
```bash
# 1. Update patch/minor versions first
npm update

# 2. Test thoroughly
npm run build
npm run lint
npm run test  # If tests exist

# 3. Update major versions individually
# (None needed - all major versions current)

# 4. Commit between each major update
git add package*.json
git commit -m "chore(deps): update to latest stable versions"
```

### Nuclear Option (If blocked):
```bash
# Delete and reinstall
rm -rf node_modules package-lock.json
npm install

# Then update
npm update
```

---

## 9. Maintenance Recommendations

### Ongoing:
1. **Monthly:** Run `npm outdated` and update patch versions
2. **Quarterly:** Review and update minor versions
3. **Set up Dependabot/Renovate:** Auto-PR for updates
4. **Pin versions in package-lock.json:** Commit lockfile for reproducibility

### Before Production Deploy:
```bash
npm audit
npm ls  # Check for conflicts
npm run build  # Verify build succeeds
```

---

## 10. Summary Table

| Issue | Severity | Package | Action |
|-------|----------|---------|--------|
| Unnecessary client-side dep | 🚨 Critical | dotenv | Remove |
| Outdated security patches | ⚠️ High | axios | Update to 1.13.2 |
| 12 versions behind | ⚠️ High | eslint | Update to 9.39.1 |
| Build tool updates | ⚠️ Medium | @rsbuild/core | Update to 1.6.9 |
| Large icon bundle | ℹ️ Info | @mdi/font | Optimize to @mdi/js |
| Minor updates available | ℹ️ Info | vue, vuetify, etc | Update to latest |

---

## Files Requiring Changes After dotenv Removal

**Search for dotenv usage:**
```bash
grep -r "dotenv" /path/to/veoci-app-template-construct/src
grep -r "process.env" /path/to/veoci-app-template-construct/src
```

**Replace with:**
```typescript
// Before:
import dotenv from 'dotenv'
dotenv.config()
const apiUrl = process.env.VUE_APP_API_URL

// After:
const apiUrl = import.meta.env.VITE_API_URL
```

**Rename env vars:**
```bash
# .env file
VUE_APP_API_URL → VITE_API_URL
VUE_APP_* → VITE_*
```

---

**End of Analysis**

*All weapons loaded and inspected. No critical failures. One weapon (dotenv) is inert and should be removed. Others require maintenance updates.*

---

**Location:** `/home/w3surf/.claude/cache/construct/veoci-app-template-construct/dependencies.md`
