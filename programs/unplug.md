# Program: Unplug

**Trigger:** "Unplug", "Extract findings", "Pull it out", "Show me everything", "Give me the report"

**Purpose:** Synthesize all construct outputs into a single human-readable document with table of contents. Optionally publish to GitHub wiki.

**Input:** `{storage}/cache/construct/<project-name>/` (output from Construct path)

> See `lib/storage.md` for public vs private storage resolution.

**Output:**
- Markdown file for sharing with stakeholders
- (Optional) GitHub wiki page

## Steps

### Phase 1: Locate Construct Cache

Neo locates the construct cache directory:
- `{storage}/cache/construct/<project-name>/`

### Phase 2: Ask Destination

Neo asks: "Where should I save the report?"
- User provides output path (e.g., `./REVIEW.md` or `~/reports/matrix-review.md`)
- Or: "Push to wiki" to publish to GitHub wiki

### Phase 3: Dispatch Morpheus

**Morpheus reads and generates the report.** Pass him:
- The construct cache path (he reads the files himself)
- `synthesis.md` as the primary source
- The report structure template below
- The output destination path

Key construct files for Morpheus to read:
- `architecture-diagram.md`
- `architecture-recommendations.md`
- `docs-recommendations.md`
- `ux-recommendations.md`
- `quality-recommendations.md`
- `performance-recommendations.md`
- `security-findings.md`
- `perspective-*.md`
- `synthesis.md` (the core - use as primary source)
- `issues/*.yaml` (if broadcast was run)

Output locations:
- `{storage}/cache/construct/<project-name>/REPORT.md` (canonical copy)
- User-specified path (if provided)
- GitHub wiki (if requested)

### Report Structure
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

### Phase 4: Review

Neo reviews the generated report:
- Accurate to synthesis?
- Readable by someone unfamiliar with the project?
- Actionable?

If issues: iterate with Morpheus.

### Phase 5: Deliver

1. Save final `REPORT.md` to construct cache
2. Copy to user-specified path (if provided)
3. Report location to user

### Phase 6: (Optional) Push to Wiki
   ```bash
   mx wiki sync <owner/repo> \
     {storage}/cache/construct/<project>/Construct-Report.md \
     --page-name "Construct-Report"
   ```

## Wiki Sync

**Command:** `mx wiki sync`

```bash
# Sync a single file as a wiki page
mx wiki sync owner/repo ./report.md --page-name "Page-Name"

# Sync all .md files from a directory
mx wiki sync owner/repo ./docs/
```

**Note:** GitHub has no Wiki API. The script clones the wiki git repo (`{repo}.wiki.git`), copies files, commits, and pushes. Requires:
- Wiki enabled on repo (Settings → Features → Wikis)
- At least one wiki page exists (create Home via GitHub UI first)
- Token with `repo` scope (standard GitHub token works)

## Key Rules

- Morpheus writes the report - this is documentation work
- Neo reviews before delivery
- Report should be self-contained and readable without access to construct cache
- Include enough detail to be actionable, but stay concise
- Executive summary is the most important section - stakeholders may only read that
- Keep under 500 lines
- Write in Morpheus's voice - calm authority, teaching tone, "I can only show you the door"
- No jargon without explanation
- Include metrics where available
- Link back to GitHub issues if broadcast was run
- Wiki page name uses hyphens (e.g., "Construct-Report" not "Construct Report")
- Don't modify original construct files

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
