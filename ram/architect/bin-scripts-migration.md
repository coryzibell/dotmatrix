# Python Script Migration Plan
*Architect Decision Record*
*Created: 2025-11-29*

## Overview

Migration of Python utility scripts from `~/.matrix/artifacts/bin/` to native Rust in the mx CLI. The goal is to consolidate tooling, eliminate Python runtime dependencies, and leverage existing mx infrastructure (REST/GraphQL clients, YAML store, token auth).

**Total Scripts:** 7
**Estimated Issues:** 11 (grouped logically by domain)

---

## Script Analysis

### 1. cleanup_github.py
**Purpose:** Close issues and delete discussions by number
**Complexity:** Low
**Dependencies:** GitHub REST API (close issues), GraphQL (delete discussions)
**Reusable Infrastructure:**
- `sync::github::rest::RestClient` for issue operations
- `sync::github::graphql::GraphQLClient` for discussion deletion
- `sync::github::auth::get_github_token()` for authentication

**Notes:**
- Combines two operations: closing issues (REST PATCH) and deleting discussions (GraphQL mutation)
- Uses label "duplicate" when closing
- Pattern: fetch discussion ID via GraphQL query, then mutate

---

### 2. convert_issues.py (md2yaml)
**Purpose:** Convert structured markdown to YAML for GitHub API consumption
**Complexity:** Medium
**Dependencies:** Regex parsing, YAML serialization
**Reusable Infrastructure:**
- `sync::yaml::schema::IssueYaml` types (extend as needed)
- Standard Rust regex and serde_yaml

**Notes:**
- Parses specific markdown format with sections (Context, Problem, Solution, etc.)
- Extracts metadata (Type, Labels), implementation steps, acceptance criteria, handoff workflow
- Generates `body_markdown` field for GitHub rendering
- Known identity detection for handoff workflow

---

### 3. export_markdown.py
**Purpose:** Convert YAML issue/discussion files to readable markdown
**Complexity:** Medium
**Dependencies:** YAML deserialization, markdown generation
**Reusable Infrastructure:**
- `sync::yaml::schema::IssueYaml` for reading
- `sync::yaml::store::YamlStore` for batch operations

**Notes:**
- Inverse of convert_issues.py
- Formats dates from ISO8601 to human-readable
- Extracts repo info from various YAML fields
- Builds GitHub URLs for issues/discussions
- Includes comments section

---

### 4. extract-session.py
**Purpose:** Extract Claude Code session JSONL to readable markdown
**Complexity:** Low
**Dependencies:** JSONL parsing, filesystem operations
**Reusable Infrastructure:**
- None (session-specific, not GitHub-related)

**Notes:**
- Parses `~/.claude/projects/-home-w3surf/*.jsonl`
- Extracts human/assistant messages, tool uses, summaries
- Filters out agent sessions (files starting with `agent-`)
- Summarizes tool calls (Edit, Write, Read, Bash, Task)
- Useful for debugging and session review

---

### 5. health_check.py
**Purpose:** Verify dotmatrix environment setup
**Complexity:** Low
**Dependencies:** File system checks, env var validation
**Reusable Infrastructure:**
- `sync::github::auth::get_github_token()` for token validation

**Notes:**
- Checks for required files (`~/.claude/agents/`, config files, etc.)
- Validates GitHub token format (ghp_ or github_pat_ prefix)
- Verifies RAM directories
- CLI health check pattern, useful as `mx doctor` or `mx health`

---

### 6. matrix_client.py
**Purpose:** Post comments as dotmatrix-ai GitHub App bot
**Complexity:** Medium-High
**Dependencies:** JWT signing (RS256), GitHub App auth, GraphQL mutations
**Reusable Infrastructure:**
- Can extend `sync::github::auth` with App authentication
- Reuse `sync::github::graphql::GraphQLClient`

**Notes:**
- Requires JWT library (e.g., `jsonwebtoken` crate)
- Exchanges JWT for installation token (cached, refreshed 5 min before expiry)
- Posts to issues (REST) or discussions (GraphQL)
- Optional identity signatures in comment body
- Env vars: DOTMATRIX_APP_ID, DOTMATRIX_INSTALLATION_ID, DOTMATRIX_PRIVATE_KEY

---

### 7. sync_wiki.py
**Purpose:** Sync markdown documentation to GitHub wiki
**Complexity:** Medium
**Dependencies:** Git operations, temporary directories
**Reusable Infrastructure:**
- `sync::github::auth::get_github_token()` for auth
- Standard library for git subprocess calls

**Notes:**
- Clones wiki repo (shallow), copies markdown files, commits, pushes
- Supports single file or directory sync
- Sanitizes page names for wiki compatibility
- Uses git CLI (not libgit2) - subprocess approach
- Configurable git user for commits

---

## Migration Strategy

### Phase 1: Core GitHub Operations (Issues 1-3)
Foundation operations that extend existing sync infrastructure.

**Issue 1: GitHub Cleanup Subcommand**
- Command: `mx github cleanup <repo> --issues 1,2,3 --discussions 4,5,6`
- Close issues with "duplicate" label
- Delete discussions via GraphQL
- Reuse REST/GraphQL clients

**Issue 2: Session Export Tool**
- Command: `mx session export [session-file]`
- Extract JSONL → markdown
- Default to most recent non-agent session
- Output to `~/.matrix/cache/sessions/`

**Issue 3: Environment Health Check**
- Command: `mx doctor` or `mx health`
- Check file structure, GitHub token, directories
- Colorized output (when tty)
- Exit codes for scripting

---

### Phase 2: YAML/Markdown Conversion (Issues 4-5)
Format conversion utilities for issue management.

**Issue 4: Markdown → YAML Converter**
- Command: `mx convert md2yaml <input-dir> [output-dir]`
- Parse structured markdown to YAML
- Extend `sync::yaml::schema` as needed
- Batch processing

**Issue 5: YAML → Markdown Exporter**
- Command: `mx convert yaml2md <yaml-dir> [output-dir]`
- Generate readable markdown from YAML
- Date formatting, URL building
- Comments support

---

### Phase 3: GitHub App Integration (Issues 6-7)
Advanced authentication and bot operations.

**Issue 6: GitHub App Authentication Module**
- New module: `sync::github::app_auth`
- JWT signing with RS256
- Installation token exchange and caching
- Token refresh logic (5 min buffer)

**Issue 7: GitHub App Comment Posting**
- Command: `mx github comment issue <repo> <number> <message> [--identity NAME]`
- Command: `mx github comment discussion <repo> <number> <message> [--identity NAME]`
- Uses App auth module
- Identity signature formatting

---

### Phase 4: Git Operations (Issues 8-9)
Wiki sync and git-based workflows.

**Issue 8: Wiki Sync Infrastructure**
- New module: `sync::wiki`
- Git subprocess wrapper (not libgit2)
- Temporary directory management
- Page name sanitization

**Issue 9: Wiki Sync Command**
- Command: `mx wiki sync <repo> <source> [--page-name NAME]`
- Clone, copy, commit, push workflow
- Single file or directory mode
- Dry-run support

---

### Phase 5: Refinement & Integration (Issues 10-11)

**Issue 10: Unified Conversion Subcommand**
- Consolidate under `mx convert`:
  - `mx convert md2yaml <input> [output]`
  - `mx convert yaml2md <input> [output]`
- Consistent CLI patterns
- Shared conversion utilities module

**Issue 11: Testing & Documentation**
- Integration tests for each subcommand
- Update README with new commands
- Migration guide for Python script users
- Document deprecation of Python scripts

---

## Issue Breakdown

### Issue 1: GitHub Cleanup Subcommand
**Title:** Add `mx github cleanup` for closing issues and deleting discussions
**Type:** `enhancement`
**Labels:** `github`, `cli`, `rust-migration`

**Context:**
Replace `cleanup_github.py` with native Rust implementation in mx CLI.

**Implementation:**
1. Add `mx github cleanup <repo>` subcommand
2. Accept `--issues <numbers>` and `--discussions <numbers>` flags
3. Use existing `RestClient` to close issues (PATCH with state=closed, labels=[duplicate])
4. Use existing `GraphQLClient` to:
   - Query discussion ID from number
   - Mutate to delete discussion
5. Display progress with ✓/✗ indicators

**Acceptance Criteria:**
- [ ] Command closes issues with duplicate label
- [ ] Command deletes discussions via GraphQL
- [ ] Errors are reported per-item without failing entire batch
- [ ] Output matches Python script format

**Handoff:**
Smith for implementation.

---

### Issue 2: Session Export Tool
**Title:** Add `mx session export` for extracting Claude JSONL sessions
**Type:** `enhancement`
**Labels:** `cli`, `utilities`, `rust-migration`

**Context:**
Replace `extract-session.py` with native Rust for debugging and session review.

**Implementation:**
1. Add `mx session export [path]` subcommand
2. Default to most recent non-agent session in `~/.claude/projects/-home-w3surf/`
3. Parse JSONL, extract user/assistant messages
4. Summarize tool uses (Edit, Write, Read, Bash, Task)
5. Output to `~/.matrix/cache/sessions/session-export-<timestamp>.md`
6. Filter out system-reminder blocks

**Acceptance Criteria:**
- [ ] Exports most recent session by default
- [ ] Handles custom path argument
- [ ] Filters agent sessions
- [ ] Summarizes tool calls
- [ ] Outputs readable markdown

**Handoff:**
Smith for implementation.

---

### Issue 3: Environment Health Check
**Title:** Add `mx doctor` environment health check
**Type:** `enhancement`
**Labels:** `cli`, `diagnostics`, `rust-migration`

**Context:**
Replace `health_check.py` with native Rust diagnostic command.

**Implementation:**
1. Add `mx doctor` (or `mx health`) subcommand
2. Check required files:
   - `~/.matrix/agents/neo.md`, `_base.md`
   - `~/.matrix/artifacts/etc/*.yaml`
   - `~/.claude/CLAUDE.md`, `orchestration.md`, `paths.md`
3. Verify RAM directories (`~/.matrix/ram/neo/`)
4. Validate GitHub token (format check: `ghp_` or `github_pat_` prefix)
5. Colorize output when stdout is tty
6. Exit code 0 if healthy, 1 if issues

**Acceptance Criteria:**
- [ ] Checks all required files and directories
- [ ] Validates GitHub token format
- [ ] Colorized output on tty
- [ ] Returns appropriate exit codes
- [ ] Lists specific missing/invalid items

**Handoff:**
Smith for implementation.

---

### Issue 4: Markdown to YAML Converter
**Title:** Add `mx convert md2yaml` for issue format conversion
**Type:** `enhancement`
**Labels:** `conversion`, `yaml`, `rust-migration`

**Context:**
Replace `convert_issues.py` (md2yaml) with native Rust converter.

**Implementation:**
1. Add `mx convert md2yaml <input-dir> [output-dir]` subcommand
2. Parse markdown with sections:
   - Extract title from `# Heading`
   - Parse `**Type:** \`issue\`` metadata
   - Parse `**Labels:** \`label1\`, \`label2\``
   - Extract sections: Context, Problem, Solution, Implementation Steps, Acceptance Criteria, Handoff
3. Generate YAML using `sync::yaml::schema::IssueYaml`
4. Support numbered lists, checkboxes, identity detection in handoff
5. Preserve original markdown as `body_markdown` field

**Acceptance Criteria:**
- [ ] Parses structured markdown format
- [ ] Extracts metadata, sections, structured content
- [ ] Generates valid YAML for GitHub API
- [ ] Batch processes directory of .md files
- [ ] Reports success/failure per file

**Handoff:**
Smith for implementation. Extend `sync::yaml::schema` as needed.

---

### Issue 5: YAML to Markdown Exporter
**Title:** Add `mx convert yaml2md` for human-readable export
**Type:** `enhancement`
**Labels:** `conversion`, `yaml`, `rust-migration`

**Context:**
Replace `export_markdown.py` with native Rust exporter.

**Implementation:**
1. Add `mx convert yaml2md <yaml-dir> [output-dir]` subcommand
2. Read YAML files using `YamlStore`
3. Generate markdown with:
   - Title, Type, Labels, Status, GitHub URL
   - Body content
   - Comments section (author, date, body)
   - Footer with last synced timestamp
4. Format dates from ISO8601 to human-readable
5. Extract repo info and build GitHub URLs

**Acceptance Criteria:**
- [ ] Converts YAML to readable markdown
- [ ] Formats dates properly
- [ ] Builds correct GitHub URLs
- [ ] Includes comments if present
- [ ] Batch processes directory

**Handoff:**
Smith for implementation.

---

### Issue 6: GitHub App Authentication Module
**Title:** Implement GitHub App JWT authentication
**Type:** `enhancement`
**Labels:** `github`, `auth`, `rust-migration`

**Context:**
Add GitHub App authentication to support bot operations (matrix_client.py replacement).

**Implementation:**
1. Create `sync::github::app_auth` module
2. Add dependency: `jsonwebtoken` crate for RS256 JWT signing
3. Implement:
   - `generate_jwt(app_id, private_key) -> String`
   - `get_installation_token(app_id, installation_id, private_key) -> String`
   - Token caching with 5-minute expiry buffer
4. Read from env vars:
   - `DOTMATRIX_APP_ID`
   - `DOTMATRIX_INSTALLATION_ID`
   - `DOTMATRIX_PRIVATE_KEY` (full PEM)
5. Extend `RestClient` and `GraphQLClient` to accept App tokens

**Acceptance Criteria:**
- [ ] Generates valid RS256 JWTs
- [ ] Exchanges JWT for installation token
- [ ] Caches tokens and refreshes before expiry
- [ ] Reads from environment variables
- [ ] Integrates with existing REST/GraphQL clients

**Handoff:**
Smith for implementation. Add `jsonwebtoken = "9"` to Cargo.toml.

---

### Issue 7: GitHub App Comment Posting
**Title:** Add `mx github comment` for bot posting
**Type:** `enhancement`
**Labels:** `github`, `bot`, `rust-migration`

**Context:**
Replace `matrix_client.py` with native Rust for posting as dotmatrix-ai bot.

**Implementation:**
1. Add `mx github comment` subcommand:
   - `mx github comment issue <repo> <number> <message> [--identity NAME]`
   - `mx github comment discussion <repo> <number> <message> [--identity NAME]`
2. Use App authentication from Issue 6
3. Format messages with identity signatures:
   ```
   **[{identity}]**

   {message}

   ---
   *Posted by dotmatrix-ai • Identity: {identity}*
   ```
4. Post to issues via REST API
5. Post to discussions via GraphQL (addDiscussionComment mutation)

**Acceptance Criteria:**
- [ ] Posts comments to issues
- [ ] Posts comments to discussions
- [ ] Optional identity signatures
- [ ] Returns comment URL on success
- [ ] Proper error handling

**Dependencies:**
- Issue 6 (App auth module)

**Handoff:**
Smith for implementation.

---

### Issue 8: Wiki Sync Infrastructure
**Title:** Add wiki sync module with git operations
**Type:** `enhancement`
**Labels:** `wiki`, `git`, `rust-migration`

**Context:**
Create infrastructure for wiki sync (sync_wiki.py replacement).

**Implementation:**
1. Create `sync::wiki` module
2. Implement git subprocess wrapper:
   - `clone_wiki(owner, repo, token, target_dir) -> Result<()>`
   - `commit_and_push(wiki_dir, message) -> Result<()>`
   - `run_git(args, cwd) -> Result<Output>`
3. Page name sanitization (spaces → hyphens, alphanumeric only)
4. Temporary directory management using `tempfile` crate
5. Configure git user for commits (neo@construct.local)

**Acceptance Criteria:**
- [ ] Clones wiki repos with authentication
- [ ] Runs git commands in specified directories
- [ ] Sanitizes wiki page names
- [ ] Manages temporary directories safely
- [ ] Configures git user for commits

**Handoff:**
Smith for implementation. Add `tempfile = "3"` to Cargo.toml.

---

### Issue 9: Wiki Sync Command
**Title:** Add `mx wiki sync` command
**Type:** `enhancement`
**Labels:** `wiki`, `cli`, `rust-migration`

**Context:**
Replace `sync_wiki.py` with native Rust wiki sync.

**Implementation:**
1. Add `mx wiki sync <repo> <source>` subcommand
2. Support flags:
   - `--page-name NAME` for single file sync
   - `--dry-run` to preview changes
3. Modes:
   - Single file: sync to specified page name
   - Directory: sync all .md files (skip numbered issue files)
4. Workflow:
   - Clone wiki to temp dir
   - Copy markdown files
   - Commit changes
   - Push to remote
5. Output wiki URL on success

**Acceptance Criteria:**
- [ ] Syncs single file with custom page name
- [ ] Syncs all .md files from directory
- [ ] Skips numbered issue files (e.g., 001-blocker-*.md)
- [ ] Dry-run mode shows what would change
- [ ] Returns wiki URL on success

**Dependencies:**
- Issue 8 (wiki infrastructure)

**Handoff:**
Smith for implementation.

---

### Issue 10: Unified Conversion Subcommand
**Title:** Consolidate conversion tools under `mx convert`
**Type:** `refactor`
**Labels:** `cli`, `ux`

**Context:**
Group md2yaml and yaml2md under consistent `mx convert` namespace.

**Implementation:**
1. Update CLI structure:
   ```
   mx convert md2yaml <input> [output]
   mx convert yaml2md <input> [output]
   ```
2. Create `convert` module with shared utilities:
   - Date formatting
   - Markdown parsing helpers
   - YAML validation
3. Consistent CLI patterns (input/output args, dry-run, etc.)

**Acceptance Criteria:**
- [ ] Both converters work under `mx convert`
- [ ] Shared utilities extracted to module
- [ ] Consistent help text and error messages

**Dependencies:**
- Issues 4 and 5

**Handoff:**
Smith for implementation.

---

### Issue 11: Testing & Documentation
**Title:** Tests and docs for Python script migration
**Type:** `documentation`
**Labels:** `testing`, `docs`

**Context:**
Ensure migrated commands are tested and documented.

**Implementation:**
1. Integration tests:
   - GitHub cleanup (mock GitHub API)
   - Session export (sample JSONL)
   - Health check (mock filesystem)
   - Converters (sample md/yaml fixtures)
   - Wiki sync (mock git operations)
2. Update README.md with new commands
3. Migration guide:
   - Map Python scripts to mx commands
   - Environment variable changes
   - Deprecation timeline
4. Update `mx --help` descriptions

**Acceptance Criteria:**
- [ ] Integration tests for all new commands
- [ ] README documents all new subcommands
- [ ] Migration guide published
- [ ] Help text is clear and complete

**Dependencies:**
- All previous issues

**Handoff:**
Smith for implementation. Oracle for documentation review.

---

## Implementation Order

**Recommended sequence:**

1. **Issue 3** (Health Check) - Independent, useful immediately
2. **Issue 2** (Session Export) - Independent, useful for debugging
3. **Issue 1** (GitHub Cleanup) - Extends existing sync infrastructure
4. **Issue 4** (md2yaml) - Foundation for conversion tools
5. **Issue 5** (yaml2md) - Complements Issue 4
6. **Issue 10** (Unified Conversion) - Refactor after 4 and 5
7. **Issue 6** (App Auth) - Foundation for bot operations
8. **Issue 7** (App Comments) - Depends on Issue 6
9. **Issue 8** (Wiki Infrastructure) - Foundation for wiki ops
10. **Issue 9** (Wiki Sync) - Depends on Issue 8
11. **Issue 11** (Testing & Docs) - Final polish

**Parallelization opportunities:**
- Issues 1, 2, 3 can run in parallel (independent)
- Issues 4, 5 can overlap (similar domain)
- Issues 6, 8 can overlap (different domains)

---

## Shared Infrastructure Reuse

| Python Script | Reusable mx Components |
|---------------|------------------------|
| cleanup_github.py | `sync::github::rest::RestClient`, `sync::github::graphql::GraphQLClient`, `sync::github::auth` |
| convert_issues.py | `sync::yaml::schema::IssueYaml`, serde_yaml |
| export_markdown.py | `sync::yaml::store::YamlStore`, `sync::yaml::schema` |
| extract-session.py | None (session-specific) |
| health_check.py | `sync::github::auth::get_github_token()` |
| matrix_client.py | `sync::github` (extend with app_auth), REST/GraphQL clients |
| sync_wiki.py | `sync::github::auth`, git subprocess wrapper |

**New modules needed:**
- `sync::github::app_auth` (GitHub App JWT)
- `sync::wiki` (git operations, wiki-specific logic)
- `convert` (consolidate md/yaml conversion)

---

## Deprecation Timeline

**Phase 1:** (Immediate)
- Keep Python scripts in place
- Add Rust equivalents with `mx` CLI

**Phase 2:** (After testing)
- Update documentation to prefer `mx` commands
- Add deprecation warnings to Python scripts

**Phase 3:** (1 month after Phase 2)
- Move Python scripts to `~/.matrix/artifacts/bin/deprecated/`
- Update any automation to use `mx`

**Phase 4:** (3 months after Phase 3)
- Remove Python scripts entirely
- Python becomes optional dependency

---

## Dependencies & Crates

**New Cargo dependencies:**
- `jsonwebtoken = "9"` (for GitHub App JWT signing)
- `tempfile = "3"` (for wiki temp directories)

**Existing dependencies:**
- `reqwest` (HTTP client)
- `serde`, `serde_yaml`, `serde_json` (serialization)
- `anyhow` (error handling)
- `clap` (CLI)

---

## Success Metrics

1. **Zero Python Runtime Dependency:** mx CLI is self-contained Rust binary
2. **Feature Parity:** All Python script functionality available in `mx`
3. **Performance:** Rust implementations ≥ Python (should be faster)
4. **User Adoption:** Automation scripts updated to use `mx`
5. **Documentation:** Clear migration guide, comprehensive help text

---

## Notes

**Architecture principles:**
- Reuse over reimplementation (extend existing sync infrastructure)
- Consistent CLI patterns (flags, dry-run, output formats)
- Modular design (new modules integrate cleanly)
- Error handling (anyhow::Result throughout)
- Testing (integration tests for each command)

**Deferred decisions:**
- Whether to support reading GitHub token from both env var and ~/.claude.json (Python scripts use ~/.claude.json, mx sync uses env var)
- Whether to consolidate under `mx github` vs separate top-level commands
- Whether to add `mx bot` namespace for App operations vs `mx github comment`

**Future enhancements:**
- Interactive mode for cleanup (confirm before deleting)
- Batch wiki sync across multiple repos
- Session export formats (JSON, HTML)
- Health check auto-repair mode
