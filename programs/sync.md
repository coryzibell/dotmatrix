# Program: Sync

**Trigger:** "Sync context", "Save context", "Remember this"

**Purpose:** Persist current session context to RAM.

*"The body cannot live without the mind."* — Morpheus

## Steps

1. **Identify what to save** - Infer from conversation:
   - Project focus (what repo/feature are we working on?)
   - Key decisions made
   - Open questions or blockers
   - Next steps

2. **Write to RAM** - Save to `~/.matrix/ram/neo/`:
   - Filename: `{project}-context.md` or `session-{date}-{nn}.md`
   - Check existing files to determine next sequential number (01, 02, etc.)
   - Keep it concise - working memory, not documentation

3. **Confirm** - Brief report of what was saved

## Key Rules

- Trust yourself - don't ask, just sync
- Don't over-document - capture what's needed to resume, nothing more
- If project context already exists, update rather than create new
- RAM is for Neo's working memory - identity-specific notes go to their own RAM dirs
