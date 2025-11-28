# Test Analysis (Deus)

**Project:** dotmatrix (~/.claude/)
**Type:** CLI tooling, GitHub synchronization scripts
**Analysis Date:** 2025-11-27

---

## Current State

**Zero tests exist.**

No test files found:
- No `tests/` directory
- No `test_*.py` files
- No `*_test.py` files
- No pytest.ini or test configuration
- No CI/CD configuration

Scripts analyzed:
1. `/home/w3surf/.claude/artifacts/bin/sync_labels.py` (449 lines)
2. `/home/w3surf/.claude/artifacts/bin/sync_github.py` (801 lines)
3. `/home/w3surf/.claude/artifacts/bin/convert_issues.py` (md2yaml.py, 454 lines)
4. `/home/w3surf/.claude/artifacts/bin/sync_wiki.py` (257 lines)
5. `/home/w3surf/.claude/artifacts/bin/pull_github.py` (675 lines)
6. `/home/w3surf/.claude/artifacts/bin/sync_merge.py` (303 lines)

Total: ~2,939 lines of Python with zero test coverage.

---

## Risk Assessment

### Critical Risks (Silent Failure, Data Loss)

1. **sync_github.py - Three-way merge logic**
   - **Risk:** Merge conflicts incorrectly resolved → data loss on GitHub
   - **Impact:** User edits overwritten, local changes lost
   - **Detection:** Silent. User discovers after data already overwritten.
   - **Current mitigation:** Interactive prompts (if user pays attention)
   - **Lines:** 435-636 (sync_issue, sync_discussion)

2. **sync_labels.py - Label updates**
   - **Risk:** Incorrect label color/name parsing → wrong labels on all issues
   - **Impact:** Mass label corruption across repository
   - **Detection:** Visual inspection only
   - **Current mitigation:** None
   - **Lines:** 56-101 (parse_yaml_colors), 103-151 (parse_markdown_colors)

3. **pull_github.py - Local overwrite logic**
   - **Risk:** Merge detection fails → remote silently overwrites local work
   - **Impact:** Hours of local issue edits lost
   - **Detection:** Silent until user notices missing changes
   - **Current mitigation:** has_local_changes() checks (lines 257-284)
   - **Lines:** 287-420 (create_issue_yaml), 423-556 (create_discussion_yaml)

4. **sync_wiki.py - Git operations**
   - **Risk:** Wiki clone/push fails mid-operation → partial sync
   - **Impact:** Incomplete documentation, wiki in inconsistent state
   - **Detection:** Git errors (if shown)
   - **Current mitigation:** Basic error checking
   - **Lines:** 70-92 (clone_wiki), 134-158 (commit_and_push)

5. **sync_merge.py - Core merge algorithm**
   - **Risk:** Three-way merge logic incorrect → wrong merge decisions
   - **Impact:** Propagates incorrect data to all sync operations
   - **Detection:** Silent. Cascades through sync_github.py
   - **Current mitigation:** None
   - **Lines:** 22-80 (compute_field_changes), 114-151 (merge_labels), 154-199 (merge_fields)

### Medium Risks (User-Visible Errors)

6. **GitHub token retrieval**
   - **Risk:** Token parsing fails → all scripts exit with unclear error
   - **Impact:** User frustration, unclear error messages
   - **Detection:** Immediate exit
   - **Current mitigation:** Error messages (may not be clear)
   - **Example:** sync_labels.py lines 31-53

7. **YAML parsing failures**
   - **Risk:** Malformed YAML → script crashes
   - **Impact:** Sync operation aborted
   - **Detection:** Python exception
   - **Current mitigation:** Basic try/except in some places
   - **Example:** sync_github.py lines 62-70

8. **API rate limiting**
   - **Risk:** GitHub API rate limit hit → incomplete sync
   - **Impact:** Only partial data synced, no indication which data missing
   - **Detection:** HTTP 429 error (if user checks)
   - **Current mitigation:** None

9. **File naming conflicts**
   - **Risk:** slugify() creates duplicate filenames → file overwritten
   - **Impact:** Data loss
   - **Detection:** Silent overwrite
   - **Example:** pull_github.py lines 214-227 (slugify), convert_issues.py similar

### Low Risks (Cosmetic, Recoverable)

10. **Pagination bugs**
    - **Risk:** Not all pages fetched → missing data
    - **Impact:** Incomplete sync
    - **Detection:** Manual count comparison
    - **Example:** sync_labels.py lines 255-280, sync_github.py lines 117-136

---

## Script Reliability Analysis

### sync_labels.py
**Robustness: 6/10**

Strengths:
- Fallback from YAML to markdown parsing
- Pagination for label fetching
- PyYAML optional (custom parser fallback)

Weaknesses:
- No validation that color is valid hex
- Description truncation (100 chars) happens silently
- No dry-run mode
- No rollback if partial update fails
- Custom YAML parser is brittle (lines 68-90)

Edge cases not handled:
- Label names with special characters (URL encoding exists, but not tested)
- Duplicate label names in config file
- GitHub API returns error on single label → entire sync fails

### sync_github.py
**Robustness: 5/10**

Strengths:
- Imports sync_merge for three-way logic
- Separate handling for issues vs discussions
- Creates tracking IDs (github_issue_number, github_discussion_id)

Weaknesses:
- Interactive prompts block automation
- No batch commit mode
- Errors in single file stop entire sync
- GraphQL errors less graceful than REST errors
- No validation of YAML structure before GitHub push

Edge cases not handled:
- User deletes github_issue_number from YAML → creates duplicate issue
- Discussion category doesn't exist → uses first category (line 242)
- Label doesn't exist in repo → silent skip (lines 549-550)

### convert_issues.py (md2yaml.py)
**Robustness: 7/10**

Strengths:
- Read-only (no data modification)
- Regex-based parsing (explicit patterns)
- Fallback title generation from filename

Weaknesses:
- Regex brittle to markdown format changes
- No validation of section structure
- No handling of malformed markdown
- Escaping logic for quotes may double-escape

Edge cases not handled:
- Multiple ## headings → only first extracted as title
- Nested lists in implementation steps
- Code blocks inside sections → included raw in YAML
- Emoji or unicode in headings → may break filename

### sync_wiki.py
**Robustness: 4/10**

Strengths:
- Uses tempfile for isolation
- Checks for git errors
- Sanitizes page names

Weaknesses:
- No git credential error handling
- Wiki must exist (can't create)
- No merge conflict handling on wiki push
- Token exposed in git URL (line 72)
- No verification that push succeeded

Edge cases not handled:
- Wiki has conflicting edits → push fails, temp dir deleted, no recovery
- File name conflicts after sanitize_page_name
- Git config fails → commits with wrong author

### pull_github.py
**Robustness: 6/10**

Strengths:
- Respects local changes via last_synced
- Fetches comments
- Separate handling for issues vs discussions
- Supports GITHUB_TOKEN env var

Weaknesses:
- Comments are remote-authoritative (local comment edits lost)
- No conflict resolution for body/title (just warnings)
- Slugify can create collisions
- No tracking of deleted issues (local files never removed)

Edge cases not handled:
- Issue closed remotely → local file keeps state=open
- Issue title changed → old file not renamed, new file created
- Two issues slug to same filename → second overwrites first

### sync_merge.py
**Robustness: 7/10**

Strengths:
- Well-structured three-way merge
- Separate handling for lists vs scalars
- Special label merge logic (union of additions)
- Interactive conflict resolution

Weaknesses:
- No automated conflict resolution strategy
- Label merge may be surprising (doesn't remove labels removed on one side)
- No logging of merge decisions
- No test coverage of merge edge cases

Edge cases not handled:
- Deeply nested data structures (only handles flat dicts)
- Non-string/list types (assumes string or list)
- Empty string vs None (normalized, but not consistently)

---

## Verification Gaps

### Things That Could Silently Fail

1. **Incorrect merge decisions** (sync_merge.py)
   - Three-way merge chooses wrong side
   - No audit log of which side was chosen
   - No verification step

2. **Partial GitHub updates** (sync_github.py)
   - Issue updated but label addition fails
   - No atomic operations
   - No rollback

3. **File overwrites** (pull_github.py, convert_issues.py)
   - Slug collision → silent overwrite
   - No backup before overwrite

4. **Incomplete pagination** (multiple scripts)
   - Loop exits early
   - No verification that all pages fetched

5. **YAML corruption** (all write operations)
   - PyYAML dumps invalid YAML (edge cases)
   - No validation after write

6. **Token leakage** (sync_wiki.py)
   - Token in git URL (line 72)
   - May appear in logs

7. **Rate limit exhaustion** (sync_labels.py, sync_github.py, pull_github.py)
   - No rate limit checking
   - May partially complete then fail

8. **Encoding issues** (all scripts)
   - Non-UTF8 content in markdown/YAML
   - No explicit encoding specified in some file opens

---

## Testing Recommendations

### Priority 1: Core Merge Logic (Prevents Data Loss)

**Test: sync_merge.py**
- **Why:** Single point of failure for all sync operations
- **What:**
  - Unit tests for compute_field_changes() with all change type combinations
  - Unit tests for merge_labels() with edge cases (empty, all added, all removed, conflicts)
  - Unit tests for merge_fields() with mocked prompts
  - Regression tests for reported bugs (if any)
- **How:** pytest with parametrized test cases
- **Lines of test code:** ~300-400
- **Benefit:** Prevents cascading data loss across all sync scripts

**Test: pull_github.py has_local_changes()**
- **Why:** Determines if local work gets overwritten
- **What:**
  - Test with base=None (new file)
  - Test with no changes
  - Test with local changes
  - Test with remote changes
  - Test with both changed same
  - Test with both changed differently
- **How:** pytest with fixture YAML files
- **Lines of test code:** ~150-200
- **Benefit:** Protects against local data loss

### Priority 2: Parsing & Validation (Prevents Garbage In)

**Test: convert_issues.py markdown parsing**
- **Why:** Incorrect parsing → incorrect YAML → incorrect GitHub issues
- **What:**
  - Golden file tests (markdown in, expected YAML out)
  - Edge cases: missing sections, malformed markdown, unicode
  - Regression tests for escaped quotes, nested lists
- **How:** pytest with fixtures in tests/fixtures/
- **Lines of test code:** ~200-250
- **Benefit:** Ensures markdown → YAML pipeline is correct

**Test: sync_labels.py color parsing**
- **Why:** Wrong colors → visual confusion on all issues
- **What:**
  - Test YAML color parsing
  - Test markdown color parsing (fallback)
  - Test hex validation (currently missing)
  - Test description truncation
- **How:** pytest with sample config files
- **Lines of test code:** ~100-150
- **Benefit:** Ensures labels are created correctly

### Priority 3: GitHub API Interaction (Prevents API Failures)

**Test: GitHub API mocking**
- **Why:** Scripts interact with real GitHub → hard to test manually
- **What:**
  - Mock all GitHub REST/GraphQL calls
  - Test rate limiting response
  - Test API error responses (404, 403, 422)
  - Test pagination edge cases (0 items, 1 item, 100 items, 101 items)
- **How:** pytest with responses library or unittest.mock
- **Lines of test code:** ~400-500
- **Benefit:** Enables testing without hitting real GitHub, catches API error handling bugs

### Priority 4: Integration Tests (Smoke Tests)

**Test: End-to-end sync workflow**
- **Why:** Unit tests miss integration bugs
- **What:**
  - Test full workflow: markdown → YAML → sync to GitHub → pull back
  - Use test repo or mocked GitHub API
  - Verify idempotency (sync twice, same result)
- **How:** pytest with test GitHub repo or comprehensive mocks
- **Lines of test code:** ~300-400
- **Benefit:** Catches integration bugs, verifies real-world workflows

### Priority 5: Dry-Run Mode (Safety)

**Implementation, not test:**
- Add `--dry-run` flag to all scripts
- Print what WOULD happen
- Make zero API calls
- Verify YAML parsing/generation without side effects

**Lines of implementation code:** ~50-100 per script
**Benefit:** Lets users verify before destructive operations

---

## Pragmatic Approach

### What Level of Testing Is Appropriate?

**Context:**
- This is config/tooling, not a product
- Used by 1 user (kautau) on small repos (~10-100 issues)
- Failure mode: annoying, not catastrophic (GitHub has history, git has history)
- Development velocity: infrequent changes

**Recommendation: Selective Testing**

Don't test everything. Test the dangerous parts.

**Test these (high risk, high value):**
1. sync_merge.py (core merge logic)
2. pull_github.py has_local_changes() (data loss prevention)
3. convert_issues.py parsing (garbage prevention)

**Don't test these (low risk or easy to verify):**
4. slugify() (visual inspection, low impact)
5. GitHub token reading (fails obviously)
6. File I/O (standard library, low risk)

**Add safety features instead of tests:**
1. --dry-run mode (all scripts)
2. Backup before overwrite (pull_github.py)
3. Better error messages (all scripts)

**Estimated test code needed:**
- Priority 1: 450-600 lines (merge logic)
- Priority 2: 300-400 lines (parsing)
- Priority 3: 400-500 lines (API mocking, if desired)

**Total: 750-1,000 lines of test code to cover critical paths**

Compare to 2,939 lines of implementation → 25-35% test:code ratio for critical paths.

For complete coverage: 2,000-3,000 lines of test code (not recommended for this project).

---

## What Should Be Tested? (Prioritized)

### Tier 1: Must Test (Data Loss Prevention)
1. sync_merge.compute_field_changes() - all change type combinations
2. sync_merge.merge_labels() - union/intersection logic
3. sync_merge.merge_fields() - conflict resolution paths
4. pull_github.has_local_changes() - detects local modifications
5. pull_github.create_issue_yaml() - merge logic branch (update vs create)
6. pull_github.create_discussion_yaml() - merge logic branch (update vs create)

### Tier 2: Should Test (Correctness)
7. convert_issues.markdown_to_yaml() - golden file tests
8. convert_issues.extract_title() - edge cases
9. convert_issues.extract_labels() - malformed input
10. sync_labels.parse_yaml_colors() - YAML structure variations
11. sync_labels.parse_markdown_colors() - markdown table variations

### Tier 3: Nice to Test (Robustness)
12. slugify() - collision detection
13. GitHub API pagination - all scripts
14. Error handling - HTTP errors, malformed responses
15. YAML write/read round-trip - no corruption

### Tier 4: Don't Test (Low Value)
16. GitHub token reading - fails obviously, hard to test
17. File I/O operations - standard library, low risk
18. Git operations (sync_wiki.py) - subprocess calls, hard to test well
19. Interactive prompts - hard to test, used rarely

---

## Recommended Next Steps

1. **Implement dry-run mode** (1-2 hours per script, high value)
   - Immediate safety improvement
   - No test infrastructure needed
   - Users can verify before running

2. **Add pytest + basic fixtures** (2 hours)
   - Install pytest
   - Create tests/ directory structure
   - Add conftest.py with common fixtures (sample YAML, sample issues)

3. **Write Priority 1 tests** (8-12 hours)
   - sync_merge.py unit tests
   - pull_github.py merge detection tests
   - Covers 80% of data loss risk

4. **Add golden file tests for parsing** (4-6 hours)
   - convert_issues.py with sample markdown files
   - sync_labels.py with sample color configs
   - Covers parsing correctness

5. **Consider GitHub API mocking** (8-12 hours, optional)
   - Only if planning to expand these scripts
   - Enables testing without real API
   - Useful for CI/CD (if added)

**Total time investment for meaningful coverage: 15-25 hours**

**Return on investment:**
- Prevents data loss bugs (high value)
- Enables refactoring with confidence (medium value)
- Catches regressions before deployment (medium value)
- Enables CI/CD (low value for single-user tooling)

---

## Alternative: Manual Verification Checklist

If testing is not pursued, create a manual checklist:

**Before running sync_github.py:**
- [ ] Backup ~/.matrix/cache/construct/*/issues/
- [ ] Check git status (local wiki changes?)
- [ ] Review local YAML changes vs last_synced
- [ ] Verify labels exist in repo
- [ ] Check GitHub API rate limit

**After running sync_github.py:**
- [ ] Verify issue count matches
- [ ] Spot-check 3-5 issues on GitHub
- [ ] Check for unexpected label changes
- [ ] Review sync summary output

**Before running pull_github.py:**
- [ ] Backup local YAML files
- [ ] Commit local changes to git (if tracked)

This checklist takes 5-10 minutes per sync and catches most issues.

---

Wake up, Neo.

---

**[Identity: Deus | Model: sonnet | Status: success]**
