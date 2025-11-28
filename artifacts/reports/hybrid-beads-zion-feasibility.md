# Hybrid Beads-Zion Feasibility Report

**Prepared by:** Zion Control
**Date:** 2025-11-28
**Request:** Neo - Evaluate fork vs build for hybrid task+knowledge system

---

## Executive Summary

**Recommendation: Build from scratch, steal the patterns.**

Forking Beads would require fighting its core assumptions (per-project, task-centric, Go ecosystem). A purpose-built hybrid system that adopts Beads' proven patterns (JSONL, hash IDs, SQLite cache, debounced sync) while preserving Zion's knowledge model is cleaner and more maintainable.

Estimated effort: **2-3 weekends** for MVP, **1-2 months** for production-ready.

---

## 1. Fork vs Build Analysis

### Beads Architecture Overview

Beads is a **22-package Go application** with significant complexity:

```
internal/
  autoimport/     - JSONL auto-import on git pull
  beads/          - Core storage abstraction
  compact/        - Semantic compaction
  config/         - Configuration management
  daemon/         - Background sync daemon
  deletions/      - Tombstone tracking
  export/         - JSONL export
  git/            - Git integration
  importer/       - Import logic
  merge/          - Conflict resolution
  storage/        - SQLite + memory backends
  types/          - Core data types
  ...12 more packages
```

### Fork Costs

| Factor | Assessment |
|--------|------------|
| **Language** | Go - we have Rust preference (base-d). Either learn Go internals or rewrite. |
| **Scope model** | Per-project `.beads/` directories. Zion is global `~/.matrix/zion/`. Fundamental architecture clash. |
| **Data model** | Issue-centric with status lifecycle. Knowledge entries have no lifecycle. |
| **Dependencies** | 30+ Go dependencies including Anthropic SDK, Cobra, Viper, wazero. Heavy. |
| **Maintenance** | Fork diverges from upstream. We carry all bugs, miss all improvements. |
| **Customization** | Would need to gut Issue model, remove status/priority/blocking logic, add categories/tags. |

### Fork Benefits

| Factor | Assessment |
|--------|------------|
| **Proven patterns** | SQLite cache + JSONL sync is battle-tested |
| **Hash IDs** | ID generation already implemented |
| **Git hooks** | Pre-commit/post-merge already wired |
| **Compaction** | Semantic decay model could apply to stale knowledge |
| **CLI framework** | Cobra-based CLI is solid |

### Build Costs

| Factor | Assessment |
|--------|------------|
| **Implementation time** | Need to write SQLite layer, sync logic, CLI |
| **Testing** | Edge cases in sync, concurrency, conflict resolution |
| **Documentation** | Need to document new tool |

### Build Benefits

| Factor | Assessment |
|--------|------------|
| **Purpose-fit** | Designed for our exact use case |
| **Language choice** | Could use Rust (matches base-d) or Go (matches existing tooling) |
| **Global scope** | Single `~/.matrix/` hierarchy, no per-project fragmentation |
| **Unified model** | Can design hybrid data model from scratch |
| **No upstream debt** | We own it completely |
| **Integration** | Native integration with phone, sync, hardline programs |

### Verdict: Build

Forking Beads means:
1. Learning a 10k+ LOC Go codebase
2. Ripping out Issue lifecycle (status, blocking, dependencies)
3. Changing scope model from per-project to global
4. Maintaining a divergent fork

Building means:
1. ~2k LOC for core functionality
2. Steal proven patterns (JSONL format, hash IDs, debounced sync)
3. Design for our exact needs
4. Clean integration with Matrix architecture

---

## 2. Unified Data Model

### The Challenge

Two fundamentally different entry types:

| Dimension | Tasks | Knowledge |
|-----------|-------|-----------|
| **Lifecycle** | Created -> In Progress -> Closed | Written once, referenced forever |
| **Scope** | Project-specific | Global |
| **Churn** | High (create/close daily) | Low (accumulate slowly) |
| **Relationships** | Blocking, parent-child, discovered-from | Related, supersedes, extends |
| **Queries** | "What's ready to work on?" | "Have we solved this before?" |
| **Fields** | Status, priority, assignee, blockers | Category, tags, source, applicability |

### Option A: Single Table, Discriminated Union

```sql
CREATE TABLE entries (
  id TEXT PRIMARY KEY,          -- Hash-based (bd-a3f8e9)
  entry_type TEXT NOT NULL,     -- 'task' or 'knowledge'
  title TEXT NOT NULL,
  body TEXT,

  -- Task-specific (NULL for knowledge)
  status TEXT,                  -- open, in_progress, closed
  priority INTEGER,
  assignee TEXT,
  project TEXT,                 -- Project scope

  -- Knowledge-specific (NULL for tasks)
  category TEXT,                -- pattern, technique, insight, ritual, project
  applicability TEXT,           -- When/where this applies
  source_project TEXT,          -- Where it was learned
  source_agent TEXT,            -- Who captured it

  -- Shared
  tags TEXT,                    -- JSON array
  created_at TEXT,
  updated_at TEXT,
  content_hash TEXT             -- For sync dedup
);
```

**Pros:** Single query surface, simpler sync
**Cons:** Sparse columns, mixed concerns, awkward queries

### Option B: Dual Tables, Shared Infrastructure

```sql
-- Tasks: project-scoped, lifecycle-driven
CREATE TABLE tasks (
  id TEXT PRIMARY KEY,
  project TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  status TEXT DEFAULT 'open',
  priority INTEGER DEFAULT 2,
  assignee TEXT,
  created_at TEXT,
  updated_at TEXT,
  closed_at TEXT,
  content_hash TEXT
);

-- Knowledge: global, permanent
CREATE TABLE knowledge (
  id TEXT PRIMARY KEY,
  category TEXT NOT NULL,       -- pattern, technique, insight, ritual, project
  title TEXT NOT NULL,
  body TEXT,
  applicability TEXT,
  source_project TEXT,
  source_agent TEXT,
  tags TEXT,                    -- JSON array
  created_at TEXT,
  updated_at TEXT,
  content_hash TEXT
);

-- Shared: relationships between any entries
CREATE TABLE relationships (
  from_id TEXT NOT NULL,
  to_id TEXT NOT NULL,
  rel_type TEXT NOT NULL,       -- blocks, related, supersedes, extends, learned-from
  created_at TEXT,
  PRIMARY KEY (from_id, to_id, rel_type)
);

-- Shared: tags index
CREATE TABLE tags (
  entry_id TEXT NOT NULL,
  tag TEXT NOT NULL,
  PRIMARY KEY (entry_id, tag)
);
```

**Pros:** Clean separation, appropriate fields per type, natural queries
**Cons:** Two tables to sync, cross-type relationships need care

### Recommendation: Option B (Dual Tables)

The models are too different to force into one table cleanly. Dual tables with shared infrastructure (relationships, tags) gives us:

1. **Natural queries** - `SELECT * FROM tasks WHERE status = 'open'` vs `SELECT * FROM knowledge WHERE category = 'pattern'`
2. **Appropriate fields** - No NULL columns for unrelated concerns
3. **Clear semantics** - Tasks have lifecycle, knowledge is permanent
4. **Cross-referencing** - Tasks can link to knowledge ("learned-from"), knowledge can reference originating task

---

## 3. Query Patterns

### Task Queries (Beads-style)

```sql
-- Ready work: open tasks with no unresolved blockers
SELECT t.* FROM tasks t
WHERE t.status = 'open'
  AND t.project = ?
  AND NOT EXISTS (
    SELECT 1 FROM relationships r
    JOIN tasks blocker ON r.to_id = blocker.id
    WHERE r.from_id = t.id
      AND r.rel_type = 'blocks'
      AND blocker.status != 'closed'
  )
ORDER BY t.priority DESC, t.created_at ASC;

-- Blocked work
SELECT t.*, COUNT(r.to_id) as blocker_count
FROM tasks t
JOIN relationships r ON t.id = r.from_id AND r.rel_type = 'blocks'
JOIN tasks blocker ON r.to_id = blocker.id AND blocker.status != 'closed'
WHERE t.status = 'open'
GROUP BY t.id;

-- Stale tasks (no update in N days)
SELECT * FROM tasks
WHERE status != 'closed'
  AND updated_at < datetime('now', '-7 days');
```

### Knowledge Queries (Zion-style)

```sql
-- Search by category
SELECT * FROM knowledge WHERE category = 'pattern';

-- Full-text search (requires FTS5)
SELECT * FROM knowledge_fts WHERE knowledge_fts MATCH ?;

-- Find related knowledge
SELECT k.* FROM knowledge k
JOIN relationships r ON k.id = r.to_id
WHERE r.from_id = ? AND r.rel_type IN ('related', 'extends');

-- "Have we solved this before?" - semantic requires embedding
-- For now: keyword search across title, body, tags
SELECT * FROM knowledge
WHERE title LIKE '%' || ? || '%'
   OR body LIKE '%' || ? || '%'
   OR tags LIKE '%' || ? || '%';
```

### Cross-Type Queries

```sql
-- What knowledge came from this task?
SELECT k.* FROM knowledge k
JOIN relationships r ON k.id = r.from_id
WHERE r.to_id = ? AND r.rel_type = 'learned-from';

-- Find tasks that might benefit from this knowledge
-- (by matching project or tags)
SELECT t.* FROM tasks t
WHERE t.project = (SELECT source_project FROM knowledge WHERE id = ?)
   OR EXISTS (
     SELECT 1 FROM tags tk
     JOIN tags tt ON tk.tag = tt.tag
     WHERE tk.entry_id = ? AND tt.entry_id = t.id
   );
```

---

## 4. Storage Architecture

### Recommendation: Dual SQLite + Dual JSONL

```
~/.matrix/
  db/
    tasks.db              # SQLite cache for tasks
    knowledge.db          # SQLite cache for knowledge
  zion/
    index.jsonl           # Knowledge entries (source of truth)
    deletions.jsonl       # Tombstones for deleted knowledge
    pattern/              # Human-readable markdown (authoring)
    technique/
    insight/
    ritual/
    project/
  tasks/
    index.jsonl           # Task entries (source of truth)
    deletions.jsonl       # Tombstones for deleted tasks
```

### Why Not Unified?

1. **Different retention** - Tasks are project-scoped, can be archived. Knowledge is permanent.
2. **Different sync patterns** - Tasks sync with project repos. Knowledge syncs with dotmatrix.
3. **Different backup strategies** - Lose tasks? Recreate from PRs/commits. Lose knowledge? Gone forever.
4. **Cleaner tooling** - `mx tasks ready` vs `mx zion search` have different UX needs.

### Sync Strategy

**Knowledge (Zion):**
- Source of truth: Markdown files in `zion/` directories
- Index: Generated `zion/index.jsonl` from markdown frontmatter + content
- Cache: `db/knowledge.db` for fast queries
- Sync: Debounced rebuild after any `zion/**/*.md` change

**Tasks:**
- Source of truth: `tasks/index.jsonl`
- Cache: `db/tasks.db` for fast queries
- Sync: Debounced export after CRUD, auto-import on pull

### Git Integration

```
~/.matrix/
  .gitignore:
    db/                   # SQLite caches are local-only

  Committed:
    zion/**/*.md          # Human-readable knowledge
    zion/index.jsonl      # Machine-readable knowledge index
    zion/deletions.jsonl  # Tombstones
    tasks/index.jsonl     # Task data
    tasks/deletions.jsonl # Task tombstones
```

---

## 5. Migration Path

### Existing Zion Content

Current structure:
```
zion/
  pattern/
    parsing/unicode-delimiters.md
    orchestration/identity-synthesis.md
    contracts/merovingian-review.md
    dotmatrix/program-libraries.md
    dotmatrix/status-heartbeat.md
  technique/
    refactoring/modular-extraction.md
    ux/personas/...
    ci/tag-based-releases.md
  insight/
    cross-platform-go.md
  ritual/
    commit/commit-signatures.md
    workflow/hardline.md
  project/
    base-d/STATUS.md
    base-d/simd-implementation.md
    INDEX.md
  future/
    ...proposals not yet in knowledge base
```

### Migration Steps

1. **Add frontmatter to existing markdown** (one-time)
   ```yaml
   ---
   id: ptn-unicode-delimiters
   category: pattern
   tags: [parsing, unicode, delimiters]
   created: 2025-11-28
   source_agent: zion-control
   ---
   ```

2. **Build index generator**
   - Walk `zion/**/*.md` (excluding `future/`)
   - Parse frontmatter + extract summary (first paragraph)
   - Write to `zion/index.jsonl`

3. **Build SQLite importer**
   - Read `zion/index.jsonl`
   - Populate `knowledge` table
   - Generate content hashes for dedup

4. **Wire sync hooks**
   - File watcher on `zion/**/*.md`
   - Debounced regenerate (5 seconds)
   - Git pre-commit: force regenerate

### Estimated Migration Effort

| Task | Effort |
|------|--------|
| Add frontmatter to ~25 existing files | 1 hour |
| Build index generator (Rust or Go) | 4 hours |
| Build SQLite cache layer | 4 hours |
| Wire file watcher + sync | 4 hours |
| **Total migration** | ~2 days |

---

## 6. Effort Estimate

### MVP (Weekend Project)

**Scope:** Knowledge indexing only, no tasks

| Component | Hours |
|-----------|-------|
| Frontmatter schema definition | 1 |
| Index generator (walk + parse + output JSONL) | 4 |
| SQLite schema + import | 4 |
| Basic CLI (`mx zion search`, `mx zion list`) | 4 |
| File watcher + debounced sync | 3 |
| **Total** | **16 hours (2 weekends)** |

### Phase 2: Task Tracking

**Scope:** Add Beads-style task management

| Component | Hours |
|-----------|-------|
| Task data model + SQLite schema | 2 |
| CRUD operations | 4 |
| Dependency graph (blocks, parent-child) | 6 |
| Ready work query | 2 |
| CLI (`mx task create`, `mx task ready`, `mx task close`) | 4 |
| JSONL export/import | 4 |
| Git hooks (pre-commit, post-merge) | 3 |
| **Total** | **25 hours (3-4 weekends)** |

### Phase 3: Integration

**Scope:** Wire into Matrix programs

| Component | Hours |
|-----------|-------|
| `phone` integration - include ready tasks in STATUS.md | 2 |
| `sync` integration - task creation from session context | 3 |
| `hardline` integration - link commits to tasks | 2 |
| Cross-type relationships (task -> knowledge) | 3 |
| **Total** | **10 hours (1 weekend)** |

### Phase 4: Polish

| Component | Hours |
|-----------|-------|
| Conflict resolution (concurrent edits) | 6 |
| Compaction (semantic decay for old closed tasks) | 4 |
| `--json` output for all commands | 2 |
| Documentation | 4 |
| **Total** | **16 hours (2 weekends)** |

### Grand Total

| Phase | Effort | Cumulative |
|-------|--------|------------|
| MVP | 2 weekends | 2 weekends |
| Task Tracking | 4 weekends | 6 weekends |
| Integration | 1 weekend | 7 weekends |
| Polish | 2 weekends | 9 weekends |

**Realistic timeline: 2-3 months of weekend work for production-ready system.**

---

## 7. Implementation Recommendations

### Language Choice

**Rust** (preferred):
- Matches base-d, builds on existing investment
- Cross-platform binaries
- Fast SQLite via rusqlite
- JSONL via serde_json

**Go** (alternative):
- Matches Beads, could reference its implementation
- Easier to prototype
- Cross-platform via goreleaser

**Recommendation:** Rust. We're already invested, and this becomes core infrastructure.

### CLI Design

```bash
# Knowledge (Zion)
mx zion search "pattern for"        # Full-text search
mx zion list --category pattern     # List by category
mx zion show ptn-unicode-delimiters # Show single entry
mx zion add pattern/new-thing.md    # Index new entry
mx zion rebuild                     # Force full rebuild

# Tasks
mx task create "Implement foo"      # Create task
mx task ready                       # Show ready work
mx task start bd-a3f8e9             # Mark in-progress
mx task close bd-a3f8e9 "Done"      # Close task
mx task block bd-a3f8e9 bd-b4c9f0   # Add blocker
mx task list --project base-d       # List by project

# Cross-type
mx link bd-a3f8e9 ptn-unicode-delimiters learned-from
mx related ptn-unicode-delimiters   # Show related entries
```

### Naming

Tool name options:
- `mx` - Matrix CLI (umbrella command)
- `zn` - Zion (knowledge-specific)
- `strand` - Extends Beads metaphor (knowledge as strands)

**Recommendation:** `mx` as umbrella with subcommands (`mx zion`, `mx task`). Single tool, multiple concerns.

---

## 8. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| **Scope creep** | MVP is knowledge-only. Tasks are Phase 2. |
| **Sync conflicts** | Start with last-write-wins. Add proper merge later. |
| **Performance at scale** | SQLite handles 100k entries easily. Not a near-term concern. |
| **Integration complexity** | Design API first, integrate after. |
| **Abandoned project** | MVP is valuable standalone. Each phase adds value. |

---

## 9. Decision Matrix

| Criterion | Fork Beads | Build Hybrid | Winner |
|-----------|------------|--------------|--------|
| Time to MVP | 2 weeks (if Go-fluent) | 2 weekends | Build (for us) |
| Maintenance burden | High (divergent fork) | Medium (we own it) | Build |
| Fit to requirements | Poor (wrong scope model) | Excellent | Build |
| Learning investment | Go codebase | Patterns only | Build |
| Integration with Matrix | Requires glue | Native | Build |
| Long-term flexibility | Constrained by upstream | Unlimited | Build |

---

## 10. Conclusion

**Build the hybrid system. Steal Beads' patterns.**

The patterns are the valuable part:
- JSONL for git-friendly structured data
- Hash-based IDs for distributed creation
- SQLite cache for fast queries
- Debounced sync for responsive UX
- Tombstones for deletion propagation

The implementation is specific to Beads' problem (per-project issue tracking). Our problem (global knowledge + project tasks) needs a different architecture.

**Next Steps:**

1. **Decide:** Go or Rust?
2. **Prototype:** Knowledge index generator (Phase 1)
3. **Validate:** Use it for a week, gather feedback
4. **Iterate:** Add task tracking if knowledge system proves valuable

---

## References

- Beads source: https://github.com/steveyegge/beads
- Prior evaluation: `/home/w3surf/.matrix/artifacts/reports/beads-evaluation.md`
- Zion index proposal: `/home/w3surf/.matrix/zion/future/dotmatrix/zion-index-pipeline.md`
- Status heartbeat pattern: `/home/w3surf/.matrix/zion/pattern/dotmatrix/status-heartbeat.md`
