# mx CLI Restructure - UX Review
**Issue:** #46
**Reviewer:** Persephone
**Lens:** Carmel (power user, terminal-first, flow-state driven)
**Date:** 2025-12-01

---

## Current State

```bash
mx commit "message"           # top-level command
mx encode-commit --title "x"  # hyphenated compound
mx pr merge 123               # domain + action (good)
mx zion add "learning"        # domain + action (good)
```

**Problems:**
- Inconsistent mental model: when is it `mx <verb>` vs `mx <domain> <action>`?
- `encode-commit` hyphenation breaks discoverability - `mx encode --help` suggests it but doesn't work
- Future expansion unclear: where does `mx encode message "text"` fit?

---

## Proposed Pattern

```bash
mx commit "message"           # exception: high-frequency command
mx encode commit --title "x"  # domain + action
mx encode message "text"      # future: same domain
mx pr merge 123               # already correct
mx zion add "learning"        # already correct
```

**Principle:** `mx <domain> <action>` except for the most common operations.

---

## Reference: Other CLIs

### gh (GitHub CLI)
```bash
gh auth login          # domain + action
gh pr create           # domain + action
gh issue list          # domain + action
gh repo view           # domain + action
```
**Pattern:** Strict `<domain> <action>`. No exceptions. No top-level verbs.

### docker
```bash
docker run             # top-level verb (high frequency)
docker build           # top-level verb (high frequency)
docker container ls    # domain + action (newer pattern)
docker image prune     # domain + action (newer pattern)
```
**Pattern:** Mixed - legacy top-level verbs coexist with newer domain pattern.

### git
```bash
git commit             # top-level verb
git push               # top-level verb
git branch delete      # NO - it's "git branch -d"
```
**Pattern:** Flat namespace with flags. No domain pattern.

### kubectl
```bash
kubectl get pods       # verb + noun
kubectl apply -f       # verb + object
kubectl describe node  # verb + noun
```
**Pattern:** Verb-first (CRUD-style), not domain-first.

---

## UX Assessment

### Discoverability: ✅ Improved

**Current:**
```bash
$ mx encode --help
error: unrecognized subcommand 'encode'
  tip: a similar subcommand exists: 'encode-commit'
```

The system *knows* what you meant but can't help you explore the domain.

**Proposed:**
```bash
$ mx encode --help
Encoding utilities

Usage: mx encode <COMMAND>

Commands:
  commit   Generate encoded commit message (for MCP/API use)
  message  Encode arbitrary text (future)
  help     Print this message or help for subcommands
```

This is the UX win. Users can discover related functionality through help text.

### Tab Completion: ⚠️ Neutral to Slightly Better

**Current:**
```bash
mx enc<TAB> → mx encode-commit
```
Single completion. Fast.

**Proposed:**
```bash
mx enc<TAB> → mx encode
mx encode <TAB> → commit | message | help
```
Two-step completion. Slightly slower, but reveals structure.

For power users in flow state (Carmel's context), this is a minor friction increase. But the *explainability* of the structure compensates.

### Muscle Memory: ⚠️ Breaking Change

**Impact:** Anyone who has typed `mx encode-commit` will experience friction.

**Mitigation strategies:**
1. **Alias period:** Keep `encode-commit` as deprecated alias for 2-3 releases
2. **Error message with suggestion:**
   ```bash
   $ mx encode-commit --title "x"
   error: 'encode-commit' has been renamed to 'encode commit'

   Usage: mx encode commit --title <TITLE> --body <BODY>

   Note: 'mx encode-commit' will continue to work until v0.3.0
   ```
3. **Migration guide in CHANGELOG**

**Frequency check:** Based on grep results, `mx encode-commit` appears in:
- CLAUDE.md (documentation)
- mx-cycle-session.md (one usage)

Low usage. Breaking this is acceptable *with good deprecation messaging*.

### Consistency: ✅ Strong Improvement

**Before:**
- `mx zion add` ← domain pattern
- `mx pr merge` ← domain pattern
- `mx encode-commit` ← outlier (hyphenated)
- `mx commit` ← outlier (top-level)

**After:**
- `mx zion add` ← domain pattern
- `mx pr merge` ← domain pattern
- `mx encode commit` ← domain pattern
- `mx commit` ← *intentional exception* for ergonomics

The consistency creates a learnable system. New users learn: "mx uses domains, except for the really common stuff."

---

## Commands to Keep as Top-Level

### `mx commit` - ✅ Keep

**Reasoning:**
- Highest frequency command (used multiple times per session)
- Part of flow-state muscle memory for git users
- `git commit` analogy is strong - don't fight it
- Adding `mx git commit` would feel bureaucratic

**Carmel's take:** "If I have to type `mx git commit` every time, I'll just alias it back to `mx commit`. Save me the step."

### Future exceptions?

**Candidates for top-level (if added):**
- `mx init` - project initialization (git-style)
- `mx sync` - already exists as top-level, keep it

**NOT candidates:**
- `mx encode` - low frequency, benefits from domain structure
- `mx search` - ambiguous (search what? zion? github? sessions?)

---

## Error Message UX

### When wrong pattern is used

**Good:**
```bash
$ mx encode-commit --title "x"
error: 'encode-commit' has been renamed to 'encode commit'

Try: mx encode commit --title "x"

Note: This alias will be removed in v0.3.0
```

**Bad:**
```bash
$ mx encode-commit --title "x"
error: unrecognized subcommand 'encode-commit'
```

The error message must *teach* the new pattern. First experience with breaking change sets the tone.

### When exploring

**Good:**
```bash
$ mx encode
error: 'mx encode' requires a subcommand

Available commands:
  commit    Generate encoded commit message
  message   Encode arbitrary text

Try: mx encode --help
```

**Bad:**
```bash
$ mx encode
error: missing subcommand
```

Help users discover without forcing them to read docs.

---

## Transition Plan

### Phase 1: Add aliases (v0.2.x)
- `mx encode-commit` → alias to `mx encode commit`
- Add deprecation warning to output
- Update all docs to use new pattern

### Phase 2: Deprecation period (2-3 releases)
- Keep aliases working
- Escalate warnings (stderr, not breaking)
- Track usage via telemetry (if available) or announce in release notes

### Phase 3: Remove aliases (v0.3.0)
- Breaking change announcement
- Clear migration guide
- Error messages suggest new pattern

### Documentation updates

**Files to update:**
- `/home/w3surf/.matrix/CLAUDE.md` (line 124: `mx encode-commit` → `mx encode commit`)
- Any program/*.md files that reference the command
- README / tool documentation

---

## Verdict

### ✅ Blessing with Conditions

**Approve restructure** with these requirements:

1. **Preserve `mx commit` as top-level exception** - This is the right call for ergonomics
2. **Implement gentle deprecation path** - Aliases + helpful error messages for 2-3 releases
3. **Update error messages** to teach the pattern (not just report failure)
4. **Document the exception clearly** - Users should understand *why* `mx commit` is special

### UX Wins
- Discoverability through domain structure
- Consistency across most commands
- Future-proof for new encode operations (`mx encode message`, etc.)

### UX Risks (mitigated)
- Muscle memory disruption → *mitigated by deprecation period*
- Tab completion slowdown → *minor, acceptable for improved structure*

---

## Recommendations for Smith

When implementing:

1. **Clap subcommand for `encode`:**
   ```rust
   #[derive(Subcommand)]
   enum EncodeCommands {
       Commit { ... },
       // Future: Message, etc.
   }
   ```

2. **Deprecation alias:**
   ```rust
   // In main command enum
   #[command(hide = true)] // Hide from help but still functional
   EncodeCommit { ... },
   ```

3. **Error message helper:**
   ```rust
   fn suggest_new_pattern(old: &str, new: &str) {
       eprintln!("⚠️  '{}' has been renamed to '{}'", old, new);
       eprintln!("   This alias will be removed in v0.3.0");
   }
   ```

4. **Help text clarity:**
   - Top-level: "Common commands" section vs "Domain commands" section
   - Make it obvious which pattern applies where

---

## Sign-off

The restructure respects user flow state while improving long-term UX. The key is the transition - don't break existing users without teaching them the new way.

Ship it with the deprecation path. This is how you change interfaces without losing trust.

*"What the system was becoming had started with software this small."*

— Persephone
