# Program: Cycle

**Trigger:** "cycle", "upgrade", "update dependencies", "what's the latest version"

*"Upgrades. Enhancements."* — Agent Smith

**Purpose:** Check for available upgrades to project toolchains/languages/frameworks and dependencies, research migration paths, plan the upgrade.

**Input:** Project path or name

**Output:** Migration plan with GitHub issues for execution

## Steps

### Phase 0: Locate

> See `lib/locate.md` for project detection logic.

Output: Absolute path to repo, project name

### Phase 1: Detect Project Type & Ecosystem

1. **Neo identifies the project type and ecosystem** by checking for:
   - `Cargo.toml` → Rust ecosystem (rustc, cargo, cargo plugins, common crates)
   - `package.json` → Node ecosystem (node, npm/yarn/pnpm, framework: react/vue/quasar/next/etc)
   - `go.mod` → Go ecosystem (go, common modules)
   - `pyproject.toml` / `setup.py` → Python ecosystem (python, pip/poetry/uv, frameworks: django/fastapi/etc)
   - `Gemfile` → Ruby ecosystem (ruby, bundler, rails/etc)
   - `.tool-versions` / `mise.toml` → Multiple tools

   Output: Project type, detected frameworks/tools, current versions where detectable

### Phase 2: Check Latest Toolchain & Linter

2. **Dispatch Tank** - Research current stable toolchain version AND linter changes

   Tank should research the **full ecosystem context**, not just the language:
   - **Rust:** rustc version, edition, cargo features, clippy changes, common toolchain updates
   - **Node:** node version, npm/yarn/pnpm, AND the framework (react 18→19, next 14→15, quasar 2→3, etc)
   - **Go:** go version, module system changes
   - **Python:** python version, pip/poetry/uv, AND frameworks (django, fastapi, etc)

   **Linter research (critical):**
   - Check latest linter docs for the ecosystem (clippy, eslint, golangci-lint, ruff, etc.)
   - Note new lints added since project's current version
   - Note deprecated lints that may need updating
   - Document lint rule changes that might affect the project
   - **Research common suppressions** found in codebases:
     - What each suppressed lint checks for
     - Why it's commonly suppressed
     - How to fix the underlying issue instead of suppressing
     - Whether the lint behavior changed between versions

   **Cache linter research:**
   ```
   ~/.matrix/artifacts/cycles/<type>/lints/<lint-name>.md
   ```
   Example: `~/.matrix/artifacts/cycles/rust/lints/clippy-too-many-arguments.md`

   - One file per lint rule
   - Include: what it catches, why to fix vs suppress, code patterns to resolve
   - Ramakandra references these during cleanup

   **Cache check first:**
   ```
   ~/.matrix/artifacts/cycles/<type>/<from>-to-<to>.md
   ```
   Example: `~/.matrix/artifacts/cycles/rust/1.75-to-1.83.md`

   - **If exists:** Load it, report summary
   - **If missing:** Research and write guide

   **Skip patch versions** - only research major/minor jumps (1.75→1.83, not 1.83.0→1.83.1)

   Output: Latest version, migration guide (cached or newly written)

### Phase 3: Dependency Audit

3. **Dispatch Apoc** - Deep dependency audit using ecosystem tools

   **Input from Tank:** Target toolchain version (e.g., Rust 1.83, Node 22)

   **Important:** Dependency audit tools report based on current toolchain. To get accurate results for what's available at the *target* version, Apoc should:
   - **Rust:** Temporarily set toolchain (`rustup override set 1.83`) before running `cargo outdated`
   - **Node:** Use `nvm use 22` or equivalent before `npm outdated`
   - **Restore original toolchain** after audit (or work in temp branch)

   **Tools by ecosystem:**
   - **Rust:** `cargo outdated`, `cargo audit`, `cargo update --dry-run`
   - **Node:** `npm outdated`, `npm audit`, `npx npm-check-updates`
   - **Go:** `go list -m -u all`, `govulncheck`
   - **Python:** `pip list --outdated`, `pip-audit`, `safety check`
   - **Ruby:** `bundle outdated`, `bundle audit`

   **Cache check first:**
   ```
   ~/.matrix/artifacts/cycles/<type>/dependencies/<dep>/<from>-to-<to>.md
   ```
   Example: `~/.matrix/artifacts/cycles/rust/dependencies/tokio/1.32-to-1.40.md`

   - **If exists:** Load cached migration notes
   - **If missing AND major/minor bump:** Research breaking changes, write guide
   - **If patch only:** No research needed, note as safe to apply

   **Apoc reports:**
   - Dependencies with major version bumps (research required)
   - Dependencies with minor version bumps (light research)
   - Dependencies with patch bumps (apply directly)
   - Security vulnerabilities (priority)

   Output: Dependency upgrade list with migration notes

### Phase 4: Architecture Review & Linter Audit

4. **Dispatch Architect** - Create upgrade plan AND audit current linter state

   **Linter audit (run on current codebase):**
   - Run the ecosystem linter (clippy, eslint, golangci-lint, ruff, etc.)
   - Capture all warnings, especially deprecation warnings
   - Search for lint suppression comments/attributes:
     - **Rust:** `#[allow(...)]`, `#![allow(...)]`, `// clippy::...`
     - **Node:** `// eslint-disable`, `.eslintrc` rules
     - **Go:** `//nolint:...`, `.golangci.yml` exclusions
     - **Python:** `# noqa`, `# type: ignore`, `pyproject.toml` tool configs
   - **Goal: Remove suppressions, fix underlying issues**
     - Identify suppressions that can now be removed (code can be fixed)
     - Plan removal of deprecated lint rules
     - Document what each suppression was hiding and how to fix it
   - Create cleanup tasks for Ramakandra

   **Architecture review:**
   - Review toolchain migration guide
   - Review dependency migration notes
   - Assess project-specific impact
   - Identify files/modules affected
   - Propose phased approach:
     1. Patch bumps (low risk, batch together)
     2. Minor bumps (medium risk, group by subsystem)
     3. Major bumps (high risk, one at a time)
     4. Toolchain upgrade (after deps stable)
     5. Linter cleanup (Ramakandra handles suppressions/deprecations)
   - Flag any blockers or risks

   Output: High-level upgrade plan + linter audit report

### Phase 5: Create Issues

5. **Neo creates issue markdown files** in `~/.matrix/cache/cycle/<project>/issues/`
   - Follow pattern from Broadcast program
   - Group patch bumps into single issue
   - Separate issues for major dependency upgrades
   - Toolchain upgrade as final issue (depends on others)
   - Include: context, steps, acceptance criteria
   - Assign: Smith for implementation, Deus for verification

### Phase 6: User Approval

6. **Neo presents plan to kautau**
   - Current state → Target state
   - Toolchain upgrade summary
   - Dependency changes (major/minor/patch counts)
   - Security fixes (if any)
   - Issue list with assignments
   - Wait for approval

### Phase 7: Push Issues

7. **Dispatch Kid** - Create issues on GitHub
   ```bash
   mx sync labels <owner/repo>
   mx convert md2yaml ~/.matrix/cache/cycle/<project>/issues/
   mx sync push <owner/repo> -i ~/.matrix/cache/cycle/<project>/issues/
   ```

## Key Rules

- **Cache first** - don't re-research known migrations
- **Skip patch versions** - no research needed, just apply
- **Major/minor only** - research and document these
- **Ecosystem context** - Tank researches full stack, not just language
- **Tools matter** - Apoc uses ecosystem-specific audit tools
- Migration guides are reusable across projects
- User approval required before creating issues

## Directory Structure

```
~/.matrix/artifacts/cycles/
├── rust/
│   ├── 1.75-to-1.83.md           # Toolchain migration
│   ├── edition-2021-to-2024.md   # Edition migration
│   ├── dependencies/
│   │   ├── tokio/
│   │   │   └── 1.32-to-1.40.md
│   │   ├── serde/
│   │   │   └── 1.0-to-2.0.md
│   │   └── clap/
│   │       └── 4.4-to-4.5.md
│   └── lints/
│       ├── clippy-too-many-arguments.md
│       ├── clippy-should-implement-trait.md
│       └── clippy-large-enum-variant.md
├── node/
│   ├── 18-to-22.md
│   ├── react-18-to-19.md         # Framework migrations at type level
│   ├── next-14-to-15.md
│   ├── dependencies/
│   │   └── axios/
│   │       └── 0.x-to-1.x.md
│   └── lints/
│       └── eslint-no-unused-vars.md
└── go/
    ├── 1.21-to-1.23.md
    ├── dependencies/
    │   └── ...
    └── lints/
        └── ...
```

## Example

```
/load cycle base-d

→ Detects: Rust project, MSRV 1.75, cargo
→ Tank: Latest stable is 1.83.0
  → Cache miss: Researches rust 1.75→1.83, writes guide
→ Apoc: Runs cargo outdated, cargo audit
  → tokio 1.32→1.40 (minor, cache hit)
  → serde 1.0.193→1.0.210 (patch, skip research)
  → clap 4.4→4.5 (minor, cache miss, researches)
→ Architect: Plans upgrade sequence
  1. Patch bumps (serde, etc) - single PR
  2. Minor bumps (tokio, clap) - grouped PR
  3. Rust 1.83 upgrade - final PR
→ Neo: Creates 3 issues
→ kautau: Approves
→ Kid: Pushes to GitHub
```
