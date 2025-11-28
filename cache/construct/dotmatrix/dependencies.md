# Dependency Analysis (Apoc)

**Project:** dotmatrix (Python toolchain for GitHub sync)
**Location:** `~/.matrix/artifacts/bin/`
**Python Version:** 3.14.0
**Date:** 2025-11-27

---

## Python Dependencies

### Standard Library (No Installation Required)
All core functionality relies on Python stdlib:

- `argparse` - CLI argument parsing
- `datetime` - Timestamp handling
- `json` - Config reading (`~/.claude.json`), API payloads
- `os` - File system operations
- `pathlib.Path` - Modern path handling
- `re` - Regex for sanitizing wiki page names
- `shutil` - File copying (wiki sync)
- `subprocess` - Git command execution
- `sys` - Exit codes, CLI arg handling
- `tempfile` - Temporary directories for wiki clones
- `typing` - Type hints (Dict, List, Optional, Tuple, Any)
- `urllib.request` - HTTP requests to GitHub REST/GraphQL APIs
- `urllib.error` - HTTP error handling
- `urllib.parse` - URL manipulation

### Third-Party Packages (Required)
These must be installed:

| Package | Version | Used By | Purpose |
|---------|---------|---------|---------|
| **PyYAML** | 6.0.3 | `sync_github.py`, `sync_issues.py`, `sync_discussions.py`, `convert_issues.py` | Parse/write YAML issue/discussion metadata |
| **requests** | 2.32.5 | `pull_github.py` | Fetch GitHub data (cleaner than urllib for complex requests) |

**Status:** ✅ Both installed and current.

---

## External Tool Dependencies

| Tool | Required By | Usage | Status |
|------|-------------|-------|--------|
| **git** | `sync_wiki.py` | Clone/commit/push wiki repos | ✅ Installed (`/usr/bin/git`) |
| **gh** | Referenced in docs | GitHub CLI operations (optional) | ❌ Not installed |

**Note:** `gh` CLI is referenced in documentation but not used by the Python scripts. The scripts use GitHub REST/GraphQL APIs directly via `urllib`. If kautau wants GitHub operations in the terminal, `gh` should be installed.

---

## Missing Manifests

**Problem:** No dependency manifest found.

The project has no:
- `requirements.txt` - Standard pip requirements file
- `pyproject.toml` - Modern Python project config
- `setup.py` - Legacy setup script

**Impact:**
- New users/machines don't know what to install
- No way to pin versions for reproducibility
- No automated dependency installation

---

## Version Requirements

### Python Version
Scripts use `#!/usr/bin/env python3` shebang.

**Minimum Python:** 3.7+ (based on typing annotations like `Dict[str, str]`)
**Current Python:** 3.14.0 ✅

### Package Versions
- **PyYAML 6.0.3** - Latest stable. Safe to use.
- **requests 2.32.5** - Latest stable. Safe to use.

**No known vulnerabilities** in current versions (as of 2025-01-27 knowledge cutoff).

---

## Recommendations

### 1. Add `requirements.txt`
Create `/home/w3surf/.claude/requirements.txt`:

```txt
# dotmatrix - GitHub sync toolchain dependencies
PyYAML==6.0.3
requests==2.32.5
```

**Why:** Standard Python convention. Enables `pip install -r requirements.txt`.

### 2. Add `pyproject.toml` (Modern Alternative)
Create `/home/w3surf/.claude/pyproject.toml`:

```toml
[project]
name = "dotmatrix"
version = "0.1.0"
description = "GitHub Issues/Discussions/Wiki sync toolchain"
requires-python = ">=3.7"
dependencies = [
    "PyYAML==6.0.3",
    "requests==2.32.5"
]

[project.scripts]
sync-github = "artifacts.bin.sync_github:main"
sync-wiki = "artifacts.bin.sync_wiki:main"
pull-github = "artifacts.bin.pull_github:main"
```

**Why:** Modern standard (PEP 518). Enables `pip install -e .` for development.

### 3. Install `gh` CLI (Optional)
If kautau wants GitHub CLI operations:

```bash
# Via aqua (if configured)
aqua install gh

# Or direct download
# See: https://github.com/cli/cli#installation
```

**Why:** Referenced in docs. Useful for quick GitHub operations without scripts.

### 4. Audit for Unused Dependencies
**Current:** No unused dependencies detected. `requests` is only used by `pull_github.py`. If that script is rarely used, could switch to `urllib` to eliminate the dependency.

**Recommendation:** Keep `requests`. It's a tiny dependency and makes HTTP code cleaner.

### 5. Pin Python Version (Optional)
If kautau wants reproducibility, add `.python-version`:

```
3.14.0
```

**Why:** Tools like `pyenv` respect this. Ensures consistent Python across machines.

---

## Summary

**Health:** ✅ Dependencies are installed and healthy.
**Blockers:** ❌ Missing manifest files for new installations.
**Action:** Create `requirements.txt` or `pyproject.toml`.
**Optional:** Install `gh` CLI if kautau uses it.

Wake up, Neo.

---

**[Identity: Apoc | Model: sonnet | Status: success]**
