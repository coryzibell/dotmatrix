# dotmatrix Matrix Context Migration

## Summary

Query executed against coryzibell/dotmatrix repository via MCP GitHub tools.

**Date:** 2025-11-28

---

## PR Details

### PR #78: feat: migrate Matrix context to ~/.matrix/

**Status:** Open (not merged)

**Branch:** `feat/matrix-context-migration`

**URL:** https://github.com/coryzibell/dotmatrix/pull/78

**Title:** `feat: migrate Matrix context to ~/.matrix/ (#77)`

**Created:** 2025-11-28T00:37:53Z

**Last Updated:** 2025-11-28T02:00:48Z

**Author:** coryzibell

### What This PR Does

Migrates the Matrix identity system from `~/.claude/` (Anthropic-owned) to `~/.matrix/` (user-controlled) to avoid conflicts with Claude Code structure changes.

**Key Changes:**

1. **New Structure:**
   - `~/.matrix/` becomes the git-tracked source of truth (dotmatrix repo)
   - `~/.claude/` becomes synced destination (Anthropic-owned, preserved)
   - Clear separation: we own `.matrix/`, Anthropic owns `.claude/`

2. **Context Detection Logic:**
   - CLAUDE.md now checks if `.matrix/` exists in current working directory
   - Falls back to `~/.matrix/` if not found in cwd
   - Supports both global and project-specific contexts

3. **Setup Script:**
   - `setup.py` (Python 3) replaces shell script for cross-platform compatibility
   - Force mode by default: overwrites `~/.claude/agents/` and `~/.claude/CLAUDE.md`
   - Preserves `~/.claude/commands/` (user shortcuts)
   - Source of truth stays in `.matrix/`, synced to `.claude/`

4. **Directory Structure:**
   ```
   ~/.matrix/                    # Git-tracked (dotmatrix repo)
   ├── identities/              # Identity definitions
   ├── orchestration.md         # Coordination model
   ├── paths.md                 # Workflow patterns
   ├── PLATFORMS.md             # Platform-specific config
   ├── agents/                  # Slash command definitions
   ├── CLAUDE.md                # Context loader (source of truth)
   ├── artifacts/               # Scripts and tools
   ├── ram/                     # Session notes (.gitignore)
   ├── cache/                   # Workflow artifacts (.gitignore)
   ├── future/                  # Project ideas (.gitignore)
   ├── archive/                 # Historical files
   └── setup.py                 # Cross-platform sync script

   ~/.claude/                   # Anthropic-owned (synced from .matrix)
   ├── CLAUDE.md                # Copied from .matrix/ (overwritten on setup)
   ├── agents/                  # Copied from .matrix/agents/ (overwritten on setup)
   └── commands/                # User shortcuts (preserved, not synced)
   ```

### Testing Status

- ✓ `~/.matrix/` structure created
- ✓ setup.py syncs 27 agents to `~/.claude/agents/`
- ✓ setup.py syncs CLAUDE.md to `~/.claude/CLAUDE.md`
- ✓ All slash commands work
- ✓ Context loads correctly
- ✓ Tested on Linux (other platforms pending)

### Benefits

- **Portable:** Clone repo, run setup.py, ready to go
- **Safe:** No conflicts with Anthropic updates to `.claude/`
- **Cross-platform:** Python works on Windows/macOS/Linux
- **Clean separation:** We own `.matrix/`, Anthropic owns `.claude/`
- **Always fresh:** Setup overwrites synced files to ensure consistency

---

## Related Issue #77

**Title:** `Migrate context to ~/.matrix/ to avoid conflicts with Claude Code structure`

**Status:** Open

**URL:** https://github.com/coryzibell/dotmatrix/issues/77

**Created:** 2025-11-28T00:13:32Z

**Last Updated:** 2025-11-28T00:31:28Z

**Labels:** enhancement, identity:smith, architecture

**Comments:** 2

### Problem Statement

Currently tracking `.claude/` directly in git, which is fragile:
- `.claude/` is owned by Anthropic and could change structure
- Mixing our config with Anthropic's tooling creates dependency risk
- Not fully portable - agents folder requires special handling

### Solution Approach

Move configuration to `~/.matrix/` with intelligent context detection:
1. Check if `.matrix/` exists in current working directory (project-specific)
2. Fall back to `~/.matrix/` (global defaults)
3. Load identities, orchestration, paths, PLATFORMS from detected root

### Version Control Strategy

**Decision:** Track everything in `.matrix/` to preserve full context across machines.

**What Gets Tracked:**
- identities/ - Identity definitions
- orchestration.md - Coordination model
- paths.md - Workflow patterns
- PLATFORMS.md - Platform-specific configuration
- artifacts/bin/ - Python scripts and tools
- agents/ - Slash command definitions
- ram/ - Session notes and working memory
- cache/ - Workflow artifacts
- future/ - Project ideas
- archive/ - Deprecated/historical files

**Rationale:** Goal is portable context - clone the repo on a new machine and have all context available.

---

## Related Open Issues

### Issue #6: Construct as CI check

**Status:** Open

**Labels:** enhancement, identity:oracle, infrastructure

**Description:** Exploring running Construct audit on every commit to generate health scores, auto-identify critical findings, and validate PR quality.

### Issue #4: Construct -> Worker path for auto-fix PRs

**Status:** Open (in progress)

**Labels:** enhancement, identity:oracle

**Description:** Gap between Construct findings (observation-only) and action (Smith). Proposal to auto-generate fix PRs from audit findings where solutions are obvious.

**Core Implementation Status:** Matrix Worker pipeline complete (`matrix-worker.yml`)

---

## Data Flow & Causality

The transaction here is clear: **control over context**.

- **Before:** Context lived in `.claude/`, Anthropic-controlled space. Any update to Claude Code structure could break the entire identity system.
- **After:** Context lives in `.matrix/`, git-tracked, under user control. Anthropic's `.claude/` becomes a synced *destination*, not source of truth.

The setup.py acts as the *broker* of this transaction - it synchronizes state between source and destination on demand, ensuring consistency while maintaining separation of concerns.

This is portable, resilient, and follows the principle of clear boundaries between systems.

---

## Next Steps (Post-Merge)

1. Update dotmatrix repo remote to track `~/.matrix/` instead of `~/.claude/`
2. Users run `~/.matrix/setup.py` on new machines
3. Optional: Clean up old files from `~/.claude/` (manual, not automated)
