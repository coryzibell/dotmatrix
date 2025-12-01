# mx CLI Restructure - Architectural Design

**Date:** 2025-12-01
**Issue:** #46
**Status:** Design Complete

## Current State Analysis

### Command Inventory

#### Already Conforming (Domain Action)
```
mx zion <action>          # Knowledge management
mx pr <action>            # Pull request operations
mx sync <action>          # GitHub sync operations
mx github <action>        # GitHub operations
mx wiki <action>          # Wiki operations
mx session <action>       # Session export
mx convert <action>       # Conversion utilities
```

#### Non-Conforming (Single-Level)
```
mx commit <message>       # Should be: mx git commit
mx encode-commit          # Should be: mx git encode-commit
mx doctor                 # Should be: mx system doctor
```

### Full Command Tree (Current)

```
mx
├── zion
│   ├── rebuild
│   ├── search <query>
│   ├── list [--category]
│   ├── show <id>
│   ├── stats
│   ├── delete <id>
│   ├── import [path]
│   ├── add [options]
│   ├── migrate [--status]
│   ├── agents
│   │   ├── list
│   │   ├── add <id>
│   │   ├── show <id>
│   │   └── seed [--path]
│   ├── projects
│   │   ├── list
│   │   └── add [options]
│   ├── applicability
│   │   ├── list
│   │   └── add [options]
│   ├── sessions
│   │   ├── list [--project]
│   │   ├── create [options]
│   │   └── close <id>
│   └── export [--format] [--output]
│
├── commit <message> [-a] [-p]          # NON-CONFORMING
├── encode-commit -t <title> -b <body>  # NON-CONFORMING
│
├── pr
│   └── merge <number> [--rebase|--merge]
│
├── sync
│   ├── pull <repo> [-o output] [--dry-run]
│   ├── push <repo> [-i input] [--dry-run]
│   ├── labels <repo> [--dry-run]
│   └── issues <repo> [--dry-run]
│
├── github
│   ├── cleanup <repo> [--issues] [--discussions] [--dry-run]
│   └── comment
│       ├── issue <repo> <number> <message> [--identity]
│       └── discussion <repo> <number> <message> [--identity]
│
├── wiki
│   └── sync <repo> <source> [--page-name] [--dry-run]
│
├── session
│   └── export [path] [-o output]
│
├── convert
│   ├── md2yaml <input> [-o output] [--dry-run]
│   └── yaml2md <input> [-o output] [-r repo] [--dry-run]
│
└── doctor                               # NON-CONFORMING
```

## Domain Model

The system organizes into these logical domains:

### Primary Domains
1. **zion** - Knowledge management (already correct)
2. **git** - Git operations with encoded commits (NEW)
3. **github** - GitHub API operations (existing)
4. **sync** - Bidirectional GitHub sync (existing)
5. **wiki** - GitHub wiki operations (existing)
6. **convert** - Format conversion utilities (existing)
7. **session** - Session management (existing)
8. **system** - Environment diagnostics (NEW)

### Boundary Analysis

**zion domain** handles knowledge indexing, search, export. Well-bounded.

**git domain** encapsulates Matrix-encoded commit workflow. Separated from github (API) and sync (bidirectional state management).

**github domain** for direct GitHub API operations (cleanup, comments). Distinct from sync which manages state synchronization.

**sync domain** manages bidirectional state sync between local YAML and GitHub issues/discussions. Orthogonal to github domain.

**pr operations** are git operations (merge commits), not GitHub API calls. Should migrate to git domain.

**doctor** is system health check. Belongs in new system domain.

## Proposed Structure

```
mx
├── zion <action>            # No change
├── git                      # NEW domain
│   ├── commit <message> [-a] [-p]
│   ├── encode-commit -t <title> -b <body>
│   └── pr
│       └── merge <number> [--rebase|--merge]
├── github <action>          # No change
├── sync <action>            # No change
├── wiki <action>            # No change
├── convert <action>         # No change
├── session <action>         # No change
└── system                   # NEW domain
    └── doctor
```

## Migration Strategy

### Approach: Gradual with Deprecation

Breaking change would disrupt documented workflows. Gradual migration preferred.

#### Phase 1: Introduce New Commands (v0.2.0)
- Add `mx git commit` (same behavior as `mx commit`)
- Add `mx git encode-commit` (same behavior as `mx encode-commit`)
- Add `mx git pr merge` (same behavior as `mx pr merge`)
- Add `mx system doctor` (same behavior as `mx doctor`)
- Keep old commands functional with deprecation warnings

#### Phase 2: Deprecation Period (v0.2.x - v0.4.x)
- Old commands print warning: "Warning: 'mx commit' is deprecated. Use 'mx git commit'"
- Update documentation to reference new patterns
- Update CLAUDE.md to prefer new patterns
- Monitor usage, gather feedback

#### Phase 3: Breaking Change (v1.0.0)
- Remove `mx commit`, `mx encode-commit`, `mx doctor`
- Remove `mx pr` (move to `mx git pr`)
- Clean removal during major version bump

### Backwards Compatibility Mechanism

```rust
// In main.rs Commands enum
enum Commands {
    // New structure
    Git {
        #[command(subcommand)]
        command: GitCommands,
    },
    System {
        #[command(subcommand)]
        command: SystemCommands,
    },

    // Deprecated (keep for Phase 1-2)
    #[command(hide = true)]  // Hide from --help
    Commit { ... },
    #[command(hide = true)]
    EncodeCommit { ... },
    #[command(hide = true)]
    Pr { ... },
    #[command(hide = true)]
    Doctor,

    // Existing domains (no change)
    Zion { ... },
    Github { ... },
    Sync { ... },
    Wiki { ... },
    Convert { ... },
    Session { ... },
}

enum GitCommands {
    Commit { ... },
    EncodeCommit { ... },
    Pr {
        #[command(subcommand)]
        command: PrCommands,
    },
}

enum SystemCommands {
    Doctor,
}
```

### Deprecation Warning Implementation

```rust
fn handle_deprecated_commit(message: String, all: bool, push: bool) -> Result<()> {
    eprintln!("Warning: 'mx commit' is deprecated. Use 'mx git commit' instead.");
    eprintln!("This command will be removed in mx v1.0.0\n");
    commit::upload_commit(&message, all, push)
}
```

## Technical Considerations

### Clap Patterns

Current code uses clap derive macros correctly. Migration requires:

1. Add new `GitCommands` and `SystemCommands` enums
2. Move existing `PrCommands` under `GitCommands::Pr`
3. Mark deprecated commands with `#[command(hide = true)]`
4. Route deprecated commands to same handlers with warning wrapper

### Impact Analysis

**User Impact:**
- No immediate breaking changes
- Clear migration path with warnings
- Documentation updates guide transition

**Code Impact:**
- Minimal - primarily routing layer changes
- Handler functions unchanged
- Test suite requires command invocation updates

**Integration Impact:**
- CLAUDE.md requires updates to reference new patterns
- CI/CD scripts need updating to use new commands
- GitHub workflows may reference old commands

### Command Aliasing

clap supports aliases. Consider:

```rust
#[command(name = "commit", aliases = ["c"])]
Commit { ... }
```

Could provide both full migration AND short aliases:
- `mx g c` (git commit - short)
- `mx git commit` (git commit - full)
- `mx commit` (deprecated - warning)

This satisfies both consistency and ergonomics.

## Decision Record

### Decision: Gradual Migration with Three Phases

**Context:** Need to restructure CLI to `mx <domain> <action>` pattern while minimizing disruption.

**Decision:**
1. Introduce new commands alongside old (v0.2.0)
2. Deprecate old commands with warnings (v0.2.x - v0.4.x)
3. Remove old commands at v1.0.0

**Consequences:**
- Positive: Users have migration window
- Positive: Documentation can update gradually
- Positive: Breakage occurs at semver major boundary
- Negative: Code carries deprecation baggage temporarily
- Negative: Two ways to invoke same command during transition

### Decision: Create 'git' and 'system' Domains

**Context:** `commit`, `encode-commit`, `pr`, and `doctor` don't fit domain pattern.

**Decision:**
- Git operations → `mx git` domain
- System diagnostics → `mx system` domain

**Consequences:**
- Positive: All commands follow consistent domain pattern
- Positive: Clear separation between git operations and GitHub API
- Positive: Future git operations have natural home
- Negative: `mx git` may confuse users (not standard git commands)

**Alternatives Considered:**
- `mx commit` → `mx vcs commit` (too generic)
- `mx commit` → `mx repo commit` (unclear)
- `mx doctor` → `mx health check` (verbose)

### Decision: Move PR Operations to Git Domain

**Context:** PRs are GitHub objects but `mx pr merge` performs git operations (merge commits).

**Decision:** Move to `mx git pr merge`

**Rationale:**
- Primary action is git commit with encoded message
- GitHub API is implementation detail
- Aligns with git commit encoding workflow

**Consequences:**
- Positive: Git-related operations colocated
- Positive: Clearer that this modifies git history
- Negative: May feel unintuitive (PRs are GitHub concept)

## Implementation Order

For Smith (implementation agent):

1. **Add New Domains** (single commit)
   - Define `GitCommands` and `SystemCommands` enums
   - Wire up routing in match statement
   - Share handlers with deprecated commands

2. **Add Deprecation Warnings** (single commit)
   - Wrap deprecated command handlers
   - Mark with `#[command(hide = true)]`
   - Test warning output

3. **Update Documentation** (single commit)
   - README examples use new commands
   - Note deprecation timeline
   - Update CLAUDE.md preferences

4. **Update Tests** (single commit)
   - Add tests for new command paths
   - Keep deprecated command tests (for now)
   - Verify warnings appear

5. **Update Version** (with release)
   - Bump to v0.2.0
   - Changelog notes new structure
   - Migration guide in release notes

## Future Considerations

### Potential Future Domains

If system grows, additional domains might emerge:

- `mx cache` - Cache management operations
- `mx ram` - RAM tier operations
- `mx artifacts` - Artifact management

### Alias Strategy

Post-v1.0.0, could add ergonomic aliases:
- `mx g` → `mx git`
- `mx gh` → `mx github`
- `mx z` → `mx zion`

Keep as explicit opt-in to maintain discoverability.

### Help Text Organization

With more domains, consider:
```
mx --help          # Shows domains
mx git --help      # Shows git actions
mx git commit -h   # Shows commit flags
```

Clap supports this naturally.

## Conclusion

The restructure introduces two new domains (git, system) and establishes a three-phase migration plan. This maintains backward compatibility while moving toward architectural consistency. Implementation is straightforward given clap's capabilities. Impact is primarily documentation and user communication, not code complexity.

---

**Files Affected:**
- `/home/w3surf/work/personal/code/mx/src/main.rs` - Primary changes
- `/home/w3surf/work/personal/code/mx/README.md` - Documentation updates
- `/home/w3surf/.matrix/CLAUDE.md` - Preference updates

**Dependencies:**
- None. Pure routing layer changes.

**Testing Requirements:**
- Verify new commands invoke same handlers
- Verify deprecation warnings appear
- Verify --help hides deprecated commands
- Integration tests for both old and new paths
