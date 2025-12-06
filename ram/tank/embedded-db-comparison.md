# Embedded Database Alternatives to SQLite for Rust CLI

Research compiled by Tank | December 2025

## Executive Summary

For a **knowledge base use case** (text documents, code snippets, tagging, full-text search), the recommended options in order are:

1. **SurrealDB Embedded** - Best overall for multi-model needs with native FTS
2. **libSQL/Turso** - Best SQLite-compatible option with better concurrency
3. **DuckDB** - Best for analytical queries and large-scale text processing
4. **LanceDB** - Best if vector/embeddings are primary concern

---

## Comparison Table

| Database | Rust Maturity | FTS Native | Concurrent Writes | Schema Flexibility | Migration from SQLite | Best For |
|----------|---------------|------------|-------------------|-------------------|----------------------|----------|
| **DuckDB** | Good (bindings) | Yes (BM25) | Single writer | SQL, columnar | Moderate | Analytics, bulk text processing |
| **libSQL** | Excellent | Yes (FTS5) | Improved (BEGIN CONCURRENT) | SQL | Easy (drop-in) | SQLite replacement with extras |
| **SurrealDB** | Excellent (native) | Yes (custom engine) | Yes (ACID) | Multi-model | Moderate | Documents, graphs, full-text |
| **redb** | Excellent (pure Rust) | No | Single writer | Key-value only | Hard | Simple KV with ACID |
| **sled** | Good (pure Rust, beta) | No | Single writer | Key-value only | Hard | Async KV operations |
| **LanceDB** | Good (native core) | Yes | Append-optimized | Columnar + vectors | Hard | Vector search, embeddings |
| **Meilisearch** | SDK only (not embedded) | Yes (excellent) | N/A | Document | N/A | Dedicated search server |

---

## Detailed Analysis

### DuckDB

**Rust Crate**: `duckdb` (crates.io) - bindings to C API, similar API to rusqlite

**Better than SQLite at**:
- Analytical/OLAP queries (columnar storage)
- Bulk data ingestion and processing
- Complex aggregations and window functions
- Parallel query execution
- Arrow integration for data pipelines

**Worse than SQLite at**:
- OLTP workloads (frequent small writes)
- Build times (large compilation)
- Single-writer limitation persists
- ICU extension missing in bundled builds (date/time limitations)

**Full-Text Search**: Yes, via FTS extension
- BM25 scoring algorithm
- Snowball stemmer (17+ languages)
- Stopword filtering
- **Limitation**: Index does not auto-update on table changes

**Migration Complexity**: Moderate
- Similar SQL syntax
- API mirrors rusqlite
- Schema migration required for columnar optimization

**Sources**: [DuckDB Rust Client](https://duckdb.org/docs/stable/clients/rust), [DuckDB FTS](https://duckdb.org/docs/stable/core_extensions/full_text_search)

---

### libSQL (Turso's SQLite Fork)

**Rust Crate**: Native Rust SDK via Turso

**Better than SQLite at**:
- Concurrent writes (BEGIN CONCURRENT experimental branch)
- Native vector search (no extension needed)
- Encryption at rest
- Replication support
- Active development with modern features

**Worse than SQLite at**:
- Ecosystem maturity (newer project)
- Some experimental features not production-ready
- Turso/Limbo rewrite is still evolving

**Full-Text Search**: Yes, inherits SQLite FTS5
- Full FTS5 compatibility
- Can combine with native vector search for hybrid retrieval

**Migration Complexity**: Easy
- Drop-in SQLite replacement
- Same file format, same API
- Additional features are additive

**Note**: Turso is rewriting SQLite entirely in Rust (codename "Limbo", now "Turso Database"). libSQL is production-ready; the Rust rewrite is not yet production-ready but evolving rapidly.

**Sources**: [libSQL GitHub](https://github.com/tursodatabase/libsql), [Turso Vector Search](https://turso.tech/vector)

---

### SurrealDB Embedded

**Rust Crate**: `surrealdb` - native Rust, first-class support

**Better than SQLite at**:
- Multi-model support (document, graph, relational, time-series, KV)
- Native full-text search with custom ACID-compliant engine
- Schema flexibility (schemaless or strict)
- Graph traversal queries
- Live queries and subscriptions
- Concurrent ACID transactions

**Worse than SQLite at**:
- Ecosystem maturity (newer)
- SQL familiarity (SurrealQL is different)
- Disk space efficiency for simple relational data
- Learning curve

**Full-Text Search**: Yes, custom-built engine
- BM25 and TF-IDF scoring
- Custom analyzers with multiple tokenizers
- Ngram, EdgeNGram, Snowball filters
- 17 language support
- ACID-compliant (unlike Tantivy/Lucene)
- Query with native SurrealQL (no separate query language)

**Migration Complexity**: Moderate
- Different query language (SurrealQL)
- Schema redesign may be beneficial
- Data export/import required

**Sources**: [SurrealDB Embedding Rust](https://surrealdb.com/docs/surrealdb/embedding/rust), [SurrealDB FTS](https://surrealdb.com/features/full-text-search)

---

### redb

**Rust Crate**: `redb` - pure Rust, ACID

**Better than SQLite at**:
- Pure Rust (no C dependencies)
- Simple, focused API
- Individual write performance (227ms vs 388ms lmdb in benchmarks)
- Memory safety guarantees

**Worse than SQLite at**:
- No SQL query language
- No full-text search
- Key-value only (no relations, no complex queries)
- Less mature than SQLite

**Full-Text Search**: No
- Would need to integrate with Tantivy separately

**Migration Complexity**: Hard
- Completely different paradigm (KV vs relational)
- No query language, just key lookups
- Application logic must handle all querying

**Use Case**: Best for simple key-value storage with ACID guarantees, not knowledge bases

**Sources**: [redb GitHub](https://github.com/cberner/redb)

---

### sled

**Rust Crate**: `sled` - pure Rust, lock-free

**Better than SQLite at**:
- Pure Rust
- Lock-free data structures
- Optimized for SSDs
- Async-friendly with `flush_async`

**Worse than SQLite at**:
- Still beta (not production-ready)
- No SQL, key-value only
- Less actively maintained (author working on new engine)
- No full-text search

**Full-Text Search**: No

**Migration Complexity**: Hard
- Same issues as redb (KV paradigm shift)

**Status Warning**: Described as "the champagne of beta embedded databases" - use with caution for production

**Sources**: [sled GitHub](https://github.com/spacejam/sled)

---

### LanceDB

**Rust Crate**: `lancedb` - core written in Rust

**Better than SQLite at**:
- Vector similarity search (native)
- Embedding management
- Columnar storage (Lance format)
- Arrow integration
- Multi-modal data (text, images, etc.)
- GPU-accelerated index building

**Worse than SQLite at**:
- General-purpose relational queries
- Traditional OLTP workloads
- Ecosystem maturity for non-vector use cases

**Full-Text Search**: Yes
- Combined with vector search for hybrid retrieval
- SQL query support

**Migration Complexity**: Hard
- Different paradigm (vector-first)
- Best suited for AI/ML workloads
- Schema redesign needed

**Use Case**: Ideal if your knowledge base heavily relies on semantic search/embeddings

**Sources**: [LanceDB Docs](https://lancedb.com/documentation/overview/index.html), [LanceDB Rust Crate](https://docs.rs/lancedb/latest/lancedb/)

---

### Meilisearch

**Rust Crate**: `meilisearch-sdk` - **client SDK only, not embeddable**

**Status**: Meilisearch itself is written in Rust, but it runs as a **server**, not an embedded library. There is a lower-level `milli` crate that can be embedded, but it lacks the full API polish.

**Not recommended** for your use case as it requires running a separate process.

**Sources**: [Meilisearch Rust SDK](https://github.com/meilisearch/meilisearch-rust), [milli embedding discussion](https://github.com/meilisearch/meilisearch/discussions/1523)

---

## Recommendations for Knowledge Base Use Case

### Requirements Analysis:
- Text documents and code snippets storage
- Tagging system
- Full-text search
- Embedded (no server)
- Rust CLI tool

### Recommendation Tiers:

#### Tier 1: SurrealDB Embedded
**Why**: Native Rust, multi-model (perfect for documents + tags as graph relations), built-in FTS with ACID compliance, excellent Rust SDK.

```rust
// Example: Documents with tags as graph relations
use surrealdb::engine::local::RocksDb;
let db = Surreal::new::<RocksDb>("path/to/db").await?;
```

**Caveats**: Learning SurrealQL, newer ecosystem

---

#### Tier 2: libSQL
**Why**: Drop-in SQLite replacement, FTS5 support, better concurrency, native vector search for future semantic features.

```rust
// Easy migration from existing SQLite code
```

**Caveats**: Some features still experimental

---

#### Tier 3: DuckDB + Tantivy Combo
**Why**: DuckDB for structured data/analytics, Tantivy for dedicated FTS. Best-in-class for each responsibility.

**Caveats**: Two systems to manage, more complexity

---

#### Tier 4: LanceDB
**Why**: If you anticipate heavy use of embeddings/semantic search, start here.

**Caveats**: Vector-first design may be overkill if FTS is primary need

---

## Concurrent Writes Deep Dive

SQLite's WAL mode limitation (single writer) is a known pain point. Here's how alternatives compare:

| Database | Concurrent Write Strategy |
|----------|--------------------------|
| SQLite WAL | Single writer, readers don't block |
| libSQL | BEGIN CONCURRENT (optimistic page-level locking) |
| SurrealDB | Full ACID concurrent transactions |
| DuckDB | Single writer (OLAP-focused) |
| redb | Single writer, ACID |
| LanceDB | Append-optimized, versioning |

For a CLI tool where writes are typically single-user, this may not be critical. libSQL or SurrealDB are best if concurrent writes matter.

---

## File Output

This research is stored at: `/home/w3surf/.matrix/ram/tank/embedded-db-comparison.md`
