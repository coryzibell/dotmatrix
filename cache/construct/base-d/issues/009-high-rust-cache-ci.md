## Add rust-cache to CI for faster builds

**Type:** `issue`
**Labels:** `identity:niobe`, `high-priority`, `ci`

### Context

From Construct review of `base-d` project. Niobe identified CI optimization.

**Source:** `~/.matrix/cache/construct/base-d/cicd-review.md`

### Problem

CI builds don't cache Rust dependencies, rebuilding everything from scratch each time. This adds ~2-3 minutes per workflow run.

### Solution

Add `Swatinem/rust-cache@v2` action to CI workflows.

### Implementation Steps

1. Add rust-cache action after rust toolchain setup:
   ```yaml
   - uses: Swatinem/rust-cache@v2
   ```
2. Apply to all workflow files:
   - `pr-checks.yml`
   - `the-matrix-has-you.yml`
   - Any other CI workflows
3. Verify cache hits in subsequent runs

### Acceptance Criteria

- [ ] rust-cache added to all workflows
- [ ] Second run shows cache hit
- [ ] ~50% build time reduction

### Handoff

Niobe implements → verify cache hits → Neo merges
