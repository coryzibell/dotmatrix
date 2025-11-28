# Program: Sync

**Trigger:** "Sync context", "Save context", "Remember this"

**Purpose:** Persist current session context - working memory to RAM, learnings to Zion.

*"The body cannot live without the mind."* — Morpheus

## Steps

### Phase 1: RAM - Working Memory

1. **Identify what to save** - Infer from conversation:
   - Project focus (what repo/feature are we working on?)
   - Key decisions made
   - Open questions or blockers
   - Next steps

2. **Write to RAM** - Save to `~/.matrix/ram/neo/`:
   - Filename: `{project}-context.md` or `session-{date}.md`
   - Include timestamp
   - Keep it concise - this is working memory, not documentation

### Phase 2: Zion - Permanent Knowledge

3. **Dispatch Zion Control** - Process session for permanent storage
   - "Zion Control, this is the Nebuchadnezzar. Requesting clearance."
   - Zion reviews session for:
     - **Patterns** - Reusable approaches that worked
     - **Techniques** - How-to knowledge worth preserving
     - **Insights** - Realizations, connections discovered
     - **Rituals** - New workflows or ceremonies established
   - Zion writes to appropriate `~/.matrix/zion/` directories
   - RAM stays ephemeral, Zion is permanent

### Phase 3: Confirm

4. **Summary** - Brief report of what was saved:
   - RAM: what context was persisted
   - Zion: what learnings were archived (if any)

## Key Rules

- Trust yourself - don't ask, just sync. The data can be moved or cleaned later.
- Only ask kautau if there's a significant conflict (e.g., overwriting substantial context)
- Don't over-document - capture what's needed to resume, nothing more
- If project context already exists, update rather than create new
- RAM is for Neo's working memory - identity-specific notes go to their own RAM dirs
- Zion is for permanent knowledge - patterns, techniques, insights that transcend sessions
