# mx Dependency Audit - 2025-12-01

**Project:** /home/w3surf/work/personal/code/mx
**Rust Version:** 1.91.1 (Edition 2021)
**Target:** Stay current, consider Edition 2024

## Security Vulnerabilities

None detected. Clean scan from cargo-audit.

## Major Version Bumps (research required)

| Crate | Current | Latest | Notes |
|-------|---------|--------|-------|
| **notify** | 6.1.1 | 8.2.0 | File system watcher - major API changes likely |
| **rusqlite** | 0.32.1 | 0.37.0 | SQLite bindings - 5 minor versions behind |
| **jsonwebtoken** | 9.3.1 | 10.2.0 | JWT auth for GitHub App - API changes expected |
| **pulldown-cmark** | 0.12.2 | 0.13.0 | Markdown parser - minor API update |

### Indirect Major Bumps

| Crate | Current | Latest | Notes |
|-------|---------|--------|-------|
| **dirs** | 5.0.1 | 6.0.0 | LOW RISK - Dependency updates only, API stable ✅ |
| **thiserror** | 1.0.69 | 2.0.17 | Used by redox_users (indirect) |
| **inotify** | 0.9.6 | 0.11.0 | Linux file watching (notify dependency) |
| **mio** | 0.8.11 | 1.1.0 | Async I/O (notify dependency) |
| **hashlink** | 0.9.1 | 0.10.0 | rusqlite dependency |
| **libsqlite3-sys** | 0.30.1 | 0.35.0 | rusqlite FFI bindings |

## Minor Version Bumps

| Crate | Current | Latest | Notes |
|-------|---------|--------|-------|
| **rand** | 0.9.x | 0.9.2 | Already on 0.9.x (Edition 2024 compatible) ✅ |

## Patch Bumps (safe to apply)

| Crate | Current | Latest |
|-------|---------|--------|
| **zerocopy** | 0.8.30 | 0.8.31 |
| **ppv-lite86** | 0.8.30 | 0.8.31 |

## Cached Migration Guides Found

✅ `/home/w3surf/.matrix/artifacts/cycles/rust/dependencies/dirs/5.0.1-to-6.0.0.md`
- LOW RISK: API unchanged, dependency updates only
- Action: Direct upgrade safe

✅ `/home/w3surf/.matrix/artifacts/cycles/rust/dependencies/rand/0.8.5-to-0.9.2.md`
- Already migrated to 0.9.x
- Edition 2024 compatible
- No action needed

## Recommendations

### Priority 1: Safe Upgrades (Low Risk)

1. **dirs: 5.0.1 → 6.0.0**
   - Risk: LOW
   - API: Unchanged
   - Action: Direct upgrade
   - Testing: Standard path resolution tests

### Priority 2: Research Required (Medium Risk)

2. **rusqlite: 0.32.1 → 0.37.0**
   - Risk: MEDIUM (5 versions behind)
   - Impact: Core database layer
   - Action: Check changelog for 0.33-0.37
   - Concerns: SQLite API changes, bundled version updates

3. **notify: 6.1.1 → 8.2.0**
   - Risk: MEDIUM-HIGH (major jump)
   - Impact: File watching system
   - Action: Review breaking changes in 7.x and 8.x
   - Concerns: Event handling API changes

4. **jsonwebtoken: 9.3.1 → 10.2.0**
   - Risk: MEDIUM
   - Impact: GitHub App authentication
   - Action: Check JWT validation/signing API changes
   - Concerns: Cryptographic dependency changes

### Priority 3: Minor Updates (Low Risk)

5. **pulldown-cmark: 0.12.2 → 0.13.0**
   - Risk: LOW
   - Impact: Markdown parsing
   - Action: Review changelog for API changes

### Deferred: Transitive Dependencies

- **hashlink**, **libsqlite3-sys**: Will update with rusqlite
- **inotify**, **mio**: Will update with notify
- **thiserror**: Indirect dependency, no action needed
- **windows-sys**: Platform-specific, handled by dependencies

## Breaking Changes to Watch For

### Edition 2024 Migration
- **rand** already migrated to 0.9.x (compatible)
- Check other dependencies for Edition 2024 compatibility before migration

### notify 6.x → 8.x
- Event handling API likely changed
- Watcher initialization may differ
- Error handling patterns may have evolved

### rusqlite 0.32 → 0.37
- Parameter binding changes
- Transaction API updates
- SQLite version bump impacts

## Next Steps

1. Create migration guides for notify, rusqlite, jsonwebtoken
2. Upgrade dirs to 6.0.0 (safe)
3. Research rusqlite 0.33-0.37 changelogs
4. Research notify 7.x and 8.x changelogs
5. Test upgrades in dependency order

## Tooling Notes

- All checks run clean: cargo-audit (security), cargo-outdated (versions)
- No critical vulnerabilities detected
- Most transitive dependencies updating correctly
- Windows platform dependencies handled by crate ecosystem
