# Program: Broadcast

**Trigger:** "Broadcast", "Create issues from construct", "Turn recommendations into tasks"

**Purpose:** Neo synthesizes construct outputs into actionable GitHub issues, each assigned to the identity best suited to execute it.

**Input:** `~/.matrix/cache/construct/<project-name>/` (output from Construct path)

**Output:** GitHub issues created on the repo with `identity:<name>` labels

## Steps

### Phase 0: Locate

> See `lib/locate.md` for project detection logic.

Output: Absolute path to repo, project name (used to find `~/.matrix/cache/construct/<project-name>/`)

### Phase 1: Read the Construct
1. **Neo reads all construct outputs:**

   **Architecture (Phase 1):**
   - `architecture-diagram.md` - visual system overview
   - `architecture-recommendations.md` - structural improvements

   **Docs & UX (Phases 2-3):**
   - `docs-recommendations.md` - what Morpheus found
   - `ux-recommendations.md` - what Persephone found

   **Quality & Performance (Phase 4):**
   - `quality-recommendations.md` - what Deus found (tests, linting, formatting)
   - `performance-recommendations.md` - what Kamala found (benchmarks, profiling)

   **Security (Phase 5):**
   - `security-findings.md` - what Cypher found

   **Health Checks (Phase 6):**
   - `dependencies.md` - Apoc on packages and CVEs
   - `integrations.md` - Merovingian on APIs and external services
   - `tech-debt.md` - Ramakandra on legacy code and patterns
   - `cross-platform.md` - Trainman on OS compatibility
   - `error-handling.md` - Trinity on error patterns and logging
   - `compliance.md` - Lock on RFC/spec compliance
   - `auth-review.md` - Keymaker on auth and encryption
   - `data-review.md` - Librarian on schemas and queries
   - `cicd-review.md` - Niobe on pipeline efficiency and quality gates
   - `devex-review.md` - Seraph on developer experience
   - `accessibility.md` - Zee on a11y and i18n
   - `format-review.md` - Twins on language and format choices
   - `test-data-review.md` - Mouse on fixtures and mocks

   **Perspectives (Phase 7):**
   - `perspective-sati.md` - fresh eyes, simplicity
   - `perspective-spoon.md` - alternative framings
   - `perspective-oracle.md` - paths not taken

   **Synthesis (Phase 8):**
   - `synthesis.md` - blockers, improvements, ideas

### Phase 2: Write Issue Markdown
2. **Neo writes issue `.md` files** to `~/.matrix/cache/construct/<project-name>/issues/`
   - One file per actionable item (e.g., `fix-command-injection.md`)
   - Follow template at `~/.matrix/artifacts/etc/issue-template.md`
   - Include: Context, Problem, Solution, Implementation Steps, Acceptance Criteria, Handoff
   - Add `**Labels:**` line with `identity:<name>` for assignment
   - Priority order: blockers first, then improvements, then ideas

### Phase 3: User Approval
3. **Neo presents issues to kautau for review**
   - List all issue titles with assigned identities
   - Wait for approval before proceeding
   - kautau can request changes or approve

### Phase 4: Convert and Sync
4. **Dispatch Kid** - Convert and push to GitHub
   ```bash
   # Sync labels first (ensure identity labels exist)
   python ~/.matrix/artifacts/bin/sync_labels.py <owner/repo>

   # Convert authored markdown to YAML
   python ~/.matrix/artifacts/bin/convert_issues.py ~/.matrix/cache/construct/<project>/issues/

   # Push to GitHub (unified script routes by type)
   python ~/.matrix/artifacts/bin/sync_github.py <owner/repo> ~/.matrix/cache/construct/<project>/issues/
   ```

   The unified `sync_github.py` routes based on `metadata.type`:
   - `type: issue` → GitHub Issues (REST API)
   - `type: idea` → GitHub Discussions (GraphQL API)

## Three-Way Merge Behavior

- Scripts store `last_synced` snapshot in YAML after each sync
- Before updating, compares: local (YAML) vs remote (GitHub) vs base (last_synced)
- **Auto-resolves:** When only one side changed a field
- **Prompts:** When both sides changed the same field (true conflict)
- Labels merge as sets: union of additions from both sides
- Respects remote changes - won't overwrite edits made directly on GitHub

## Key Rules

- Neo writes issue markdown - this requires Opus-level synthesis
- Each issue is self-contained with full execution instructions
- Issues link back to construct findings where relevant
- **User approval required** before creating issues on GitHub
- Kid handles script execution (convert + sync)
