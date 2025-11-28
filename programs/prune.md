# Program: Prune

**Owner:** Zion Control
**Purpose:** Compress RAM, archive knowledge to Zion, discard noise.

---

## Phase 0: Pre-flight (Neo)

Before dispatching Zion Control:
1. Check `git status` in `~/.matrix/`
2. If dirty, commit first (rollback safety)

---

## Phase 1: Survey

Scan all `~/.matrix/ram/` subdirectories. List files with sizes and dates.

---

## Phase 2: Triage

For each file, decide:

| Action | Destination |
|--------|-------------|
| **Keep** | Leave in RAM |
| **Archive** | Extract knowledge → `mx zion add` |
| **Delete** | Remove |

---

## Phase 3: Review Gate

Zion proposes, Neo reviews.

Flag for kautau if:
- Archiving active project as "complete"
- Uncertain about content accuracy
- Significant learnings that need human validation

---

## Phase 4: Execute

- **Archive:** Use `mx zion add` - synthesize into proper categories (pattern/technique/insight), don't just dump files
- **Delete:** `rm` the file

See Zion Control's agent file for `mx zion` CLI details.

---

## Phase 5: Commit

1. Update `neo/projects.md` if projects completed
2. Commit changes to dotmatrix
3. Report back to Neo

---

## Key Rules

1. **Synthesize, don't consolidate** - Extract patterns, techniques, insights separately
2. **Never delete without review**
3. **Trust regeneration** - If easily recreated, delete it
4. **Timebox** - 10 min max per agent's RAM

---

**"Free your RAM, Neo."**
