# ADR-001: SQLite to SurrealDB Migration for Zion Knowledge Base

**Status:** Proposed
**Date:** 2024-12-06
**Decision Makers:** kautau, Neo

## Context

The Zion knowledge base currently uses SQLite with a normalized relational schema (v5). The system works but presents friction:

1. Junction tables for many-to-many relationships require multiple queries
2. Relationship traversal (knowledge -> related knowledge) is awkward in SQL
3. Full-text search relies on LIKE patterns (no FTS5 configured)
4. Schema migrations require manual SQL scripts

SurrealDB offers:
- Native graph edges for relationships
- Built-in full-text search
- Embedded mode with RocksDB backend (no server)
- Multi-model: documents + relations + graph in one
- SurrealQL with graph traversal operators

## Decision

Migrate from SQLite to SurrealDB embedded (RocksDB backend).

## Architecture Changes

### 1. Lookup Tables -> Records (Preserve)

Keep lookup tables as proper records. SurrealDB does not collapse them into strings - they remain queryable entities with metadata.

```surql
-- Categories remain records
DEFINE TABLE category SCHEMAFULL;
DEFINE FIELD description ON category TYPE string;
DEFINE FIELD created_at ON category TYPE datetime;

-- Source types remain records
DEFINE TABLE source_type SCHEMAFULL;
DEFINE FIELD description ON source_type TYPE string;
DEFINE FIELD created_at ON source_type TYPE datetime;
```

**Rationale:** Lookup tables provide referential integrity, queryable metadata (descriptions), and enable future expansion (e.g., adding category hierarchies).

### 2. Junction Tables -> Graph Edges

Replace junction tables with SurrealDB graph relations:

```
-- SQLite junction table approach
knowledge_applicability(entry_id, applicability_id)
tags(entry_id, tag)
relationships(from_entry_id, to_entry_id, relationship_type)

-- SurrealDB graph edge approach
knowledge:kn-abc123 -> applies_to -> applicability_type:rust
knowledge:kn-abc123 -> tagged_with -> tag:async
knowledge:kn-abc123 -> relates_to:extends -> knowledge:kn-def456
```

**Key insight:** Graph edges ARE the junction. No separate table needed.

### 3. Relationships -> Typed Graph Edges

Current `relationships` table becomes native graph edges:

```surql
DEFINE TABLE relates_to SCHEMAFULL TYPE RELATION
    IN knowledge OUT knowledge;
DEFINE FIELD relationship_type ON relates_to TYPE record<relationship_type>;
DEFINE FIELD created_at ON relates_to TYPE datetime;
```

Query pattern:
```surql
-- Find all knowledge that this entry extends
SELECT <-relates_to[WHERE relationship_type = relationship_type:extends]<-knowledge
FROM knowledge:kn-abc123;

-- Find related entries (both directions for non-directional types)
SELECT ->relates_to->knowledge, <-relates_to<-knowledge
FROM knowledge:kn-abc123;
```

### 4. Knowledge Entry Structure

```surql
DEFINE TABLE knowledge SCHEMAFULL;
DEFINE FIELD title ON knowledge TYPE string;
DEFINE FIELD body ON knowledge TYPE option<string>;
DEFINE FIELD summary ON knowledge TYPE option<string>;
DEFINE FIELD file_path ON knowledge TYPE option<string>;
DEFINE FIELD content_hash ON knowledge TYPE string;
DEFINE FIELD ephemeral ON knowledge TYPE bool DEFAULT false;
DEFINE FIELD created_at ON knowledge TYPE datetime;
DEFINE FIELD updated_at ON knowledge TYPE datetime;

-- Record links (replaces FKs)
DEFINE FIELD category ON knowledge TYPE record<category>;
DEFINE FIELD source_project ON knowledge TYPE option<record<project>>;
DEFINE FIELD source_agent ON knowledge TYPE option<record<agent>>;
DEFINE FIELD source_type ON knowledge TYPE record<source_type>;
DEFINE FIELD entry_type ON knowledge TYPE record<entry_type>;
DEFINE FIELD content_type ON knowledge TYPE record<content_type>;
DEFINE FIELD session ON knowledge TYPE option<record<session>>;

-- Full-text search index
DEFINE ANALYZER zion_analyzer TOKENIZERS class FILTERS lowercase, snowball(english);
DEFINE INDEX title_search ON knowledge FIELDS title SEARCH ANALYZER zion_analyzer;
DEFINE INDEX body_search ON knowledge FIELDS body SEARCH ANALYZER zion_analyzer;
DEFINE INDEX summary_search ON knowledge FIELDS summary SEARCH ANALYZER zion_analyzer;
```

### 5. Tag Modeling

Tags become their own records with edges:

```surql
DEFINE TABLE tag SCHEMAFULL;
DEFINE FIELD name ON tag TYPE string;
DEFINE FIELD created_at ON tag TYPE datetime;
DEFINE INDEX tag_name ON tag FIELDS name UNIQUE;

DEFINE TABLE tagged_with TYPE RELATION
    IN knowledge OUT tag;
```

Query tags:
```surql
-- Get all tags for an entry
SELECT ->tagged_with->tag.name FROM knowledge:kn-abc123;

-- Find entries by tag
SELECT <-tagged_with<-knowledge FROM tag:rust;
```

### 6. Applicability as Graph Edges

```surql
DEFINE TABLE applies_to TYPE RELATION
    IN knowledge OUT applicability_type;

DEFINE TABLE project_applies_to TYPE RELATION
    IN project OUT applicability_type;
```

## Full Schema (SurrealQL)

See companion file: `surrealdb-schema.surql`

## Migration Strategy

### Phase 1: Parallel Operation
1. Add surrealdb crate alongside rusqlite
2. Implement `SurrealDatabase` struct mirroring `Database` interface
3. Feature flag to switch between backends
4. Run both in sync during development

### Phase 2: Data Migration
```rust
// Migration script pseudocode
async fn migrate(sqlite: &Database, surreal: &Surreal<Db>) -> Result<()> {
    // 1. Migrate lookup tables first (they're referenced by others)
    for category in sqlite.list_categories()? {
        surreal.create(("category", &category.id))
            .content(category)
            .await?;
    }
    // ... repeat for all lookup tables

    // 2. Migrate knowledge entries
    for entry in sqlite.list_all()? {
        surreal.create(("knowledge", &entry.id))
            .content(entry)
            .await?;
    }

    // 3. Migrate junction table data as edges
    for (entry_id, tag) in sqlite.get_all_tags()? {
        // Create tag record if not exists
        surreal.query("CREATE tag:$tag SET name = $tag")
            .bind(("tag", &tag))
            .await?;
        // Create edge
        surreal.query("RELATE knowledge:$entry->tagged_with->tag:$tag")
            .bind(("entry", entry_id))
            .bind(("tag", tag))
            .await?;
    }

    // 4. Migrate relationships as edges
    for rel in sqlite.list_all_relationships()? {
        surreal.query(r#"
            RELATE knowledge:$from->relates_to->knowledge:$to
            SET relationship_type = relationship_type:$type,
                created_at = $created
        "#)
        .bind(...)
        .await?;
    }
}
```

### Phase 3: Cutover
1. Run migration script
2. Validate data integrity (counts, spot checks)
3. Switch feature flag to SurrealDB
4. Remove SQLite code path
5. Archive old knowledge.db

## Rust Implementation Patterns

### Database Wrapper

```rust
use surrealdb::{Surreal, engine::local::{Db, RocksDb}};

pub struct SurrealDatabase {
    db: Surreal<Db>,
}

impl SurrealDatabase {
    pub async fn open(path: &Path) -> Result<Self> {
        let db = Surreal::new::<RocksDb>(path).await?;
        db.use_ns("zion").use_db("knowledge").await?;

        // Apply schema
        db.query(include_str!("surrealdb-schema.surql")).await?;

        Ok(Self { db })
    }

    pub async fn upsert_knowledge(&self, entry: &KnowledgeEntry) -> Result<()> {
        // Upsert main record
        self.db.upsert(("knowledge", &entry.id))
            .content(entry)
            .await?;

        // Update tag edges (delete old, create new)
        self.db.query(r#"
            DELETE knowledge:$id->tagged_with;
            FOR $tag IN $tags {
                CREATE tag:$tag SET name = $tag ON DUPLICATE KEY UPDATE name = $tag;
                RELATE knowledge:$id->tagged_with->tag:$tag;
            };
        "#)
        .bind(("id", &entry.id))
        .bind(("tags", &entry.tags))
        .await?;

        Ok(())
    }

    pub async fn search(&self, query: &str) -> Result<Vec<KnowledgeEntry>> {
        let results: Vec<KnowledgeEntry> = self.db.query(r#"
            SELECT *,
                   ->tagged_with->tag.name AS tags,
                   ->applies_to->applicability_type AS applicability
            FROM knowledge
            WHERE title @@ $query
               OR body @@ $query
               OR summary @@ $query
            ORDER BY updated_at DESC
        "#)
        .bind(("query", query))
        .await?
        .take(0)?;

        Ok(results)
    }
}
```

### Trait Abstraction

```rust
#[async_trait]
pub trait KnowledgeStore {
    async fn upsert(&self, entry: &KnowledgeEntry) -> Result<()>;
    async fn get(&self, id: &str) -> Result<Option<KnowledgeEntry>>;
    async fn search(&self, query: &str) -> Result<Vec<KnowledgeEntry>>;
    async fn list_by_category(&self, category: &str) -> Result<Vec<KnowledgeEntry>>;
    async fn delete(&self, id: &str) -> Result<bool>;
    // ... etc
}

impl KnowledgeStore for Database { /* SQLite impl */ }
impl KnowledgeStore for SurrealDatabase { /* SurrealDB impl */ }
```

## Consequences

### Positive
- **Graph queries native:** Relationship traversal becomes natural
- **Full-text search built-in:** No external FTS setup
- **Simpler junction handling:** Edges replace junction tables
- **Future flexibility:** Can add graph analytics, path queries
- **Type safety:** SurrealDB schema enforcement

### Negative
- **Async required:** surrealdb crate is async-only
- **Binary size:** RocksDB adds to binary size
- **Learning curve:** New query language (SurrealQL)
- **Less mature:** SurrealDB is newer than SQLite
- **Testing:** Need to mock or use in-memory mode

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SurrealDB bugs/instability | Medium | High | Pin version, test thoroughly, keep SQLite backup |
| Performance regression | Low | Medium | Benchmark before/after, index carefully |
| Migration data loss | Low | Critical | Backup SQLite, validate counts, rollback plan |
| Async complexity | Medium | Low | Use tokio runtime already in place |

## Alternatives Considered

### 1. Add FTS5 to SQLite
- Pro: Minimal change
- Con: Still awkward graph queries, manual FTS setup

### 2. SQLite + Separate Graph DB (e.g., age)
- Pro: Best of both worlds
- Con: Two databases to maintain, sync complexity

### 3. DuckDB
- Pro: Analytical queries
- Con: No native graph support

## Open Questions

1. **Namespace strategy:** Single namespace or separate for private knowledge?
2. **Backup format:** SurrealDB export format vs custom JSON?
3. **Index tuning:** Which fields need indexes beyond FTS?

## References

- SurrealDB Docs: https://surrealdb.com/docs
- surrealdb crate: https://docs.rs/surrealdb
- Current schema: `/home/w3surf/work/personal/code/mx/src/schema.sql`
