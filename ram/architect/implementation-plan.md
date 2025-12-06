# SurrealDB Migration: Implementation Plan

## Component Ownership

Smith should implement in this order:

### Phase 1: Foundation (Est. 2-3 hours)

1. **Add surrealdb dependency**
   - `Cargo.toml`: Add `surrealdb = { version = "2", features = ["kv-rocksdb"] }`
   - Feature flag: `--features surrealdb` for opt-in during development

2. **Create `src/surreal_db.rs`**
   - `SurrealDatabase` struct
   - `open()` with RocksDB backend
   - Schema application on first open

3. **Define trait abstraction**
   - `src/store.rs`: `KnowledgeStore` trait
   - Implement for both `Database` (SQLite) and `SurrealDatabase`

### Phase 2: Core Operations (Est. 3-4 hours)

4. **Knowledge CRUD**
   - `upsert_knowledge()` - with tag/applicability edge management
   - `get()` - fetch with related edges
   - `delete()` - cascades edges automatically
   - `search()` - use FTS indexes

5. **Lookup table operations**
   - `list_categories()`, `list_projects()`, etc.
   - `upsert_*()` for each lookup type

6. **Relationship operations**
   - `add_relationship()` - creates edge
   - `list_relationships_for_entry()` - graph traversal
   - `delete_relationship()`

### Phase 3: CLI Integration (Est. 2 hours)

7. **Update `src/zion.rs`**
   - Accept store implementation via trait object
   - Factory function to create correct backend based on config/flag

8. **Config for backend selection**
   - `~/.config/mx/config.toml`: `zion_backend = "sqlite" | "surrealdb"`
   - Or environment variable: `MX_ZION_BACKEND`

### Phase 4: Migration (Est. 2 hours)

9. **Migration command**
   - `mx zion migrate --to surrealdb`
   - Opens both databases
   - Transfers all data
   - Validates counts
   - Reports success/failure

10. **Validation helpers**
    - Count comparison
    - Random sample verification
    - Relationship integrity check

### Phase 5: Cleanup (Est. 1 hour)

11. **Remove SQLite code path** (after validation period)
    - Remove `rusqlite` dependency
    - Remove `src/db.rs`
    - Remove feature flag
    - Archive migration code

## File Changes

```
mx/
  Cargo.toml                 # Add surrealdb dependency
  src/
    db.rs                    # Existing - keep during transition
    surreal_db.rs            # NEW - SurrealDB implementation
    store.rs                 # NEW - KnowledgeStore trait
    knowledge.rs             # Minor updates to struct derives
    schema.sql               # Keep for SQLite
    surrealdb-schema.surql   # NEW - SurrealDB schema
    zion.rs                  # Update to use trait abstraction
    migrations/
      sqlite_to_surreal.rs   # NEW - Migration logic
```

## Testing Strategy

1. **Unit tests**: Each `SurrealDatabase` method
2. **Integration tests**: Full workflow (add, search, relate, delete)
3. **Migration tests**: Round-trip data integrity
4. **Performance benchmarks**: Search latency, write throughput

## Rollback Plan

If issues discovered post-migration:

1. Keep SQLite backup: `~/.matrix/zion/knowledge.db.backup`
2. Config switch back to SQLite
3. No data loss - both databases exist

## Dependencies

```toml
[dependencies]
surrealdb = { version = "2", features = ["kv-rocksdb"], optional = true }
tokio = { version = "1", features = ["rt-multi-thread", "macros"] }

[features]
default = []
surrealdb = ["dep:surrealdb"]
```

## Async Consideration

SurrealDB is async-only. Options:

1. **Make mx async** - Use tokio runtime for CLI
2. **Block on async** - Use `tokio::runtime::Runtime::block_on()`

Recommendation: Option 2 for minimal disruption. The CLI is already synchronous; wrap async calls at the boundary.

```rust
impl SurrealDatabase {
    fn runtime() -> &'static Runtime {
        static RT: OnceLock<Runtime> = OnceLock::new();
        RT.get_or_init(|| Runtime::new().unwrap())
    }

    pub fn search(&self, query: &str) -> Result<Vec<KnowledgeEntry>> {
        Self::runtime().block_on(self.search_async(query))
    }

    async fn search_async(&self, query: &str) -> Result<Vec<KnowledgeEntry>> {
        // actual async implementation
    }
}
```
