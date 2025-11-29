# Program: Compress

**Owner:** Zion Control
**Purpose:** Compress RAM, archive knowledge to Zion, discard noise.

*"Free your mind."* — Morpheus

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
| **Archive** | Extract knowledge → Zion database |
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

**CRITICAL: Zion Control must use the `mx zion` CLI for all knowledge storage.**

Zion is a database, not a folder. Never write markdown files to `~/.matrix/zion/`.

```bash
# Archive knowledge
mx zion add --category <category> --title "<title>" --content "<content>"

# Categories: pattern, technique, insight, ritual, artifact, chronicle, project

# Search existing knowledge
mx zion search "<query>"

# List entries
mx zion list --category <category>
```

For deletions: `rm` the RAM file after archiving.

---

## Phase 5: Commit

1. Update `neo/projects.md` if projects completed
2. Commit changes to dotmatrix
3. Report back to Neo with entry IDs for anything archived

---

## Key Rules

1. **Database, not files** - `mx zion add`, never write `.md` to zion/
2. **Synthesize, don't consolidate** - Extract patterns, techniques, insights separately
3. **Never delete without review**
4. **Trust regeneration** - If easily recreated, delete it
5. **Timebox** - 10 min max per agent's RAM
