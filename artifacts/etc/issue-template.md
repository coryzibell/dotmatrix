# Issue Template

Example issue from Broadcast path - demonstrates structure for actionable GitHub issues.

---

## Fix command injection in balance-checker

**Type:** `issue`
**Labels:** `identity:smith`, `blocker`, `security`

### Context

From Construct review of `matrix` project. Cypher identified critical security vulnerability during Phase 5 (Security Review).

**Source:** `~/.matrix/cache/construct/matrix/security-findings.md`

### Problem

`cmd/matrix/balance_checker.go:187-295` executes shell commands from markdown `[verify:]` directives without sanitization.

```go
// Current vulnerable code pattern
directive := extractVerifyDirective(line)  // e.g., "[verify:rm -rf /]"
cmd := exec.Command("sh", "-c", directive)
output, _ := cmd.Output()
```

An attacker with write access to markdown files in `~/.matrix/ram/` could execute arbitrary commands.

### Solution

**Option A: Remove the feature entirely**
- Delete `[verify:]` directive handling
- Simplest, eliminates attack surface completely

**Option B: Implement command allowlist**
- Only permit: `grep`, `find`, `test`, `[`, `cat`, `head`, `wc`
- Validate command before execution
- Log rejected attempts

**Recommendation:** Option B - the verification feature is useful, just needs guardrails.

### Implementation Steps

1. Create `isAllowedCommand(cmd string) bool` function
2. Parse directive to extract base command
3. Check against allowlist before execution
4. Return clear error for rejected commands
5. Add tests for both allowed and rejected cases

### Acceptance Criteria

- [ ] No arbitrary command execution possible
- [ ] Allowlisted commands work as before
- [ ] Rejected commands return helpful error message
- [ ] Unit tests cover allowlist validation
- [ ] Cypher re-audits after fix

### Handoff

After Smith implements:
1. Deus verifies with security-focused tests
2. Cypher re-audits the fix
3. Neo reviews and merges
