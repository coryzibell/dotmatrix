# mx SurrealDB Migration Context

**Issue:** #51 - Migrate Zion knowledge base from SQLite to SurrealDB
**Branch:** `feature/surrealdb-migration` (pushed)
**Status:** Phase 1 complete, Phase 2 pending

## What We Did

1. **Researched embedded DB alternatives** - Tank compared SurrealDB, libSQL, DuckDB, LanceDB, redb, sled
2. **Selected SurrealDB** - Native Rust, graph edges, built-in FTS with BM25, embedded RocksDB backend (no SaaS)
3. **Architect designed migration** - ADR, schema, implementation plan in `~/.matrix/ram/architect/`
4. **Smith implemented Phase 1:**
   - Added `surrealdb` crate with `kv-rocksdb` feature
   - Created `src/surreal_db.rs` with `SurrealDatabase` struct
   - Schema at `schema/surrealdb-schema.surql` (embedded via `include_str!`)
   - RocksDB path: `~/.matrix/zion/knowledge.surreal/`
   - Async handled with static tokio Runtime (OnceLock pattern)

## Key Decisions

- **Full switch, not abstraction layer** - SurrealDB replaces SQLite entirely
- **Junction tables → graph edges** - `tagged_with`, `applies_to`, `relates_to` relations
- **Record links replace FKs** - `category: record<category>` not `category_id TEXT`
- **FTS built-in** - BM25 scoring with snowball stemmer

## Design Documents

- `~/.matrix/ram/architect/adr-001-surrealdb-migration.md`
- `~/.matrix/ram/architect/surrealdb-schema.surql`
- `~/.matrix/ram/architect/implementation-plan.md`
- `~/.matrix/ram/architect/query-examples.surql`

## Remaining Phases

2. **Core CRUD** - Add/update/delete knowledge, edge management for tags/applicability
3. **CLI Integration** - Trait abstraction, backend config
4. **Migration** - `mx zion migrate --to surrealdb` command
5. **Cleanup** - Remove SQLite after validation

## Next Step

Dispatch Smith for Phase 2: Core CRUD operations with edge management.
