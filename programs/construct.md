# Program: Construct

**Trigger:** "Construct", "Load the construct", "Is this ready to ship?", "Full project audit"

**Purpose:** Load the project into the construct and examine it from every angle. This is observation only - no changes are made. Recommendations are stored for later execution.

**Output location:** `{storage}/cache/construct/<project-name>/`

Where `{storage}` is:
- `~/.matrix-private/` for work repos (`~/work/*/` except `~/work/personal/`)
- `~/.matrix/` for personal/open source repos

## Steps

### Phase 0: Locate

> See `lib/locate.md` for project detection logic.

Output: Absolute path to repo, project name

### Phase 1: Architecture
1. **Dispatch Architect** - Analyze repo structure, produce two deliverables:
   - Input: repo path
   - **Output 1:** `architecture-diagram.md` - Visual representation of the project
     - ASCII or mermaid diagram
     - Component map
     - Data flows between components
     - Module boundaries
   - **Output 2:** `architecture-recommendations.md` - Architect's assessment
     - Is the structure optimal? Should files be moved or reorganized?
     - Are names clear and consistent? Should anything be renamed?
     - Do module boundaries make sense?
     - Are there circular dependencies or coupling issues?
     - Specific recommendations for structural improvements
2. **Neo reviews** - Verify diagram makes sense, ask clarifying questions if needed

### Phase 2: Documentation Review (parallel with Phase 3)
3. **Dispatch Morpheus** - Review documentation gaps
   - Input: architecture diagram, repo path
   - Reviews: README accuracy, --help text, code comments, module docs
   - Output: `docs-recommendations.md` - what needs updating (does NOT make changes)

### Phase 3: User Experience Review (parallel with Phase 2)
4. **Dispatch Persephone** - Review UX and tone
   - Input: repo path, any CLI/UI surfaces
   - Reviews: CLI output, error messages, help text tone, user flows
   - Output: `ux-recommendations.md` - friction points, suggested improvements

### Phase 4: Code Quality & Performance Review (parallel)
5. **Dispatch in parallel:**
   - **Deus** - Analyze tests, linting, formatting
     - Input: architecture diagram, repo path
     - Actions: run tests, run linters, check formatting
     - Reviews: test coverage, linting rules, code style consistency, test patterns
     - Output: `quality-recommendations.md` - coverage gaps, linting issues, formatting fixes
   - **Kamala** - Analyze performance and benchmarks
     - Input: architecture diagram, repo path
     - Actions: identify benchmarks, profile hotspots, check perf antipatterns
     - Reviews: benchmark coverage, algorithmic complexity, memory patterns, async efficiency
     - Output: `performance-recommendations.md` - missing benchmarks, optimization opportunities, perf antipatterns

### Phase 5: Security Review
6. **Dispatch Cypher** - Security audit
   - Input: architecture diagram, repo path
   - Reviews: auth flows, input validation, secrets handling, dependency vulnerabilities
   - Output: `security-findings.md` - vulnerabilities (critical/high/medium/low)

### Phase 6: Health Checks (parallel)
7. **Dispatch in parallel:**
   - **Apoc** → `dependencies.md` - Outdated packages? npm/cargo/pip warnings? What can we update? CVEs in deps?
   - **Merovingian** → `integrations.md` - API calls accurate? Legacy endpoints? Deprecated APIs? External service health?
   - **Ramakandra** → `tech-debt.md` - Legacy code? Old patterns? Outdated build systems? Code that should be refactored?
   - **Trainman** → `cross-platform.md` - Works on all platforms? Platform-specific code that could be generic? OS assumptions?
   - **Trinity** → `error-handling.md` - Error handling patterns? Logging coverage? Debug-ability? Stack traces useful? Recovery paths?
   - **Lock** → `compliance.md` - RFC compliance? OAuth/JWT specs followed? HTTP conventions? REST standards? API design patterns?
   - **Keymaker** → `auth-review.md` - Auth design patterns? Token flows correct? Session handling? Encryption choices appropriate? Secrets rotation?
   - **Librarian** → `data-review.md` - Schema design? Query efficiency? N+1 problems? Index coverage? Migration safety? Data integrity constraints?
   - **Niobe** → `cicd-review.md` - Pipeline efficiency? Duplicated jobs? Caching opportunities? Job parallelization? Quality gates configured? Branch protection? Required checks? .gitignore complete? Release automation?
   - **Seraph** → `devex-review.md` - Shell scripts correct? Setup scripts work? Makefiles? .env.example? Can a dev clone and run?
   - **Zee** → `accessibility.md` - WCAG compliance? Screen reader support? Keyboard navigation? i18n/l10n? Color contrast?
   - **Twins** → `format-review.md` - Right language choices? File format appropriate? Should this be TypeScript? JSON vs YAML vs TOML?
   - **Mouse** → `test-data-review.md` - Test fixtures realistic? Mocks representative? Edge cases in test data? Seed data quality?

### Phase 7: Perspectives (parallel)
8. **Dispatch in parallel:**
   - **Sati** → `perspective-sati.md` - Fresh eyes, what's exciting, what could be simpler?
   - **Spoon** → `perspective-spoon.md` - What assumptions created this? Alternative framings?
   - **Oracle** → `perspective-oracle.md` - What paths weren't taken? What's unseen?

### Phase 8: Synthesis
9. **Neo synthesizes** - Read all outputs from cache, produce:
   - `synthesis.md` containing:
     - Blockers (must fix before ship)
     - Improvements (should fix)
     - Ideas (could explore later)

   **Synthesis rules:**
   - **All perspectives inform, none override.** Spoon reframes but doesn't veto. Oracle explores but doesn't dictate. Sati observes but doesn't decide. Neo weighs all inputs.
   - **Present all findings.** Even if Spoon says "this isn't a problem in this context," the finding still gets documented. Context matters, but so does completeness.
   - **Distinguish context from dismissal.** "This threat model doesn't apply here" is useful context. "There are no issues" is dismissal. Include the former, reject the latter.
   - **Improvements are worth tracking.** Even if something "works," an improvement that makes it clearer, safer, or more maintainable is still valuable.

10. **Decision** - Ship, iterate, or revisit
11. **Execution** - If proceeding, dispatch Smith with specific recommendations to implement

## Key Rules

- This path is REVIEW ONLY - no code/doc changes during the path
- All outputs go to `{storage}/cache/construct/<project-name>/`
- Phases 2 & 3 run in parallel (docs + UX)
- Phase 4 runs Deus + Kamala in parallel (quality + performance)
- Phase 6 runs all thirteen in parallel (health checks)
- Phase 7 runs all three in parallel (perspectives)
- Architecture diagram (`architecture-diagram.md`) is the shared artifact that flows through phases
- Each identity reports back with "Knock knock, Neo."
- Execution happens AFTER synthesis, as a separate decision

## Example Dispatch

```
Task: Architect
Prompt: "Analyze ~/work/personal/code/matrix and produce two deliverables:

1. architecture-diagram.md - Visual diagram showing directory structure,
   module responsibilities, data flows between components.

2. architecture-recommendations.md - Your assessment of the structure.
   Is it optimal? Naming issues? Coupling problems? Specific recommendations.

Save both to {storage}/cache/construct/matrix/
(Use ~/.matrix-private/ for client work, ~/.matrix/ for personal/open source)
End with 'Knock knock, Neo.'"
```
