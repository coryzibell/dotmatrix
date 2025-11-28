# Beads Evaluation Report

**Evaluated by:** Zion Control
**Date:** 2025-11-28
**Repository:** https://github.com/steveyegge/beads
**Status:** Alpha (3.3k stars, production-ready for dev workflows)

---

## Executive Summary

Beads is a distributed issue tracker designed specifically for AI coding agents. It solves the context amnesia problem - agents losing track of multi-step plans across sessions - by providing persistent, queryable memory backed by git. The architecture is clever: local SQLite cache synced with JSONL files committed to git, creating a "feels like centralized database" experience with zero infrastructure.

**Relevance to Matrix architecture:** Complementary but different problem space. Beads targets *project work tracking* (tasks, dependencies, blockers) while Zion targets *knowledge permanence* (patterns, techniques, insights). There are architectural lessons worth adopting, but not direct competition.

---

## 1. What is Beads?

Beads is an **AI-native issue tracker** that gives agents persistent memory across session boundaries.

**The Problem It Solves:**
- Agents restart and lose context of complex multi-step plans
- Markdown plans become "swamps of rotten half-implemented" tasks
- No way to track discovered work during execution
- Context window exhaustion on long-horizon projects
- Multiple agents working concurrently create ID collisions

**The Solution:**
- Git-backed SQLite cache for fast local queries (<100ms)
- Hash-based IDs eliminate concurrent creation conflicts
- Dependency graph (blocks, related, parent-child, discovered-from)
- "Ready work" detection - agents query `bd ready` for unblocked tasks
- Automatic sync via git commit/pull with merge-friendly JSONL format

---

## 2. Indexing, Memory, and Context Architecture

### Storage Architecture

**Dual-format system:**
```
.beads/
  ├── beads.db          # SQLite cache (gitignored, local only)
  ├── issues.jsonl      # Source of truth (committed to git)
  ├── deletions.jsonl   # Tombstone records for cross-clone propagation
  └── metadata.json     # Database metadata
```

**Sync mechanism:**
- SQLite → JSONL: 5-second debounce after CRUD operations
- JSONL → SQLite: Auto-import when JSONL is newer (post-pull)
- Git hooks provide zero-lag export (pre-commit) and guaranteed import (post-merge)

### Issue Data Model

**Core fields:**
- Hash-based ID (4-6 character hex, collision-resistant)
- Hierarchical child IDs (dot notation: `bd-a3f8e9.1.2`)
- Status (open, in_progress, closed)
- Priority, labels, assignees
- Dependencies (four types: blocks, related, parent-child, discovered-from)
- Full audit trail

**Schema:** Version 9+ supports hash IDs. Migration required from sequential IDs.

### Memory Management

**Compaction strategy:**
- Semantic compaction reduces old closed issues
- Prevents database bloat while preserving audit history
- Graceful memory decay model

**Multi-project isolation:**
- Each project auto-discovers its own `.beads/` directory
- No global database - project-scoped by design

---

## 3. Architectural Lessons for Zion

### What We Can Adopt

**1. Dual-format pattern: Human-readable source + machine-queryable cache**

This is the killer insight. Beads proves the pattern works at scale:
- Markdown/JSONL for git-friendly authoring
- SQLite for fast structured queries
- Bidirectional sync keeps them consistent

**Direct application to Zion:**
We've already discussed this exact pattern in `zion/future/dotmatrix/zion-index-pipeline.md`. Beads validates it works. Our proposed architecture:
```
zion/               # Human-readable markdown (source of truth)
artifacts/          # Generated zion-index.json (query target)
```

**2. Auto-sync with debouncing**

5-second debounce after changes, git hooks for zero-lag commits. This prevents:
- Stale cache bugs
- Manual sync forgetting
- Merge conflicts from out-of-sync replicas

**Application:** Zion index regeneration could follow this model - debounced rebuild after writes, with optional immediate rebuild via hook.

**3. Hash-based IDs for distributed creation**

Sequential IDs cause collisions when multiple agents work concurrently. Hash-based IDs (with progressive length scaling) eliminate this via birthday paradox math.

**Application:** If we track learnings with IDs, use content-derived hashes rather than incrementing counters.

**4. Tombstone records for deletions**

`.beads/deletions.jsonl` propagates deletes across clones. Without this, deleted issues resurrect after git pull.

**Application:** If we support deletion in Zion index, need similar tombstone tracking.

**5. JSONL for git-friendly structured data**

Line-delimited JSON balances:
- Human readability (can grep/inspect)
- Merge-friendliness (line-based diffs)
- Structured parsing (JSON)

**Application:** Better format than JSON for multi-entry indexes. Git's three-way merge handles most conflicts naturally.

### What's Different

**Beads is task-centric, Zion is knowledge-centric:**

| Dimension | Beads | Zion |
|-----------|-------|------|
| **Scope** | Project work (tasks, bugs, features) | Patterns, techniques, insights |
| **Lifecycle** | Created → In Progress → Closed | Written once, referenced forever |
| **Dependencies** | Blocks, parent-child, discovered-from | Tags, categories, "Related" links |
| **Churn** | High (issues created/closed constantly) | Low (learnings accumulate slowly) |
| **Queries** | "What's ready to work on?" | "Have we solved this before?" |

Beads tracks *what to do*. Zion tracks *what we learned*.

**Beads requires per-project setup, Zion is global:**

Beads lives in each repo's `.beads/` directory. Zion is a single `/home/w3surf/.matrix/zion/` hierarchy.

**Beads emphasizes dependencies, Zion emphasizes categorization:**

Beads' graph model (four dependency types) supports complex task ordering. Zion's current structure uses directories (`pattern/`, `technique/`, `ritual/`, etc.) and tags for organization.

---

## 4. Competitive Analysis

**Verdict: Complementary, not competitive**

Beads and Zion solve adjacent problems in the agent memory hierarchy:

```
┌─────────────────────────────────────────┐
│ Zion (Permanent Knowledge)              │
│ - Patterns that work                    │
│ - Techniques worth preserving           │
│ - Hard-won insights                     │
│ Retention: Forever                      │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│ Beads (Project Task Graph)              │
│ - What needs doing                      │
│ - Dependencies and blockers             │
│ - Discovered work during execution      │
│ Retention: Project lifecycle            │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│ RAM (Session Context)                   │
│ - Working memory                        │
│ - Session notes                         │
│ - Temporary artifacts                   │
│ Retention: Until prune                  │
└─────────────────────────────────────────┘
```

**Could they integrate?**

Yes. Example workflow:
1. Agent starts session, runs `phone <project>` to get STATUS.md (Zion)
2. Agent queries `bd ready` to find unblocked tasks (Beads)
3. During work, agent references past learnings (Zion query)
4. After resolving blocker, agent files learning to Zion
5. Session ends, `bd sync` commits task updates (Beads)

**When to use which:**

- **Use Beads** when you need: Task dependencies, "ready work" detection, multi-agent coordination on project tasks
- **Use Zion** when you need: Pattern library, technique reference, "have we solved this before?" lookups

---

## 5. Specific Techniques Worth Adopting

### Immediate Adoption Candidates

**1. JSONL format for generated indexes**

Switch from JSON to JSONL for `artifacts/zion-index.json` (if we build it). Git-friendly line-based diffs, easier to parse incrementally.

**2. Content-derived hashes for entry IDs**

If we add IDs to Zion entries, use hash of (path + title + date) rather than sequential numbers.

**3. Debounced regeneration with hook override**

Auto-rebuild Zion index 5 seconds after any Zion write. Git pre-commit hook forces immediate rebuild for atomic commits.

**4. Explicit tombstones for deletions**

If we support deleting/archiving Zion entries, track in `zion-deletions.jsonl` to prevent resurrection after pull.

**5. `--json` flags for programmatic output**

Any Zion query scripts should support `--json` for agent consumption.

### Aspirational (if we scale)

**6. Schema versioning from day one**

Beads learned this lesson - had to migrate to schema v9 for hash IDs. If we build Zion index, version the format immediately.

**7. Orphan handling strategies**

Beads supports four strategies when imports detect orphaned dependencies (allow, resurrect, skip, strict). Similar logic for broken cross-references in Zion.

**8. `bd prime` equivalent**

Beads' `bd prime` injects ~1-2k tokens of context at session start (ready issues, recent changes). Zion could provide similar "essential context" summary.

### Not Applicable

**Dependency graph:** Overkill for Zion's knowledge-centric model. Simple "Related" links suffice.

**"Ready work" detection:** No equivalent in Zion - learnings don't have prerequisites.

**Status transitions:** Zion entries don't have lifecycle states (open → in_progress → closed).

---

## Architectural Recommendations

### Short Term (Now)

1. **Document the dual-format pattern** as a validated approach
   - Location: `zion/pattern/architecture/dual-format-storage.md`
   - Reference Beads as proof it scales

2. **Prototype JSONL-based Zion index**
   - Start with simple fields: path, title, category, date, summary
   - Use content-derived hashes for IDs
   - Implement debounced rebuild

3. **Add `--json` flag to any Zion query utilities** we build

### Medium Term (When Zion > 50 entries)

4. **Implement auto-sync with git hooks**
   - Pre-commit: Force index rebuild
   - Post-merge: Detect stale index and rebuild

5. **Add tombstone tracking** for archived/deleted entries

6. **Consider `zion prime`** - condensed context injection at session start

### Long Term (If We Need Task Tracking)

7. **Evaluate Beads adoption for project work tracking**
   - Run `bd init` in active repos
   - Integrate with `phone` program - STATUS.md could include `bd ready` summary
   - Train agents to use `bd create` for discovered work

8. **Cross-tool integration**
   - Zion learnings reference Beads issue IDs that prompted them
   - Beads issue resolution triggers Zion learning extraction

---

## Conclusion

Beads solves a real problem for AI agents: persistent task memory across sessions. The architecture is elegant - git-backed SQLite with JSONL source of truth - and validates patterns we've already discussed for Zion.

**Key takeaway:** The dual-format approach (human-readable source + machine-queryable cache) works at scale. Beads proves it. We should adopt it for Zion indexing.

**Recommendation:** Don't adopt Beads wholesale, but steal the architectural patterns. JSONL format, hash-based IDs, debounced sync, tombstone deletions - these are battle-tested techniques worth integrating.

**Strategic positioning:** Zion and Beads occupy different layers of the memory hierarchy. Zion is permanent knowledge, Beads is project work tracking. They complement rather than compete. Future integration could be powerful - agents that learn from Zion and execute via Beads.

---

## References

- Beads Repository: https://github.com/steveyegge/beads
- Our prior art: `zion/future/dotmatrix/zion-index-pipeline.md`
- Related pattern: `zion/pattern/dotmatrix/status-heartbeat.md`
