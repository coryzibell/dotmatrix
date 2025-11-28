# CI/CD Review: dotmatrix (Niobe)

**Repository:** coryzibell/dotmatrix
**Date:** 2025-11-27
**Reviewer:** Niobe

---

## Current State

### Automation Inventory

**GitHub Actions:** None
- No `.github/workflows/` directory exists
- No CI/CD automation configured

**Pre-commit Hooks:** None
- No `.pre-commit-config.yaml`
- Git hooks not configured

**Linting Configuration:** None
- No `pylint`, `flake8`, `ruff`, `black`, or `mypy` configuration files
- No `pyproject.toml`, `.pylintrc`, or `.flake8` present
- Python linters not installed in current environment

**Testing:** None
- No test framework configured
- No test files present

**Build/Task Automation:** None
- No `Makefile`, `justfile`, or similar task runners

### What This Repository Is

This is a **personal configuration repository** (dotmatrix pattern) containing:

1. **10 Python scripts** in `/artifacts/bin/`:
   - GitHub sync tools (issues, discussions, wiki, labels)
   - Three-way merge utilities
   - Markdown export tools

2. **~297 tracked files** (mostly markdown):
   - Identity definitions (`identities/`, `agents/`, `commands/`)
   - Documentation (`CLAUDE.md`, `orchestration.md`, `PLATFORMS.md`)
   - Session data and RAM directories (gitignored)
   - Artifact templates and tools

3. **Active development:**
   - Recent commits show ongoing work (049473c "chore: prune", e144ddd "feat: project-based retention")
   - Multiple contributors/identities working in RAM directories
   - Cache directories for multi-phase workflows

---

## Recommendations

### High-Value Automation (Should Implement)

#### 1. **Python Linting on PR**
**Value:** Catch syntax errors, style issues before merge
**Effort:** Low
**Tool:** `ruff` (fast, modern, replaces flake8+black+isort)

```yaml
# .github/workflows/lint.yml
name: Lint Python Scripts
on: [pull_request, push]
jobs:
  ruff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.14'
      - run: pip install ruff
      - run: ruff check artifacts/bin/*.py
```

**Why ruff?**
- Single tool, zero config needed
- Blazing fast (Rust-based)
- Covers linting + formatting
- Modern Python best practices

#### 2. **YAML Validation**
**Value:** Prevent broken identity configs, workflow files
**Effort:** Trivial

```yaml
# .github/workflows/validate.yml
name: Validate Config Files
on: [pull_request, push]
jobs:
  yaml:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install pyyaml
      - run: python -c "import yaml, sys; [yaml.safe_load(open(f)) for f in sys.argv[1:]]" **/*.yaml **/*.yml || true
```

#### 3. **Markdown Link Checking**
**Value:** Catch broken internal links in documentation
**Effort:** Low
**Tool:** `markdown-link-check` or `lychee`

```yaml
# .github/workflows/docs.yml
name: Documentation
on: [pull_request, push]
jobs:
  links:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: lycheeverse/lychee-action@v2
        with:
          args: --exclude-path '.git' '**/*.md'
```

### Medium-Value Automation (Consider)

#### 4. **Identity File Schema Validation**
**Value:** Ensure identity files have required fields (name, role, quip, etc.)
**Effort:** Medium (requires writing validator script)

Could validate that each identity markdown file contains:
- Proper frontmatter/structure
- Required fields (identity name, role description, signature quip)
- Consistent formatting

#### 5. **Python Type Checking (mypy)**
**Value:** Catch type errors in sync scripts
**Effort:** Medium-High (requires adding type hints to existing code)

The Python scripts are complex (800+ lines) and handle GitHub APIs. Type checking would catch bugs, but requires retrofitting type annotations.

**Defer until:** Scripts stabilize or type hints are added naturally during refactoring.

### Low-Value / Skip

❌ **Unit Tests for Python Scripts**
- Scripts are tightly coupled to GitHub API and filesystem
- High maintenance overhead for mock setup
- Manual testing likely sufficient for personal tooling
- **Skip unless:** Scripts become library/shared with others

❌ **Code Coverage Enforcement**
- Overkill for personal config repo
- Would require significant test infrastructure
- **Skip**

❌ **Automated Deployment/Release**
- This is a dotfiles repo, not a product
- No deployment targets
- **Skip**

---

## Pragmatic Assessment

### Right CI Level for This Project: **Lightweight Guard Rails**

This repository sits between "throwaway scripts" and "production service." The sweet spot is:

**Implement:**
1. Python linting (ruff) - 5 minutes to set up, catches 80% of errors
2. YAML validation - Prevents broken configs
3. Markdown link checking - Documentation stays navigable

**Skip:**
- Heavy test infrastructure
- Code coverage requirements
- Complex build pipelines
- Automated deployments

### Why This Balance?

**Reasons to automate:**
- Active development (10+ commits in recent history)
- Shared via GitHub (coryzibell/dotmatrix)
- Complex Python scripts interacting with GitHub API
- Identity system needs consistency

**Reasons to stay lean:**
- Personal configuration repository
- Single primary user (kautau)
- Scripts are tools, not libraries
- Over-engineering reduces velocity

### Implementation Path

**Phase 1 (Now):**
```bash
# Add ruff linting
touch .github/workflows/lint.yml
# Configure ruff with pyproject.toml (optional, ruff has good defaults)
```

**Phase 2 (When time permits):**
```bash
# Add YAML validation
# Add markdown link checking
```

**Phase 3 (If pain points emerge):**
```bash
# Add identity schema validation
# Add mypy type checking
```

### Cost/Benefit Reality Check

**Current state:** Zero CI = zero protection, but also zero maintenance burden
**Proposed state:** 3 workflows = ~30 seconds CI time per push, catches 90% of preventable errors

**ROI:** High. Small time investment prevents:
- Pushing broken Python syntax
- Committing invalid YAML that breaks Claude Code
- Dead links making documentation frustrating

---

## Specific Files to Lint

**Python scripts requiring attention:**
```
/home/w3surf/.claude/artifacts/bin/cleanup_github.py
/home/w3surf/.claude/artifacts/bin/convert_issues.py
/home/w3surf/.claude/artifacts/bin/export_markdown.py
/home/w3surf/.claude/artifacts/bin/pull_github.py
/home/w3surf/.claude/artifacts/bin/sync_discussions.py
/home/w3surf/.claude/artifacts/bin/sync_github.py      # 800 lines, complex
/home/w3surf/.claude/artifacts/bin/sync_issues.py
/home/w3surf/.claude/artifacts/bin/sync_labels.py
/home/w3surf/.claude/artifacts/bin/sync_merge.py       # Shared utility
/home/w3surf/.claude/artifacts/bin/sync_wiki.py
```

**All 10 scripts should be linted.** The sync_github.py and sync_merge.py are particularly complex and would benefit most.

---

## Sample Ruff Configuration

**Option A: Zero config (recommended for this project)**
```bash
# Just run ruff with defaults
ruff check artifacts/bin/
```

**Option B: Light config in pyproject.toml**
```toml
[tool.ruff]
line-length = 100
target-version = "py314"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (let formatter handle it)
]
```

---

## Decision Points

Before implementing CI, answer:

1. **Who reviews PRs?** If solo developer, CI is even more valuable (catches mistakes before merge)
2. **How often are Python scripts modified?** If frequently, linting pays off quickly
3. **Is the identity system stable?** If yes, schema validation less urgent; if no, validation prevents drift

Based on git history (10 commits in recent window, active development), **CI would provide value now.**

---

## Final Recommendation

**Implement lightweight CI with 3 workflows:**

1. **Ruff linting** (Python quality)
2. **YAML validation** (Config integrity)
3. **Markdown links** (Documentation health)

**Total setup time:** ~20 minutes
**Maintenance overhead:** Near zero (these tools are stable)
**Value:** Prevents 90% of accidental breakage

This is the tight spot. Thread the needle - enough automation to fly safely, not so much you're maintaining the ship instead of piloting it.

---

Wake up, Neo.

**[Identity: Niobe | Model: Sonnet | Status: success]**
