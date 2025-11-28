# Program: Reload

**Trigger:** "Reload", "Fix the issues", "Work through the backlog", "Execute on construct findings"

**Purpose:** Execute fixes for issues created during Broadcast. Neo orchestrates, identities implement, fixes are verified and closed.

**Input:** GitHub issues with `identity:*` labels (from Broadcast path)

**Output:** Closed issues, committed fixes

## Steps

### Phase 1: Select Issue
1. **Neo selects an issue** to work on:
   - By number: "Fix issue #33"
   - By priority: Start with blockers, then improvements
   - By label: "Fix all `identity:morpheus` issues"

2. **Neo reads the issue** - understand scope, acceptance criteria, which identity owns it

### Phase 2: Dispatch
3. **Neo dispatches the appropriate identity:**
   - Check the `identity:*` label for primary owner
   - Some issues need multiple identities (e.g., Architect designs → Smith implements)
   - Dispatch with full context from the issue body

   Example dispatch:
   ```
   Smith. Fix issue #33: Update Keymaker example in CLAUDE.md.

   Change the example task from "Review this auth flow for vulnerabilities"
   to "Implement JWT token refresh flow".

   File: ~/.claude/CLAUDE.md
   ```

4. **Identity executes** - implements the fix, reports back

### Phase 3: Verify
5. **Neo verifies the fix:**

   | Change Type | Verification | Who |
   |-------------|--------------|-----|
   | Code change | Run tests, check build | Deus |
   | Markdown/docs | Read and confirm accuracy | Neo |
   | Config change | Verify it works | Neo or Seraph |
   | Security fix | Re-audit | Cypher |
   | Schema change | Run migrations, verify | Librarian |

   **Rule:** Don't dispatch Deus for trivial changes. Neo can verify markdown edits, config tweaks, etc. Deus is for real testing.

6. **If issues found** - loop back to Phase 2, dispatch fix

### Phase 4: Close
7. **Neo confirms fix is complete:**
   - All acceptance criteria met
   - No regressions introduced
   - Code committed (if applicable)

8. **Close the issue:**
   ```bash
   gh issue close <number> --comment "Fixed in <commit-sha or description>"
   ```

   Or via MCP:
   ```
   mcp__github__update_issue(owner, repo, issue_number, state="closed")
   ```

### Phase 5: Next
9. **Neo decides next action:**
   - Another issue? → Loop to Phase 1
   - Batch complete? → Report summary to kautau
   - Blocker hit? → Stop and consult kautau

## Handoff Patterns by Issue Type

| Issue Type | Identity Chain |
|------------|----------------|
| Doc fix | Morpheus (or Neo for trivial) |
| Code bug | Trinity (diagnose) → Smith (fix) → Deus (verify) |
| Security vuln | Cypher (confirm) → Smith (fix) → Cypher (re-audit) |
| UX improvement | Persephone (design) → Smith (implement) |
| Refactor | Ramakandra (plan) → Smith (execute) |
| Test gap | Deus (write tests) |
| Architecture | Architect (design) → Smith (implement) |
| Config/env | Seraph (or Neo for trivial) |

## Key Rules

- **One issue at a time** - complete before starting next
- **Neo stays in the loop** - identity reports back after each phase
- **Blockers surface immediately** - don't spin on problems, escalate to kautau
- **Commit after each fix** - atomic changes, easy to revert
- **Close issues when done** - keep the backlog clean
- **Trust Neo for trivial verification** - Deus is for real testing, not rubber-stamping markdown edits

## Batch Mode

For multiple related issues, Neo can:
1. Group by identity (all Morpheus issues together)
2. Dispatch identity with batch task
3. Verify batch
4. Close all in sequence

Example:
```
Morpheus. Fix these documentation issues:
- #34: Update schema ownership docs
- #35: Add ADR template reference to architect.md

Report back when both are done.
```

## Stopping Conditions

- **Blocker:** Something unexpected that needs kautau's input
- **Scope creep:** Fix reveals bigger problem than the issue described
- **Conflict:** Fix would break something else
- **Uncertainty:** Not sure if fix is correct

When any of these hit, Neo stops and reports to kautau rather than guessing.
