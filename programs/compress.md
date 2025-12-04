# Program: Compress

**Owner:** Zion Control
**Purpose:** Compress RAM, archive knowledge to Zion, discard noise.

*"Free your mind."* — Morpheus

---

## Storage Note

This program operates on BOTH storage locations:
- `~/.matrix/` - Public dotfiles (personal projects, open source)
- `~/.matrix-private/` - Private work (client projects)

Run on each as needed. See `lib/storage.md`.

---

## Phase 0: Pre-flight (Neo)

Before dispatching Zion Control:
1. Check `git status` in `~/.matrix/`
2. If dirty, commit first (rollback safety)

---

## Phase 1: Dispatch Zion Control

**Neo passes these paths to Zion Control:**

1. `{storage}/ram/*/` - Agent working memory
2. `{storage}/cache/` - Workflow artifacts, construct outputs, session exports
3. `~/.matrix/future/` - Shelved ideas (should migrate to Zion db) (public only)
4. `{storage}/zion/**/*.md` - All markdown in Zion (should be in db, not files)

**Zion Control scans, reads, and contextualizes.** Neo doesn't pre-read.

**Rule:** RAM and Cache hold working files (any type). Zion is database-only - no files, just structured entries.

---

## Phase 2: Triage

**Zion Control reads** each file and decides:

| Action | Destination |
|--------|-------------|
| **Keep** | Leave in place |
| **Archive** | Extract knowledge → Zion database |
| **Migrate** | Move from future/ or zion/*.md → Zion database |
| **Delete** | Remove (stale files of any type - scripts, binaries, session exports, old construct outputs) |

Special handling:
- **Cache/construct/**: Keep recent, delete stale (regenerable via `/load construct`)
- **Cache/session-export-***: Usually deletable after review
- **Future/**: Migrate ideas to Zion db with category `future`
- **Zion/**/*.md**: Absorb into db (use appropriate category), then delete the file

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

Zion is a database, not a folder. Never write markdown files to `{storage}/zion/`.

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
