# Add consistent JSON output across all commands

**Type:** `issue`
**Labels:** `identity:smith`, `improvement`, `ux`
**Status:** open
**GitHub:** [#18](https://github.com/coryzibell/matrix/issues/18)

---

# Add consistent JSON output across all commands






From Construct review of `matrix` project. Persephone identified inconsistency during user experience review.

**Source:** Persephone's UX review

## Problem

JSON support is inconsistent across commands. Some commands support `--json`, others don't. This makes it hard to script with matrix or pipe output to other tools.

## Solution

Add `--json` flag to all commands that output data. JSON output should:
- Be valid JSON (parseable by `jq`)
- Include consistent structure across commands
- Suppress decorative output (colors, headers) when in JSON mode

## Implementation Steps

1. Audit all commands for current JSON support
2. Define consistent JSON envelope structure
3. Add `--json` flag to commands missing it
4. Ensure all commands respect the flag
5. Add tests for JSON output validity

## Acceptance Criteria

- [ ] All data-outputting commands support `--json`
- [ ] JSON output is valid and parseable by `jq`
- [ ] Consistent structure across commands
- [ ] No ANSI colors or decorative text in JSON mode
- [ ] Documentation lists JSON-capable commands

## Handoff

1. Smith implements JSON support across commands
2. Deus tests JSON output validity
3. Morpheus updates documentation

---

*Last synced: Nov 26, 2025 at 09:21 PM*