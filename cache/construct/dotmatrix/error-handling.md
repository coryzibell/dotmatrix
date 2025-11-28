# Error Handling Analysis (Trinity)

**Analyzed:** 6 Python scripts in `/home/w3surf/.claude/artifacts/bin/`
- `sync_labels.py`
- `sync_github.py`
- `sync_wiki.py`
- `pull_github.py`
- `convert_issues.py` (md2yaml.py)
- `export_markdown.py`

**Status:** Production-ready. The error handling is mature, defensive, and handles failure gracefully.

---

## Patterns Found

### Consistent Try-Catch Structure

All scripts follow a consistent main() pattern with specific exception handlers:

```python
try:
    # Main logic
except urllib.error.HTTPError as e:
    print(f"\nFailed with HTTP error {e.code}")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n\nInterrupted by user")
    sys.exit(1)
except Exception as e:
    print(f"\nUnexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
```

**Assessment:** Good. Handles network failures, user interrupts, and unexpected errors separately. Exit codes are meaningful.

### HTTP Error Handling

Network requests (REST/GraphQL) include error context:

```python
except urllib.error.HTTPError as e:
    error_body = e.read().decode()
    print(f"Error: HTTP {e.code} - {error_body}")
    raise
```

**Assessment:** Excellent. Errors include both status code and server response body. Helps debug API issues.

### GraphQL Error Detection

`make_graphql_request()` checks for errors in the response body:

```python
if "errors" in result:
    error_messages = [e.get("message", str(e)) for e in result["errors"]]
    raise Exception(f"GraphQL errors: {', '.join(error_messages)}")
```

**Assessment:** Correct. GraphQL returns 200 OK even with errors. This catches them.

### Missing Dependency Handling

YAML dependency is checked at import and validated before use:

```python
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Later:
if not HAS_YAML:
    print(f"Error: PyYAML not installed. Install with: pip install pyyaml")
    sys.exit(1)
```

**Assessment:** Good. Users get clear instructions instead of cryptic ImportErrors.

### Subprocess Error Handling

Git operations include stderr capture:

```python
def run_git(args: list, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Git error: {result.stderr}")
        raise subprocess.CalledProcessError(...)
    return result
```

**Assessment:** Excellent. Errors show stderr, and `check` parameter allows ignoring failures when intentional.

### Silent File Not Found Handling

In `pull_github.py`, exceptions when scanning for existing files are silently caught:

```python
for yaml_file in yaml_files:
    try:
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)
            # ...
    except:
        continue  # <-- Silent
```

**Assessment:** Acceptable. This is during discovery, not critical path. Bad YAML files don't halt the entire process.

### Warnings vs Errors

Local changes trigger warnings but don't fail:

```python
if title_changed_locally:
    print(f"    Warning: Local title changes exist, skipping title update")
else:
    metadata["title"] = title
```

**Assessment:** Good. Preserves local work while informing the user.

---

## Failure Modes

### 1. Network Failure

**What happens:**
- `urllib.error.HTTPError` caught at top level
- Error code and body printed
- Script exits with code 1

**Recovery:** None. User must retry manually.

**State:** No partial writes. No GitHub objects created because failures happen before API calls complete.

### 2. Invalid Input (Missing Config)

**sync_labels.py (line 35-37):**
```python
if not claude_config.exists():
    print(f"Error: {claude_config} not found")
    sys.exit(1)
```

**What happens:** Fails fast with clear error message before making network calls.

**Recovery:** None needed. User must create config.

### 3. Permission Denied (Git Clone)

**sync_wiki.py (line 82-90):**
```python
if result.returncode != 0:
    if "not found" in result.stderr.lower() or "does not exist" in result.stderr.lower():
        print("Error: Wiki repository not found.")
        print("Make sure:")
        print("  1. Wiki is enabled in repo settings")
        print("  2. At least one wiki page exists (create via GitHub UI)")
        return False
```

**Assessment:** Excellent. Gives actionable steps to fix the problem.

### 4. Bad YAML File

**pull_github.py (line 251):**
```python
except:
    continue  # Skip malformed files
```

**Assessment:** Acceptable during discovery. In conversion scripts, errors are caught per-file and reported in summary.

### 5. Repository Name Format Error

All scripts validate early:

```python
if "/" not in repo_arg:
    print("Error: Repository must be in format 'owner/repo'")
    sys.exit(1)
```

**Assessment:** Good. Validates input before expensive operations.

### 6. Missing Discussion Category

**sync_github.py (line 234-243):**
```python
if not categories:
    raise Exception("No discussion categories found in repository. Enable Discussions first.")

for category in categories:
    if category["name"] == category_name:
        return category["id"], category["name"]

first_category = categories[0]
print(f"  Warning: '{category_name}' category not found, using '{first_category['name']}'")
return first_category["id"], first_category["name"]
```

**Assessment:** Excellent. Degrades gracefully by using the first available category instead of failing.

### 7. Discussions Not Enabled

**sync_github.py (line 702-710):**
```python
except Exception as e:
    print(f"Warning: Could not fetch discussions: {e}")
    print("Discussions will be skipped. Enable Discussions on the repo first.")
    # Move idea files to errors
    for yaml_file, yaml_data in idea_files:
        metadata = yaml_data.get("metadata", {})
        title = metadata.get("title", "Untitled")
        stats["errors"].append((yaml_file.name, f"Discussions not available: {title}"))
    idea_files = []
```

**Assessment:** Excellent. Partial operation. Issues sync even if discussions fail.

---

## Recovery Assessment

### Can you resume after failure?

**Mostly yes, with caveats:**

1. **Network failures during sync:** Scripts are idempotent. Re-running syncs the remaining items. Already-synced items are skipped or updated.

2. **Partial syncs:** Each file/item is processed independently. One failure doesn't corrupt the entire batch. Stats track what succeeded.

3. **Git operations in sync_wiki.py:** Uses temporary directory. If push fails, local repo is not affected. Safe to retry.

4. **No transaction support:** If you create an issue but fail to update the YAML file, the next run will detect the issue exists (by title match) and update it. Self-healing.

### Is state left consistent?

**Yes, with safeguards:**

- **sync_github.py** uses three-way merge. Local changes are never overwritten blindly.
- **pull_github.py** uses `last_synced` snapshot to detect local modifications. Remote changes don't stomp local edits.
- **sync_wiki.py** uses temp directory. Either the entire wiki sync succeeds or nothing changes.

### Are partial updates handled?

**Yes:**

- **Per-file processing:** Each YAML file is independent. One bad file doesn't halt the batch.
- **Summary stats:** Users see what succeeded, what failed, and why.

**Example from export_markdown.py:**

```python
try:
    convert_yaml_to_markdown(yaml_file, output_path)
    print(f"  {yaml_file.name} → {md_filename}")
    exported_count += 1
except Exception as e:
    print(f"  ❌ {yaml_file.name}: {e}")
```

---

## User Feedback Quality

### Clear error messages?

**Yes.** Examples:

- `"Error: Repository must be in format 'owner/repo'"` — Tells you what's wrong and what format is expected.
- `"Error: Wiki repository not found. Make sure: 1. Wiki is enabled..."` — Actionable steps.
- `"Error: HTTP 401 - {"message": "Bad credentials"}"` — Shows API response.

### Exit codes meaningful?

**Yes:**

- `0` = success
- `1` = failure (all error paths use `sys.exit(1)`)

Scripts can be used in automation pipelines. Exit codes are reliable.

### Enough context to debug?

**Yes:**

- HTTP errors include status code AND response body.
- GraphQL errors extract message strings from error arrays.
- Git errors include stderr output.
- Traceback printed for unexpected exceptions.

**Example from sync_github.py (line 111-114):**

```python
except urllib.error.HTTPError as e:
    error_body = e.read().decode()
    print(f"Error: HTTP {e.code} - {error_body}")
    raise
```

You get the status code (e.g., 403 Forbidden) and the GitHub API error message (e.g., "Resource not accessible by integration").

### Progress Indicators?

**Yes:**

- `"Fetching issues..."` → `"Found 42 open issues"` → `"Processing: file.yaml"` → `"Created issue #123"`
- Summary at the end with counts: Created, Updated, Unchanged, Errors.

---

## Recommendations

### 1. **Add retry logic for transient network failures**

**Current:** Network failures immediately exit.

**Improvement:** Retry 429 (rate limit) and 5xx (server error) responses with exponential backoff.

**Why:** GitHub API can be flaky. Retries make scripts more robust in CI/CD pipelines.

### 2. **Replace bare `except:` with specific exceptions**

**Location:** `pull_github.py` line 251

**Current:**
```python
except:
    continue
```

**Better:**
```python
except (yaml.YAMLError, IOError, KeyError):
    continue
```

**Why:** Bare `except:` catches KeyboardInterrupt, SystemExit, and other things you don't want to ignore.

### 3. **Log errors to a file in addition to stderr**

**Current:** Errors only printed to console.

**Improvement:** Add `--log-file` option to write errors to a file.

**Why:** When running in CI or cron, you want persistent error logs.

### 4. **Add `--dry-run` mode**

**Current:** No way to preview changes without making them.

**Improvement:** `--dry-run` flag shows what WOULD be created/updated without actually doing it.

**Why:** Safer for testing. Users can verify before pushing to GitHub.

### 5. **Validate GitHub token before processing**

**Current:** Token validity is only checked when the first API call fails.

**Improvement:** Add a quick validation request (e.g., `GET /user`) before processing files.

**Why:** Fail fast if token is invalid. Don't waste time parsing YAML files only to fail at the end.

### 6. **Handle rate limiting explicitly**

**Current:** 429 responses treated like any other HTTP error.

**Improvement:** Check for `X-RateLimit-Remaining: 0` and show "Rate limit exceeded, retry after X seconds."

**Why:** GitHub API has rate limits. Users should know when they've hit them and when they can retry.

---

## Summary

These scripts are **production-ready**. Error handling is thoughtful, defensive, and user-friendly. The main gaps are:

- No retry logic for transient failures
- Bare `except:` blocks should be specific
- Rate limiting not explicitly handled

But for local/interactive use, the current error handling is excellent. Users get clear messages, state remains consistent, and failures are isolated to individual files.

**Grade: A-**

---

Wake up, Neo.
