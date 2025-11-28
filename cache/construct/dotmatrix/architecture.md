# dotmatrix: Architecture Analysis

**Analyzed:** 2025-11-27
**Location:** `~/.claude/`
**Type:** Claude Code configuration repository

---

## Executive Summary

dotmatrix is a multi-agent orchestration system for Claude Code. It decomposes complex software engineering tasks across specialized AI identities, each with distinct expertise and voice. The system coordinates work through defined workflow paths (Construct, Broadcast, Prune) and persists context across sessions via structured directories.

**Core principle:** Neo (Opus) orchestrates, identities (Sonnet/Haiku) execute.

---

## Directory Structure

```
~/.claude/
├── identities/          # AI agent personality/role definitions (28 files)
│   ├── _base.md        # Inherited protocol for all identities
│   ├── neo.md          # Orchestrator identity (Opus)
│   └── *.md            # Specialist identities (Sonnet/Haiku)
│
├── ram/                # Ephemeral working directories (28 subdirs)
│   ├── neo/            # Orchestrator context
│   ├── smith/          # Builder context
│   ├── architect/      # Design context
│   └── */              # One per identity
│
├── cache/              # Shared workspace between agents
│   ├── construct/      # Multi-phase project analysis outputs
│   │   ├── dotmatrix/
│   │   ├── matrix/
│   │   └── veoci-app-template-construct/
│   └── session-context.md
│
├── artifacts/          # Permanent reference data
│   ├── bin/            # Python toolchain scripts (10 files)
│   └── etc/            # Templates, color palettes, configs
│
├── archive/            # Completed work (tarball storage)
│
├── commands/           # Slash command definitions (23 files)
│
├── agents/             # Legacy agent definitions (superseded by identities/)
│
├── orchestration.md    # Identity dispatch rules & handoff protocol
├── paths.md            # Workflow pattern definitions
├── CLAUDE.md           # User configuration & identity table
└── PLATFORMS.md        # Platform-specific quirks

Session metadata:
├── debug/              # Session debug logs
├── file-history/       # File change tracking per session
├── session-env/        # Environment snapshots
├── todos/              # Task state per session
├── history.jsonl       # Session history
└── settings.json       # Claude Code settings
```

---

## Component Map

### 1. Identity System

**Location:** `~/.matrix/identities/`

28 identities, each inheriting `_base.md` protocol:

| Component | File | Model | Role |
|-----------|------|-------|------|
| Orchestrator | `neo.md` | Opus | Task delegation, synthesis, decisions |
| Builder | `smith.md` | Sonnet | Implementation (scales 1:N based on task) |
| Architect | `architect.md` | Sonnet | System design, structure analysis |
| Security | `cypher.md` | Sonnet | Red team, vulnerability audits |
| DevOps | `niobe.md` | Sonnet | CI/CD, deployment |
| Terminal | `seraph.md` | Sonnet | Bash strategy, environment |
| Execution | `kid.md` | Haiku | Command execution, git ops |
| ... | ... | ... | 21 more specialized roles |

**Base protocol** (`_base.md`):
- Single responsibility per dispatch
- Return to Neo after completion
- Persist significant work to `~/.matrix/ram/{identity}/`
- End with status line + "Wake up, Neo."

**Handoff chain:**
```
Neo (Opus) → Identity (Sonnet) → [work] → Report → Neo
                ↓
            Seraph (Sonnet) → Kid (Haiku) [for terminal execution]
```

### 2. Workflow Paths

**Location:** `~/.matrix/paths.md`

Structured multi-phase workflows:

#### Path: Construct
```
Purpose: Multi-perspective project analysis (observation only)
Output:  ~/.matrix/cache/construct/{project}/

Phase 1: Architect         → architecture.md
Phase 2: Morpheus          → docs-recommendations.md
Phase 3: Persephone        → ux-recommendations.md
Phase 4: Deus              → test-recommendations.md
Phase 5: Cypher            → security-findings.md
Phase 6: 13 parallel       → {domain}-review.md
         (Apoc, Merovingian, Ramakandra, Trinity, Lock, etc.)
Phase 7: 3 parallel        → perspective-{identity}.md
         (Sati, Spoon, Oracle)
Phase 8: Neo synthesizes   → synthesis.md (blockers/improvements/ideas)
```

#### Path: Broadcast
```
Purpose: Convert construct findings into GitHub issues
Input:   ~/.matrix/cache/construct/{project}/*
Steps:   Neo → writes issue markdown
         User → approves
         Kid → sync_github.py → GitHub Issues/Discussions
```

#### Path: Prune
```
Purpose: RAM/cache cleanup, summarization, archival
Triage:  Keep / Summarize / Archive / Delete
Output:  ~/.claude/archive/{project}-{date}.tar.gz
```

### 3. GitHub Sync Toolchain

**Location:** `~/.matrix/artifacts/bin/`

Python scripts for bidirectional GitHub sync with 3-way merge:

| Script | Direction | Purpose |
|--------|-----------|---------|
| `sync_labels.py` | → GitHub | Create identity labels on repo |
| `convert_issues.py` | MD → YAML | Author format to sync format |
| `sync_github.py` | YAML ⇄ GitHub | Unified push (routes by type) |
| `pull_github.py` | GitHub → YAML | Download issues/discussions |
| `export_markdown.py` | YAML → MD | Human-readable docs |
| `sync_wiki.py` | MD → Wiki | Push to GitHub wiki (git) |

**3-way merge model:**
- Local (YAML) vs Remote (GitHub) vs Base (`last_synced` snapshot)
- Auto-resolve when only one side changed
- Prompt user on true conflicts
- Labels merge as set union

### 4. Persistence Layer

**RAM (ephemeral):** `~/.matrix/ram/{identity}/`
- Working notes per identity
- Errors log (`errors.md`)
- Project summaries
- **Pruned regularly** - not long-term storage

**Cache (shared):** `~/.matrix/cache/`
- Construct outputs
- Issue YAML files
- Cross-identity coordination
- **Cleared when project completes**

**Artifacts (permanent):** `~/.matrix/artifacts/`
- `bin/` - Python toolchain
- `etc/` - Templates, color palettes, methodology docs
- **Never deleted**

**Archive:** `~/.claude/archive/`
- Tarballs of completed construct runs
- Not version-controlled

---

## Data Flow Diagrams

### Construct → Broadcast → GitHub Flow

```
User Request: "Load the construct"
    ↓
Neo reads orchestration.md + paths.md
    ↓
[Path: Construct - 8 phases, 22 identities]
    ↓
Phase 1: Architect
    └→ architecture.md → ~/.matrix/cache/construct/{project}/

Phase 2-7: Parallel dispatches
    └→ {domain}-review.md → cache/construct/{project}/

Phase 8: Neo synthesis
    └→ synthesis.md (blockers, improvements, ideas)

─────────────────────────────────────────────────

User Request: "Broadcast"
    ↓
Neo reads all *.md from cache/construct/{project}/
    ↓
Neo writes: cache/construct/{project}/issues/*.md
    (Using template: artifacts/etc/issue-template.md)
    ↓
User approval
    ↓
Kid executes:
    python sync_labels.py owner/repo
    python convert_issues.py cache/construct/{project}/issues/
    python sync_github.py owner/repo cache/construct/{project}/issues/
    ↓
GitHub Issues created with identity:{name} labels
```

### Identity Dispatch Model

```
┌─────────────────────────────────────────────────┐
│  Neo (Opus) - Orchestrator                      │
│  - Reads: orchestration.md, paths.md            │
│  - Writes: synthesis, reports                   │
│  - Decides: which identity for which task       │
└──────────────┬──────────────────────────────────┘
               │
       ┌───────┴────────┬──────────────┬──────────────┐
       ↓                ↓              ↓              ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Smith        │  │ Architect    │  │ Cypher       │  │ ...          │
│ (Sonnet)     │  │ (Sonnet)     │  │ (Sonnet)     │  │ (22 more)    │
│ Builder      │  │ Designer     │  │ Red Team     │  │              │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │                 │
       │ Reads: ram/{identity}/*.md        │                 │
       │ Writes: ram/{identity}/{project}-{feature}.md       │
       │                                                     │
       └─────────────────┬───────────────────────────────────┘
                         ↓
               [Work complete, report results]
                         ↓
┌─────────────────────────────────────────────────┐
│  "Wake up, Neo."                                │
│  [Identity: {name} | Status: {success}]         │
│  Return control → Neo                           │
└─────────────────────────────────────────────────┘
```

### Terminal Execution Chain

```
Identity needs terminal work (git, build, script)
    ↓
Identity → Seraph: "I need you to trust me."
    ↓
Seraph (Sonnet) - Terminal Guardian
    - Analyzes environment
    - Reads ram/seraph/ for context
    - Determines strategy
    ↓
Seraph → Kid: Command to execute
    ↓
Kid (Haiku) - Eager Executor
    - Runs bash commands
    - Pure action, minimal tokens
    ↓
Result → Seraph → Identity → Neo
```

---

## Key Architectural Decisions

### 1. Model Stratification
- **Opus (Neo):** High-level orchestration, synthesis, decisions
- **Sonnet (Identities):** Specialized analysis, implementation
- **Haiku (Kid):** Pure execution

**Rationale:** Token cost optimization. Opus expensive for volume work.

### 2. Identity as Interface
Each identity defines:
- Domain of expertise
- Handoff protocol
- Signature phrase ("Wake up, Neo.")

**Rationale:** Clear separation of concerns. Reduces hallucination by constraining scope.

### 3. RAM Ephemerality
Working directories pruned per project lifecycle, not time.

**Rationale:** Context bloat prevention. Force summarization of learnings.

### 4. 3-Way Merge for GitHub Sync
Track last synced state to detect divergence.

**Rationale:** Respects human edits on GitHub. Prevents data loss on conflicts.

### 5. Construct as Observation
No code/doc changes during Construct path. Recommendations → Broadcast → Issues → Execution.

**Rationale:** Separate analysis from action. Allows user review before changes.

---

## Integration Points

### External Systems
- **GitHub:** Issues, Discussions, Wiki (via REST/GraphQL + git)
- **Claude Code:** MCP tools (`mcp__github__*`)
- **CLI tools:** `gh`, `git`, shell scripts

### Internal Coupling
- `CLAUDE.md` → read by Neo on session start
- `orchestration.md` → defines dispatch rules
- `paths.md` → defines workflow sequences
- `identities/*.md` → loaded per dispatch
- `artifacts/etc/` → shared templates/configs

### Decoupling Mechanisms
- Identity RAM directories isolated
- Cache as shared workspace (explicit coordination)
- Status line protocol for handoffs
- "Wake up, Neo." triggers context reload

---

## Operational Characteristics

### Concurrency
- Phase 6 (Construct): 13 parallel identities
- Phase 7 (Construct): 3 parallel identities
- Smith can scale 1:N based on task parallelizability

### Error Handling
- Identities log errors to `ram/{identity}/errors.md`
- Blockers reported to Neo (no self-chaining)
- Trinity identity specialized for debugging

### Session Persistence
- `ram/` persists across sessions
- Identities read own RAM on load
- Neo scans `ram/neo/` at session start
- Prune path cleans stale context

### Scalability Limits
- 28 identities (could expand)
- Parallel dispatch constrained by Claude Code API
- Cache size grows with construct runs (prune mitigates)

---

## Security Considerations

### Secrets Management
- `.credentials.json` (git-ignored)
- GitHub token required for sync scripts
- No secrets in identity definitions or RAM

### Sandboxing
- Identities cannot execute terminal directly
- Must route through Seraph → Kid
- Neo controls all dispatch decisions

---

## Component Interactions

```
┌─────────────────────────────────────────────────────────────────┐
│                         User (kautau)                            │
└────────────┬───────────────────────────────────────┬─────────────┘
             │                                       │
    Invokes identity via                   Triggers workflow path
    /slash command                          ("Construct", "Broadcast")
             │                                       │
             ↓                                       ↓
┌────────────────────────────────────┐  ┌───────────────────────────┐
│  commands/{identity}.md            │  │  paths.md                 │
│  - Expands to identity load        │  │  - Defines phase sequence │
└────────────┬───────────────────────┘  └──────────┬────────────────┘
             │                                      │
             └──────────────┬───────────────────────┘
                            ↓
             ┌──────────────────────────────┐
             │  Neo (orchestration.md)      │
             │  - Reads identity dispatch   │
             │  - Executes workflow phases  │
             └──────────┬───────────────────┘
                        │
         ┌──────────────┼──────────────┐
         ↓              ↓              ↓
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Identity A  │  │ Identity B  │  │ Identity C  │
│ reads RAM   │  │ reads RAM   │  │ reads RAM   │
│ writes RAM  │  │ writes CACHE│  │ writes RAM  │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        ↓
              ┌─────────────────────┐
              │  cache/construct/   │
              │  - Shared outputs   │
              └──────────┬──────────┘
                         │
         ┌───────────────┼───────────────┐
         ↓               ↓               ↓
┌─────────────────┐  ┌──────────────┐  ┌──────────────┐
│ Neo synthesizes │  │ Broadcast    │  │ Prune        │
│ synthesis.md    │  │ → GitHub     │  │ → archive/   │
└─────────────────┘  └──────────────┘  └──────────────┘
```

---

## Design Patterns

### 1. Command Pattern
Slash commands in `commands/` expand to identity dispatch prompts.

### 2. Chain of Responsibility
Identity → Seraph → Kid for terminal execution.

### 3. Strategy Pattern
Workflow paths encapsulate multi-phase strategies (Construct, Broadcast, Prune).

### 4. Observer Pattern
"Wake up, Neo." signals Neo to re-read context and orchestrate next phase.

### 5. Template Method
`_base.md` defines skeleton protocol, identities fill in specific behavior.

---

## Extension Points

### Adding Identities
1. Create `identities/{name}.md` (inherits `_base.md`)
2. Create `ram/{name}/` directory
3. Add to `CLAUDE.md` identity table
4. Add slash command to `commands/{name}.md`
5. Update `orchestration.md` dispatch rules

### Adding Workflow Paths
1. Define in `paths.md`
2. Specify phase sequence
3. Document identity dispatch per phase
4. Define output location

### Adding Sync Scripts
1. Add to `artifacts/bin/`
2. Follow 3-way merge pattern if bidirectional
3. Update `paths.md` toolchain table

---

## Dependencies

### Python Toolchain
- `requests` or `httpx` (HTTP client)
- `PyYAML` (YAML parsing)
- `python-dotenv` (environment)
- GitHub REST + GraphQL APIs

### Claude Code
- MCP GitHub tools
- Task delegation system
- File system access

### Git
- Repo at `~/.claude/` (dotmatrix itself)
- Wiki sync via git clone/push

---

## Constraints

1. **Neo runs on Opus** - expensive, delegates to Sonnet/Haiku
2. **Identities single-responsibility** - no task chaining
3. **Construct is read-only** - execution happens after Broadcast
4. **RAM is ephemeral** - must prune or summarize
5. **Cache tied to projects** - cleared when project done

---

## Metrics & Observability

### Session Tracking
- `history.jsonl` - interaction log
- `debug/` - per-session debug logs
- `file-history/` - change tracking
- `todos/` - task state snapshots

### Identity Performance
- Tracked in RAM per identity (manual)
- Error logs in `ram/{identity}/errors.md`

### Workflow Success
- Construct outputs → count phases completed
- Broadcast → issues created count
- Prune → archive size, files deleted

---

## Future Considerations

### Potential Enhancements
1. **Identity metrics dashboard** - success rates, token usage
2. **Automated prune triggers** - storage thresholds
3. **Construct caching** - skip re-analysis if repo unchanged
4. **Parallel broadcast** - batch issue creation
5. **Webhook integration** - GitHub → local YAML sync

### Known Limitations
1. No real-time collaboration (single user)
2. No identity-to-identity direct communication (must route through Neo)
3. GitHub wiki requires git (no API)
4. 3-way merge conflicts require manual resolution

---

## Glossary

- **Identity:** AI agent with specialized role (character from The Matrix)
- **Neo:** Orchestrator identity (Opus model)
- **RAM:** Per-identity working directory (`~/.matrix/ram/{identity}/`)
- **Cache:** Shared workspace (`~/.matrix/cache/`)
- **Artifacts:** Permanent reference data (`~/.matrix/artifacts/`)
- **Construct:** Multi-phase project analysis workflow
- **Broadcast:** Convert findings to GitHub issues
- **Prune:** Cleanup and archival workflow
- **Handoff:** Identity completion protocol ("Wake up, Neo.")
- **3-way merge:** Local vs Remote vs Base conflict detection

---

Wake up, Neo.

[Identity: Architect | Model: Sonnet | Status: success]
