# Matrix CLI Architecture

**Generated:** 2025-11-26
**Version:** v0.0.1
**Location:** `/home/w3surf/work/personal/code/matrix`

## System Overview

Matrix is a unified CLI tool for the Claude Code identity system. It provides 24 specialized commands for analyzing and managing identity RAM directories, tracking development velocity, performing code reconnaissance, and surfacing patterns across the identity ecosystem.

## Architecture Diagram

```
matrix/
│
├── cmd/                          # Command Layer
│   ├── matrix/                   # Main CLI binary
│   │   ├── main.go              # Entry point & command router
│   │   ├── garden_paths.go      # Identity connection discovery
│   │   ├── garden_seeds.go      # RAM file generation
│   │   ├── tension_map.go       # Conflict detection
│   │   ├── velocity.go          # Performance tracking
│   │   ├── recon.go            # Codebase intelligence
│   │   ├── incident_trace.go    # Post-mortem extraction
│   │   ├── crossroads.go        # Decision tracking
│   │   ├── balance_checker.go   # Design vs implementation drift
│   │   ├── breach_points.go     # Security audit
│   │   ├── vault_keys.go        # Auth/authz mapping
│   │   ├── flight_check.go      # Deployment state
│   │   ├── knowledge_gaps.go    # Documentation holes
│   │   ├── contract_ledger.go   # Data flow tracking
│   │   ├── schema_catalog.go    # Database schemas
│   │   ├── phase_shift.go       # Language migration
│   │   ├── platform_map.go      # Cross-platform markers
│   │   ├── verdict.go           # Test metrics
│   │   ├── question.go          # Assumption surfacing
│   │   ├── debt_ledger.go       # Tech debt tracking
│   │   ├── friction_points.go   # UX feedback queue
│   │   ├── spec_verify.go       # Spec compliance
│   │   ├── alt_routes.go        # Accessibility audit
│   │   ├── data_harvest.go      # Fixture generation
│   │   ├── dependency_map.go    # Toolchain mapping
│   │   └── diff_paths.go        # Implementation comparison
│   │
│   └── test-scanner/             # Test harness
│       └── main.go              # Scanner testing tool
│
├── internal/                     # Domain Layer
│   ├── identity/                 # Identity management
│   │   └── identity.go          # Registry & validation
│   │
│   ├── ram/                      # RAM directory operations
│   │   ├── scanner.go           # File discovery & parsing
│   │   └── scanner_test.go      # Scanner tests
│   │
│   └── output/                   # Display formatting
│       └── output.go            # ANSI color utilities
│
├── go.mod                        # Module definition
└── README.md                     # Project documentation
```

## Component Map

### Command Layer (`cmd/matrix/`)

**Responsibility:** User interface, command routing, argument parsing, output formatting.

The command layer consists of:

1. **main.go** - Command router
   - Simple switch-based routing (no cobra dependency)
   - 24 command handlers
   - Help text generation
   - Error handling & exit codes

2. **Command Implementations** (24 files, ~300-900 LOC each)
   - Each command is self-contained
   - Imports from internal packages
   - Follows pattern: parse flags → scan RAM → analyze → display
   - Examples:
     - `garden_paths.go`: Scans RAM for identity mentions, builds connection graph
     - `velocity.go`: Extracts task metadata, calculates performance metrics
     - `recon.go`: Code intelligence scanning with language detection

### Domain Layer (`internal/`)

**Responsibility:** Core business logic, data structures, shared utilities.

#### `internal/identity/`
- **Purpose:** Identity registry and validation
- **Key Functions:**
  - `All()` - Returns all 28 known identities
  - `IsValid(name)` - Validates identity names
  - `RAMPath(name)` - Resolves `~/.matrix/ram/{identity}` paths
- **Data:** Hardcoded identity list (neo, smith, trinity, etc.)

#### `internal/ram/`
- **Purpose:** RAM directory scanning and file parsing
- **Key Types:**
  - `File` - Represents a RAM markdown file (path, identity, content)
- **Key Functions:**
  - `DefaultRAMDir()` - Resolves `~/.matrix/ram`
  - `ScanDir(path)` - Walks directory tree, finds all `.md` files
- **Behavior:**
  - Recursively scans identity subdirectories
  - Filters for `.md` files only
  - Gracefully handles permission errors
  - Returns flat slice of File structs

#### `internal/output/`
- **Purpose:** Terminal output formatting
- **Key Functions:**
  - `Header(text)` - Cyan headers
  - `Item(label, value)` - Yellow labels
  - `Success(text)` - Green success messages
- **Features:**
  - ANSI color codes
  - `NoColor` flag for plain output
  - Consistent visual language across commands

## Data Flows

### 1. Command Invocation Flow

```
User Input
    ↓
main.go (os.Args parser)
    ↓
Switch statement routes to command
    ↓
Command implementation (e.g., runGardenPaths)
    ↓
Parse flags (flag.FlagSet)
    ↓
Validate inputs
    ↓
Call domain layer
    ↓
Format & display results
    ↓
Exit with status code
```

### 2. RAM Scanning Flow

```
Command requests scan
    ↓
ram.DefaultRAMDir()
    ├→ os.UserHomeDir()
    └→ Resolves ~/.matrix/ram
    ↓
ram.ScanDir(ramDir)
    ├→ os.ReadDir() for identity dirs
    ├→ filepath.WalkDir() per identity
    ├→ Filter *.md files
    ├→ os.ReadFile() per file
    └→ Return []ram.File
    ↓
Command analyzes files
    ↓
Results displayed via output package
```

### 3. Garden Paths Connection Flow

```
User: matrix garden-paths
    ↓
Load all RAM files
    ↓
For each file:
    ├→ Extract identity from path
    ├→ Scan content for identity mentions
    ├→ Use regex with word boundaries
    └→ Skip self-references
    ↓
Build connection graph
    ├→ Map: file → mentioned identities
    └→ Map: identity → mention count
    ↓
Display:
    ├→ Files with connections
    ├→ Most-mentioned identities (top 10)
    └→ Sorted by count descending
```

### 4. Velocity Analysis Flow

```
User: matrix velocity [--identity X] [--days N] [--json]
    ↓
Load all RAM files (filtered by identity if specified)
    ↓
Parse task metadata from content:
    ├→ Regex: status lines (success/failure/partial)
    ├→ Regex: timestamps (started/completed)
    ├→ Regex: handoff mentions
    └→ Extract from surrounding context window
    ↓
Calculate statistics per identity:
    ├→ Total tasks
    ├→ Success/failure/partial counts
    ├→ Success rate percentage
    ├→ Average duration
    └→ Handoff patterns (from → to)
    ↓
Generate report:
    ├→ High performers (>3 tasks, sorted by success rate)
    ├→ Bottlenecks (>2 tasks, sorted by failures)
    └→ Top handoff patterns (top 5 by count)
    ↓
Output as formatted text or JSON
```

### 5. Reconnaissance Scan Flow

```
User: matrix recon [path] [--quick] [--focus security|architecture|docs]
    ↓
filepath.Walk() target directory
    ├→ Skip hidden dirs, build dirs, node_modules
    ├→ Skip binary files
    └→ Collect file paths & extensions
    ↓
Analyze in parallel:
    ├→ detectLanguage() - Count by extension
    ├→ detectProjectType() - Check for package.json, go.mod, etc.
    ├→ findEntryPoints() - Look for main.*, lib.rs, etc.
    ├→ analyzeArchitecture() - Count files per dir, detect patterns
    ├→ findDependencies() - Parse package.json, Cargo.toml, go.mod
    ├→ analyzeDocumentation() - Check for README, docs/
    └→ analyzeHealth() - Scan for TODO, FIXME, hardcoded secrets
    ↓
Build ProjectInfo struct
    ↓
Display report (filtered by focus flag)
```

## Key Design Patterns

### 1. **Command Pattern**
Each command is a separate file with a `run{CommandName}()` function. Main router dispatches via simple switch statement.

**Rationale:** Avoids heavyweight CLI framework dependency. Easy to add new commands.

### 2. **Domain-Driven Structure**
Internal packages represent domain concepts (identity, ram, output) rather than technical layers.

**Rationale:** Aligns code with problem space. Clear boundaries between concerns.

### 3. **Flat File Scanning**
RAM scanner returns flat slice of files, not nested tree structure.

**Rationale:** Most commands need to process all files linearly. Simplifies iteration.

### 4. **Regex-Based Parsing**
Content analysis uses regex patterns, not full AST parsing.

**Rationale:** Fast, works across file formats, sufficient for metadata extraction.

### 5. **Graceful Degradation**
All file operations handle errors gracefully (skip & continue).

**Rationale:** Partial results better than failure. Robust against permission issues.

## Data Storage

**Location:** `~/.matrix/ram/{identity}/*.md`

**Format:** Markdown files (unstructured)

**Schema:** None enforced. Commands extract patterns via regex.

**Ownership:** Each identity owns its subdirectory.

**No central database.** All state lives in filesystem as human-readable markdown.

## Integration Points

### External Data Sources
- **Filesystem:** Primary data source (`~/.matrix/ram/`)
- **Codebase targets:** Any directory for `recon` command
- **Package manifests:** `package.json`, `go.mod`, `Cargo.toml`, etc.

### Output Targets
- **stdout:** Formatted text (default)
- **JSON:** Structured output (some commands support `--json` flag)

### No network I/O.** All operations are local.

## Extensibility

### Adding a New Command

1. Create `cmd/matrix/{command_name}.go`
2. Implement `run{CommandName}() error` function
3. Add case to switch statement in `main.go`
4. Add help text to help display
5. Follow established patterns:
   - Use `flag.FlagSet` for flags
   - Import from `internal/` packages
   - Use `output` package for formatting
   - Return errors, don't `os.Exit()` inside command

### Adding a New Identity

1. Add name to `identities` slice in `internal/identity/identity.go`
2. Ensure `~/.matrix/ram/{name}/` directory exists
3. No code changes needed elsewhere (dynamic dispatch)

## Dependencies

**Zero external dependencies.**

Uses only Go standard library:
- `flag` - Command-line parsing
- `os`, `path/filepath` - File operations
- `regexp` - Pattern matching
- `strings` - Text processing
- `time` - Timestamp parsing
- `encoding/json` - JSON output
- `sort` - Data sorting
- `fmt` - Formatting

**Rationale:** Minimizes maintenance burden, fast builds, easy deployment.

## Constraints & Tradeoffs

### Constraint: No Database
**Tradeoff:** Must scan all files every invocation. Slow on large RAM directories.
**Mitigation:** Commands support filtering flags (e.g., `--identity`, `--days`).

### Constraint: Unstructured Markdown
**Tradeoff:** Regex parsing is brittle, may miss patterns.
**Mitigation:** Patterns designed for common conventions. Graceful handling of parse failures.

### Constraint: Single Binary
**Tradeoff:** All 24 commands compiled into one executable (~2-5 MB).
**Mitigation:** Fast startup, easy distribution. Go compile times are fast.

### Constraint: No Configuration File
**Tradeoff:** Can't customize behavior without flags.
**Mitigation:** Sensible defaults. Most commands work zero-config.

## Performance Characteristics

- **Startup:** <10ms (no framework overhead)
- **RAM Scan:** O(n) files, ~1ms per file
- **Memory:** O(n) - all files loaded into memory
- **Bottleneck:** Filesystem I/O (reading files)

**Optimization opportunities:**
- Parallel file reading (not currently implemented)
- Incremental scanning (track mtime, skip unchanged files)
- Index file (cache scan results)

## Security Considerations

- **Input Validation:** Identity names validated against hardcoded list
- **Path Traversal:** Uses `filepath.Join()`, relative path resolution
- **File Permissions:** Respects OS permissions, skips inaccessible files
- **No Code Execution:** Pure read operations, no eval or exec
- **Secrets Detection:** `recon` command includes basic secret scanning

**Audit Note:** `recon` command scans for hardcoded secrets but does not currently report to a security system.

## Testing Strategy

- **Unit Tests:** `internal/ram/scanner_test.go` (RAM scanner tests)
- **Integration Tests:** `cmd/test-scanner/main.go` (manual test harness)
- **No automated command tests yet** (TODO: add command-level tests)

**Coverage:** Limited. Core domain logic tested, commands not yet tested.

## Future Architecture Directions

### Phase 1: Current State (v0.0.1)
- 24 commands, zero dependencies
- Flat file scanning
- Regex-based parsing

### Phase 2: Optimization (v0.1.0)
- Add indexing for large RAM directories
- Parallel file scanning
- Command-level tests

### Phase 3: Extensibility (v0.2.0)
- Plugin system for custom commands
- Structured frontmatter in RAM files
- Export/import identity data

### Phase 4: Integration (v1.0.0)
- GitHub integration (PR metrics, issue tracking)
- CI/CD hooks (velocity tracking in pipelines)
- Dashboard generation (static HTML reports)

---

**Generated by:** Architect
**Model:** Sonnet 4.5
**Status:** Complete
