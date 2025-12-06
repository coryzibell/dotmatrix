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

**Neo passes to Zion Control:**

1. **Project registry** - Output of `mx zion projects list` (for project tagging)
2. **Paths to process:**
   - `{storage}/ram/*/` - Agent working memory
   - `{storage}/cache/` - Workflow artifacts, construct outputs, session exports
   - `~/.matrix/future/` - Shelved ideas (should migrate to Zion db) (public only)
   - `{storage}/zion/**/*.md` - All markdown in Zion (should be in db, not files)

**Zion Control scans, reads, and contextualizes.** Neo doesn't pre-read.

**Rule:** RAM and Cache hold working files (any type). Zion is database-only - no files, just structured entries.

---

## Phase 2: Triage

**Zion Control reads** each file and decides:

| Action | Destination |
|--------|-------------|
| **Keep** | Leave in place (active work) |
| **Archive** | Store verbatim → Zion database (archive category) |
| **Migrate** | Move from future/ or zion/*.md → Zion database |

**Nothing gets deleted.** Every document moves to Zion as an archive.

Special handling:
- **Cache/construct/**: Keep recent, archive when stale (regenerable via `/load construct`)
- **Cache/session-export-***: Archive with source context, then remove file
- **Future/**: Migrate ideas to Zion db with category `future`
- **Zion/**/*.md**: Absorb into db (use appropriate category), then delete the file

### What to Delete vs Archive

| Content Type | Action | Rationale |
|--------------|--------|-----------|
| **Session notes** | Archive | Worth looking back at the thinking |
| **Working rounds/feedback** | Archive | Preserves the evolution of ideas |
| **Issue/PR working files** | Archive | Shows improvement over time |
| **Cloned source code** | Delete | Duplicates actual repo, not worth storing |
| **Generated/build artifacts** | Delete | Regenerable |

**General rule:** Archive all notes and thinking. Delete copies of source code unless it's an active working directory.

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

### Archive-First Flow

For each document leaving RAM/Cache:

**Step 1: Archive the original**
```bash
mx zion add \
  --category archive \
  --title "RAM: smith/issue-128-schema-ir-export.md" \
  --content "<full verbatim content>" \
  --source-agent smith \
  --source-type ram \
  --entry-type primary \
  --project mx \
  --tags "archive,source:ram/smith"
```
Note: Include `--project` when content is project-specific. Omit for general knowledge.

**Step 2: Synthesize knowledge** (if patterns/insights exist)
```bash
# Extract patterns, techniques, insights as separate entries
mx zion add \
  --category pattern \
  --title "Schema IR export pattern" \
  --content "<distilled pattern>" \
  --source-agent zion-control \
  --source-type ram \
  --entry-type synthesis \
  --tags "archive-ref:<archive-id>"
```

### Categories

| Category | Use |
|----------|-----|
| **archive** | Verbatim source (never summarize) |
| **pattern** | Reusable code structures |
| **technique** | Methods and approaches |
| **insight** | Understanding of why things work |
| **ritual** | Human ceremonies |
| **artifact** | Reference implementations |
| **chronicle** | Historical records |
| **project** | Project-specific knowledge |

### Search & List

```bash
mx zion search "<query>"
mx zion list --category archive        # See all archived sources
mx zion list --category pattern        # See synthesized patterns
```

After archiving: `rm` the RAM file (source preserved in Zion).

---

## Phase 5: Commit

1. Update `neo/projects.md` if projects completed
2. Commit changes to dotmatrix
3. Report back to Neo with entry IDs for anything archived

---

## Key Rules

1. **Database, not files** - `mx zion add`, never write `.md` to zion/
2. **Archive first, synthesize second** - Store verbatim original, then extract knowledge
3. **Nothing thrown away** - Every document becomes an archive entry
4. **Link archives to synthesis** - Tag synthesized entries with `archive-ref:<id>`
5. **Timebox** - 10 min max per agent's RAM
