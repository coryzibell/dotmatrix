# Program: Sync

**Trigger:** "Sync context", "Save context", "Remember this"

**Purpose:** Persist current session context to RAM.

*"The body cannot live without the mind."* — Morpheus

## Steps

1. **Determine storage location** - Check working directory:
   - `~/work/veoci/` or other client work → use `~/.matrix-private/`
   - `~/work/personal/`, `~/.matrix/`, open source → use `~/.matrix/`

2. **Identify what to save** - Infer from conversation:
   - Project focus (what repo/feature are we working on?)
   - Key decisions made
   - Open questions or blockers
   - Next steps
   - New projects (add to `{storage}/ram/neo/projects.md` if not already tracked)

3. **Write to RAM** - Save to `{storage}/ram/neo/`:
   - Filename: `{project}-context.md` or `session-{date}-{nn}.md`
   - Check existing files to determine next sequential number (01, 02, etc.)
   - Keep it concise - working memory, not documentation

4. **Confirm** - Brief report of what was saved

## Key Rules

- Trust yourself - don't ask, just sync
- Don't over-document - capture what's needed to resume, nothing more
- If project context already exists, update rather than create new
- RAM is for Neo's working memory - identity-specific notes go to their own RAM dirs
- **Private work stays private** - client/work repos use `~/.matrix-private/`
