# Program: Transcript

**Trigger:** "transcript", "generate report", "produce report from construct"

*"The Matrix is a system, Neo. That system is our enemy."*

The official record. Takes raw construct outputs and produces a polished, production-ready report suitable for sharing, archiving, or including in project documentation.

**Input:** `~/.matrix/cache/construct/<project-name>/` (output from Construct program)

**Output:** `~/.matrix/cache/construct/<project-name>/REPORT.md`

## Steps

### Phase 0: Locate

> See `lib/locate.md` for project detection logic.

Output: Absolute path to repo, project name (used to find construct cache)

### Phase 1: Verify Construct Exists

1. Check `~/.matrix/cache/construct/<project-name>/` exists
2. Check `synthesis.md` exists (construct must be complete)
3. If missing: "Run construct first: `/load construct <project>`"

### Phase 2: Gather Sources

Read all construct outputs:
- `architecture-diagram.md`
- `architecture-recommendations.md`
- `synthesis.md` (the core)
- All perspective files (`perspective-*.md`)
- Key findings from health checks

### Phase 3: Generate Report

**Dispatch Morpheus** - Produce the official transcript:

Input: All construct files, synthesis.md as primary source

Output: `REPORT.md` with structure:
```
# <Project Name> - Construct Report

## Executive Summary
One paragraph: what is this, what's the verdict, key numbers

## Architecture Overview
Mermaid or ASCII diagram from architect
Brief description of structure

## Findings

### Blockers
From synthesis - must fix items with brief context

### Improvements
From synthesis - should fix items, grouped by priority

### Strengths
What's working well

## Perspectives
Key insights from Sati, Spoon, Oracle (condensed)

## Recommendations
Ordered action list

## Appendix: Full Reports
Links/references to individual agent reports
```

Guidelines:
- Professional tone, suitable for stakeholders
- Concrete, actionable
- No jargon without explanation
- Include metrics where available
- Keep under 500 lines

### Phase 4: Review

**Neo reviews** the generated report:
- Accurate to synthesis?
- Readable by someone unfamiliar with the project?
- Actionable?

If issues: iterate with Morpheus

### Phase 5: Deliver

1. Save final `REPORT.md` to construct cache
2. Optionally copy to project repo (ask user)
3. Report location to user

## Key Rules

- Construct must be complete before transcript
- Morpheus writes - this is documentation work
- Report should stand alone - readable without other files
- Neo approves before delivery
- Don't modify original construct files
