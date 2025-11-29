---
title: "chore(deps): update zero-code dependencies"
labels:
  - dependencies
  - identity:smith
priority: P2
---

## Context

Part of the Cycle upgrade plan for base-d. These dependencies have major version bumps but require no code changes.

## Dependencies

| Crate | Current | Target |
|-------|---------|--------|
| brotli | 7.0 | 8.0.2 |
| dirs | 5.0.1 | 6.0.0 |
| crossterm | 0.28.1 | 0.29.0 |
| terminal_size | 0.3.0 | 0.4.3 |

## Steps

1. Update versions in `Cargo.toml`
2. Run `cargo update`
3. Run `cargo test`
4. Run `cargo build --release`

## Acceptance Criteria

- [ ] All four dependencies updated
- [ ] All tests pass
- [ ] Release build succeeds
- [ ] No new warnings

## Handoff

Smith implements → Deus verifies tests pass
