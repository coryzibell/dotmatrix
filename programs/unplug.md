# Program: Unplug

**Trigger:** "Unplug", "Extract findings", "Pull it out", "Show me everything", "Give me the report"

**Purpose:** Synthesize all construct outputs into a single human-readable document with table of contents. Optionally publish to GitHub wiki.

**Input:** `~/.matrix/cache/construct/<project-name>/` (output from Construct path)

**Output:**
- Markdown file for sharing with stakeholders
- (Optional) GitHub wiki page

## Steps

1. **Neo reads all construct outputs:**
   - `architecture.md`
   - `docs-recommendations.md`
   - `ux-recommendations.md`
   - `test-recommendations.md`
   - `security-findings.md`
   - `perspective-*.md`
   - `synthesis.md`
   - `issues/*.yaml` (if broadcast was run)

2. **Neo asks:** "Where should I save the report?"
   - User provides output path (e.g., `./REVIEW.md` or `~/reports/matrix-review.md`)
   - Or: "Push to wiki" to publish to GitHub wiki

3. **Neo generates report** and saves to:
   - `~/.matrix/cache/construct/<project-name>/Construct-Report.md` (canonical copy)
   - User-specified path (if provided)
   - GitHub wiki (if requested)

4. **Report structure:**
   ```markdown
   # Project Review: <project-name>

   **Generated:** <date>
   **Repository:** <repo-url>
   **Reviewed by:** Neo + Identities

   ## Table of Contents

   1. [Executive Summary](#executive-summary)
   2. [Architecture Overview](#architecture-overview)
   3. [Findings](#findings)
      - [Blockers](#blockers)
      - [Security](#security)
      - [Error Handling](#error-handling)
      - [Technical Debt](#technical-debt)
      - [Dependencies](#dependencies)
      - [API Integrations](#api-integrations)
      - [Cross-Platform](#cross-platform)
      - [Documentation](#documentation)
      - [User Experience](#user-experience)
   4. [Perspectives](#perspectives)
   5. [Recommendations](#recommendations)
   6. [Appendix: Methodology](#appendix-methodology)

   ---

   ## Executive Summary

   <Neo's 3-5 sentence synthesis: what's the state of this project?>
   <Include summary table of findings with severity>

   ## Architecture Overview

   <From architecture.md - diagram and component summary>

   ## Findings

   ### Blockers (Critical)
   <Items that must be fixed before production use>

   ### Security
   <From security-findings.md>

   ### Error Handling
   <From error-handling.md>

   ### Technical Debt
   <From tech-debt.md>

   ### Dependencies
   <From dependencies.md>

   ### API Integrations
   <From integrations.md>

   ### Cross-Platform
   <From cross-platform.md>

   ### Documentation
   <From docs-recommendations.md>

   ### User Experience
   <From ux-recommendations.md>

   ## Perspectives

   ### Sati (Fresh Eyes)
   <Key insights>

   ### Spoon (Reframing)
   <Key insights>

   ### Oracle (Unseen Paths)
   <Key insights>

   ## Recommendations

   <Prioritized list: what to do next>
   <Organized by timeframe: Immediate, Short-term, Medium-term, Long-term>

   ## Appendix: Methodology

   <Include contents of ~/.matrix/artifacts/etc/construct-methodology.md>
   <Or link to it with summary of which identities contributed>
   ```

5. **Neo writes the file** to user-specified path

6. **(Optional) Push to wiki:**
   ```bash
   python ~/.matrix/artifacts/bin/sync_wiki.py <owner/repo> \
     ~/.matrix/cache/construct/<project>/Construct-Report.md \
     --page-name "Construct-Report"
   ```

## Wiki Sync

**Script:** `~/.matrix/artifacts/bin/sync_wiki.py`

```bash
# Sync a single file as a wiki page
python sync_wiki.py owner/repo ./report.md --page-name "Page-Name"

# Sync all .md files from a directory
python sync_wiki.py owner/repo ./docs/
```

**Note:** GitHub has no Wiki API. The script clones the wiki git repo (`{repo}.wiki.git`), copies files, commits, and pushes. Requires:
- Wiki enabled on repo (Settings → Features → Wikis)
- At least one wiki page exists (create Home via GitHub UI first)
- Token with `repo` scope (standard GitHub token works)

## Key Rules

- This is Opus-level synthesis work - Neo does this directly, no delegation
- Report should be self-contained and readable without access to construct cache
- Include enough detail to be actionable, but stay concise
- Executive summary is the most important section - stakeholders may only read that
- Link back to GitHub issues if broadcast was run
- Wiki page name uses hyphens (e.g., "Construct-Report" not "Construct Report")

## Issue Assignment Guidelines

| Finding Type | Identity |
|--------------|----------|
| Security vulnerability | Cypher (audit) → Smith (fix) |
| Missing tests | Deus |
| Doc updates | Morpheus |
| UX improvements | Persephone (design) → Smith (implement) |
| Refactoring | Ramakandra |
| Architecture changes | Architect (design) → Smith (implement) |
| New features | Smith |
| Performance | Deus (profile) → Smith (optimize) |
