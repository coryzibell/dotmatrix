# MX Zion Schema Upgrade - Architectural Design (REVISED)

**Date:** 2025-11-29
**Component:** mx knowledge database (Zion)
**Status:** Design Revision 2 - No Hardcoded Enums
**Revision Reason:** Eliminate ALL hardcoded strings for data that could vary

---

## Executive Summary

The current Zion knowledge schema contains structural defects: redundant data storage (dual tag systems), hardcoded string literals for categorical data, and missing normalization for enumerable fields. This revision creates lookup tables for ALL fields that could potentially be extended or modified.

**Critical Changes from Previous Design:**
1. **`applicability`** - Now a many-to-many relationship with `applicability_types` lookup table
2. **`source_project`** - Now FK to `projects` table with proper project metadata
3. **`rel_type` in relationships** - Now FK to `relationship_types` table
4. **Sessions table metadata** - Now uses `session_types` lookup instead of hardcoded strings

**Migration Strategy:** Additive schema changes with data preservation. Zero downtime. Backward-compatible reads during transition.

---

## 1. Field Analysis - What Needs Lookup Tables?

### Fields Requiring Normalization

| Field | Current Type | Issue | Solution |
|-------|-------------|-------|----------|
| `category` | TEXT | Hardcoded enum | ✅ Already designed: `categories` table |
| `source_agent` | TEXT | Hardcoded enum | ✅ Already designed: `agents` table |
| `source_type` | TEXT | Hardcoded enum | ✅ Already designed: `source_types` table |
| `entry_type` | TEXT | Hardcoded enum | ✅ Already designed: `entry_types` table |
| **`applicability`** | TEXT | **Free text, should be tagged** | ❌ **NEW: `applicability_types` + junction table** |
| **`source_project`** | TEXT | **Project names vary** | ❌ **NEW: `projects` table** |
| **`session_type` in sessions** | TEXT | **Hardcoded enum** | ❌ **NEW: `session_types` table** |
| **`rel_type` in relationships** | TEXT | **Hardcoded enum** | ❌ **NEW: `relationship_types` table** |

### Fields That Remain TEXT (Free-Form)

| Field | Type | Justification |
|-------|------|---------------|
| `title` | TEXT | Unique per entry, no enumeration |
| `body` | TEXT | Long-form content, not categorical |
| `summary` | TEXT | Generated text, not categorical |
| `file_path` | TEXT | Filesystem paths, not enumerable |
| `content_hash` | TEXT | SHA hashes, not enumerable |
| `metadata` in sessions | TEXT | JSON blob, flexible structure |

---

## 2. Revised Schema Design

### 2.1 Core Lookup Tables

```sql
-- Categories (pattern, technique, insight, etc.)
CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Projects (dotmatrix, mx, base-d, etc.)
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,               -- Slug: dotmatrix, mx, base-d
    name TEXT NOT NULL,                -- Display name: "dotmatrix", "MX CLI"
    path TEXT,                         -- File path: ~/work/personal/code/mx
    repo_url TEXT,                     -- GitHub URL
    description TEXT,                  -- What this project is
    active INTEGER DEFAULT 1,          -- Boolean: currently maintained
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Applicability types (cross-platform, rust-specific, etc.)
CREATE TABLE IF NOT EXISTS applicability_types (
    id TEXT PRIMARY KEY,               -- rust, python, cross-platform, linux-only
    description TEXT NOT NULL,         -- When/where this applies
    scope TEXT,                        -- language, platform, tool, domain
    created_at TEXT NOT NULL
);

-- Source types (manual, ram, cache, agent_session)
CREATE TABLE IF NOT EXISTS source_types (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Entry types (primary, summary, synthesis)
CREATE TABLE IF NOT EXISTS entry_types (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Relationship types (related, supersedes, extends, etc.)
CREATE TABLE IF NOT EXISTS relationship_types (
    id TEXT PRIMARY KEY,               -- related, supersedes, extends, implements
    description TEXT NOT NULL,
    directional INTEGER DEFAULT 1,     -- Boolean: does A->B differ from B->A?
    created_at TEXT NOT NULL
);

-- Session types (claude_desktop, agent_task, manual)
CREATE TABLE IF NOT EXISTS session_types (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Agents (neo, smith, trinity, etc.) - already exists
CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    description TEXT,
    domain TEXT,
    created_at TEXT,
    updated_at TEXT
);
```

### 2.2 Revised Sessions Table

```sql
-- Sessions (with FK to session_types)
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,               -- Session UUID or hash
    session_type_id TEXT NOT NULL,     -- FK to session_types
    project_id TEXT,                   -- FK to projects (nullable)
    started_at TEXT NOT NULL,
    ended_at TEXT,
    metadata TEXT,                     -- JSON: additional context

    FOREIGN KEY (session_type_id) REFERENCES session_types(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

### 2.3 Revised Knowledge Table

```sql
-- Knowledge entries (all FKs, no hardcoded strings)
CREATE TABLE IF NOT EXISTS knowledge (
    id TEXT PRIMARY KEY,
    category_id TEXT NOT NULL,         -- FK to categories
    title TEXT NOT NULL,
    body TEXT,
    summary TEXT,
    source_project_id TEXT,            -- FK to projects (nullable)
    source_agent_id TEXT,              -- FK to agents (nullable)
    file_path TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    content_hash TEXT NOT NULL,

    -- Provenance
    source_type_id TEXT NOT NULL,      -- FK to source_types
    entry_type_id TEXT NOT NULL,       -- FK to entry_types
    session_id TEXT,                   -- FK to sessions (nullable)
    ephemeral INTEGER DEFAULT 0,       -- Boolean: may be pruned

    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (source_project_id) REFERENCES projects(id),
    FOREIGN KEY (source_agent_id) REFERENCES agents(id),
    FOREIGN KEY (source_type_id) REFERENCES source_types(id),
    FOREIGN KEY (entry_type_id) REFERENCES entry_types(id),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

### 2.4 Applicability Junction Table (Many-to-Many)

```sql
-- Knowledge can have multiple applicability contexts
CREATE TABLE IF NOT EXISTS knowledge_applicability (
    entry_id TEXT NOT NULL,
    applicability_id TEXT NOT NULL,
    PRIMARY KEY (entry_id, applicability_id),
    FOREIGN KEY (entry_id) REFERENCES knowledge(id) ON DELETE CASCADE,
    FOREIGN KEY (applicability_id) REFERENCES applicability_types(id)
);
```

**Rationale:** A single knowledge entry can apply to multiple contexts:
- "This pattern applies to: rust, async programming, error handling"
- Each becomes a separate applicability type tag

### 2.5 Revised Relationships Table

```sql
-- Relationships between knowledge entries (with FK to relationship_types)
CREATE TABLE IF NOT EXISTS relationships (
    from_id TEXT NOT NULL,
    to_id TEXT NOT NULL,
    rel_type_id TEXT NOT NULL,         -- FK to relationship_types
    created_at TEXT NOT NULL,
    PRIMARY KEY (from_id, to_id, rel_type_id),
    FOREIGN KEY (from_id) REFERENCES knowledge(id) ON DELETE CASCADE,
    FOREIGN KEY (to_id) REFERENCES knowledge(id) ON DELETE CASCADE,
    FOREIGN KEY (rel_type_id) REFERENCES relationship_types(id)
);
```

### 2.6 Project Junction Tables

```sql
-- Project applicability (many-to-many: projects <-> applicability_types)
CREATE TABLE IF NOT EXISTS project_applicability (
    project_id TEXT NOT NULL,
    applicability_id TEXT NOT NULL,
    PRIMARY KEY (project_id, applicability_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (applicability_id) REFERENCES applicability_types(id)
);

-- Project tags (many-to-many: projects <-> freeform tags)
CREATE TABLE IF NOT EXISTS project_tags (
    project_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (project_id, tag),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

### 2.7 Existing Tables (No Changes)

```sql
-- Knowledge tags junction table (already normalized)
CREATE TABLE IF NOT EXISTS tags (
    entry_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (entry_id, tag),
    FOREIGN KEY (entry_id) REFERENCES knowledge(id) ON DELETE CASCADE
);

-- Deletions tombstones
CREATE TABLE IF NOT EXISTS deletions (
    id TEXT PRIMARY KEY,
    deleted_at TEXT NOT NULL
);
```

### 2.8 Indexes

```sql
-- Knowledge indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge(category_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_source_project ON knowledge(source_project_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_source_agent ON knowledge(source_agent_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_source_type ON knowledge(source_type_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_entry_type ON knowledge(entry_type_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_session ON knowledge(session_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_updated ON knowledge(updated_at);

-- Knowledge junction table indexes
CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag);
CREATE INDEX IF NOT EXISTS idx_applicability_entry ON knowledge_applicability(entry_id);
CREATE INDEX IF NOT EXISTS idx_applicability_type ON knowledge_applicability(applicability_id);

-- Project junction table indexes
CREATE INDEX IF NOT EXISTS idx_project_applicability_project ON project_applicability(project_id);
CREATE INDEX IF NOT EXISTS idx_project_applicability_type ON project_applicability(applicability_id);
CREATE INDEX IF NOT EXISTS idx_project_tags_project ON project_tags(project_id);
CREATE INDEX IF NOT EXISTS idx_project_tags_tag ON project_tags(tag);

-- Lookup table indexes
CREATE INDEX IF NOT EXISTS idx_agents_domain ON agents(domain);
CREATE INDEX IF NOT EXISTS idx_sessions_type ON sessions(session_type_id);
CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(rel_type_id);
CREATE INDEX IF NOT EXISTS idx_applicability_scope ON applicability_types(scope);
CREATE INDEX IF NOT EXISTS idx_projects_active ON projects(active);
```

---

## 3. Migration SQL (v2 to v3)

### 3.1 Complete Migration Script

```sql
-- Migration from v2 to v3
-- Eliminates ALL hardcoded enums, adds projects table, normalizes applicability
-- Safe to run multiple times (idempotent)

BEGIN TRANSACTION;

-- Step 1: Create new lookup tables
CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT,
    repo_url TEXT,
    description TEXT,
    active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS applicability_types (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    scope TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_types (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entry_types (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS relationship_types (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    directional INTEGER DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS session_types (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Step 2: Seed lookup tables with known values
INSERT OR IGNORE INTO categories (id, description, created_at) VALUES
    ('pattern', 'Recurring structural solutions', datetime('now')),
    ('technique', 'Specific procedural approaches', datetime('now')),
    ('insight', 'Key realizations and understanding', datetime('now')),
    ('ritual', 'Habitual practices and workflows', datetime('now')),
    ('artifact', 'Tools, scripts, templates', datetime('now')),
    ('chronicle', 'Historical records and narratives', datetime('now')),
    ('project', 'Project-specific knowledge', datetime('now')),
    ('future', 'Ideas and plans', datetime('now'));

INSERT OR IGNORE INTO source_types (id, description, created_at) VALUES
    ('manual', 'Manually entered knowledge', datetime('now')),
    ('ram', 'Absorbed from agent RAM', datetime('now')),
    ('cache', 'Absorbed from workflow cache', datetime('now')),
    ('agent_session', 'Captured during agent execution', datetime('now'));

INSERT OR IGNORE INTO entry_types (id, description, created_at) VALUES
    ('primary', 'Original source material', datetime('now')),
    ('summary', 'Condensed summary of primary material', datetime('now')),
    ('synthesis', 'Combined insights from multiple sources', datetime('now'));

INSERT OR IGNORE INTO relationship_types (id, description, directional, created_at) VALUES
    ('related', 'General association', 0, datetime('now')),
    ('supersedes', 'Replaces or deprecates', 1, datetime('now')),
    ('extends', 'Builds upon or expands', 1, datetime('now')),
    ('implements', 'Concrete realization of', 1, datetime('now')),
    ('contradicts', 'Conflicts with', 0, datetime('now'));

INSERT OR IGNORE INTO session_types (id, description, created_at) VALUES
    ('claude_desktop', 'Claude Desktop session', datetime('now')),
    ('agent_task', 'Agent task execution', datetime('now')),
    ('manual', 'Manual entry session', datetime('now')),
    ('batch_import', 'Bulk import operation', datetime('now'));

-- Seed known applicability types from existing data
INSERT OR IGNORE INTO applicability_types (id, description, scope, created_at)
SELECT DISTINCT
    LOWER(REPLACE(applicability, ' ', '-')),
    applicability,
    'general',
    datetime('now')
FROM knowledge
WHERE applicability IS NOT NULL AND applicability != '';

-- Seed known projects from existing data
INSERT OR IGNORE INTO projects (id, name, path, repo_url, description, active, created_at, updated_at)
SELECT DISTINCT
    source_project,
    source_project,
    NULL,
    NULL,
    'Migrated from v2 schema',
    1,
    datetime('now'),
    datetime('now')
FROM knowledge
WHERE source_project IS NOT NULL AND source_project != '';

-- Add well-known projects (will be ignored if already exist from data)
INSERT OR IGNORE INTO projects (id, name, path, repo_url, description, active, created_at, updated_at) VALUES
    ('mx', 'MX CLI', '~/work/personal/code/mx', 'https://github.com/coryzibell/mx', 'Matrix CLI tool', 1, datetime('now'), datetime('now')),
    ('dotmatrix', 'dotmatrix', '~/.matrix', 'https://github.com/coryzibell/dotmatrix', 'Matrix configuration repository', 1, datetime('now'), datetime('now')),
    ('base-d', 'base-d', '~/work/personal/code/base-d', NULL, 'Base-d encoder/decoder', 1, datetime('now'), datetime('now'));

-- Create project junction tables
CREATE TABLE IF NOT EXISTS project_applicability (
    project_id TEXT NOT NULL,
    applicability_id TEXT NOT NULL,
    PRIMARY KEY (project_id, applicability_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (applicability_id) REFERENCES applicability_types(id)
);

CREATE TABLE IF NOT EXISTS project_tags (
    project_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (project_id, tag),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Seed well-known applicability types for seeding project links
INSERT OR IGNORE INTO applicability_types (id, description, scope, created_at) VALUES
    ('rust', 'Rust programming language', 'language', datetime('now')),
    ('cli', 'Command-line interface tools', 'domain', datetime('now')),
    ('cross-platform', 'Works on all platforms', 'platform', datetime('now')),
    ('encoding', 'Data encoding/decoding', 'domain', datetime('now')),
    ('compression', 'Data compression', 'domain', datetime('now'));

-- Seed project applicability for known projects
INSERT OR IGNORE INTO project_applicability (project_id, applicability_id) VALUES
    ('mx', 'rust'),
    ('mx', 'cli'),
    ('mx', 'cross-platform'),
    ('base-d', 'rust'),
    ('base-d', 'cli'),
    ('base-d', 'encoding'),
    ('base-d', 'compression');

-- Seed project tags for known projects
INSERT OR IGNORE INTO project_tags (project_id, tag) VALUES
    ('mx', 'tooling'),
    ('mx', 'matrix'),
    ('mx', 'knowledge-management'),
    ('dotmatrix', 'config'),
    ('dotmatrix', 'agents'),
    ('base-d', 'unicode'),
    ('base-d', 'hashing');

-- Step 3: Create new sessions table with FK
CREATE TABLE IF NOT EXISTS sessions_v3 (
    id TEXT PRIMARY KEY,
    session_type_id TEXT NOT NULL,
    project_id TEXT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    metadata TEXT,
    FOREIGN KEY (session_type_id) REFERENCES session_types(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Migrate existing sessions (if any)
INSERT INTO sessions_v3 (id, session_type_id, project_id, started_at, ended_at, metadata)
SELECT
    id,
    COALESCE(session_type, 'manual'),
    NULL,  -- No project link in v2
    started_at,
    ended_at,
    metadata
FROM sessions
WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='sessions');

-- Step 4: Create new knowledge table with all FKs
CREATE TABLE IF NOT EXISTS knowledge_v3 (
    id TEXT PRIMARY KEY,
    category_id TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT,
    summary TEXT,
    source_project_id TEXT,
    source_agent_id TEXT,
    file_path TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    source_type_id TEXT NOT NULL,
    entry_type_id TEXT NOT NULL,
    session_id TEXT,
    ephemeral INTEGER DEFAULT 0,

    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (source_project_id) REFERENCES projects(id),
    FOREIGN KEY (source_agent_id) REFERENCES agents(id),
    FOREIGN KEY (source_type_id) REFERENCES source_types(id),
    FOREIGN KEY (entry_type_id) REFERENCES entry_types(id),
    FOREIGN KEY (session_id) REFERENCES sessions_v3(id)
);

-- Step 5: Migrate knowledge data
INSERT INTO knowledge_v3 (
    id, category_id, title, body, summary,
    source_project_id, source_agent_id, file_path,
    created_at, updated_at, content_hash,
    source_type_id, entry_type_id, session_id, ephemeral
)
SELECT
    id,
    category,  -- Old TEXT becomes category_id FK
    title,
    body,
    summary,
    source_project,  -- Old TEXT becomes source_project_id FK
    source_agent,    -- Old TEXT becomes source_agent_id FK
    file_path,
    COALESCE(created_at, datetime('now')),
    COALESCE(updated_at, datetime('now')),
    COALESCE(content_hash, ''),
    COALESCE(source_type, 'manual'),
    COALESCE(entry_type, 'primary'),
    session_id,
    COALESCE(ephemeral, 0)
FROM knowledge;

-- Step 6: Create applicability junction table
CREATE TABLE IF NOT EXISTS knowledge_applicability (
    entry_id TEXT NOT NULL,
    applicability_id TEXT NOT NULL,
    PRIMARY KEY (entry_id, applicability_id),
    FOREIGN KEY (entry_id) REFERENCES knowledge_v3(id) ON DELETE CASCADE,
    FOREIGN KEY (applicability_id) REFERENCES applicability_types(id)
);

-- Migrate old applicability TEXT to junction table
-- Split on comma if multiple values exist
INSERT INTO knowledge_applicability (entry_id, applicability_id)
SELECT
    id,
    LOWER(REPLACE(applicability, ' ', '-'))
FROM knowledge
WHERE applicability IS NOT NULL AND applicability != '';

-- Step 7: Update relationships table with FK
CREATE TABLE IF NOT EXISTS relationships_v3 (
    from_id TEXT NOT NULL,
    to_id TEXT NOT NULL,
    rel_type_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (from_id, to_id, rel_type_id),
    FOREIGN KEY (from_id) REFERENCES knowledge_v3(id) ON DELETE CASCADE,
    FOREIGN KEY (to_id) REFERENCES knowledge_v3(id) ON DELETE CASCADE,
    FOREIGN KEY (rel_type_id) REFERENCES relationship_types(id)
);

-- Migrate existing relationships
INSERT INTO relationships_v3 (from_id, to_id, rel_type_id, created_at)
SELECT
    from_id,
    to_id,
    COALESCE(rel_type, 'related'),
    COALESCE(created_at, datetime('now'))
FROM relationships
WHERE EXISTS (SELECT 1 FROM sqlite_master WHERE type='table' AND name='relationships');

-- Step 8: Swap tables
DROP TABLE IF EXISTS knowledge;
ALTER TABLE knowledge_v3 RENAME TO knowledge;

DROP TABLE IF EXISTS sessions;
ALTER TABLE sessions_v3 RENAME TO sessions;

DROP TABLE IF EXISTS relationships;
ALTER TABLE relationships_v3 RENAME TO relationships;

-- Step 9: Recreate indexes
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge(category_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_source_project ON knowledge(source_project_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_source_agent ON knowledge(source_agent_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_source_type ON knowledge(source_type_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_entry_type ON knowledge(entry_type_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_session ON knowledge(session_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_updated ON knowledge(updated_at);

CREATE INDEX IF NOT EXISTS idx_applicability_entry ON knowledge_applicability(entry_id);
CREATE INDEX IF NOT EXISTS idx_applicability_type ON knowledge_applicability(applicability_id);

CREATE INDEX IF NOT EXISTS idx_project_applicability_project ON project_applicability(project_id);
CREATE INDEX IF NOT EXISTS idx_project_applicability_type ON project_applicability(applicability_id);
CREATE INDEX IF NOT EXISTS idx_project_tags_project ON project_tags(project_id);
CREATE INDEX IF NOT EXISTS idx_project_tags_tag ON project_tags(tag);

CREATE INDEX IF NOT EXISTS idx_sessions_type ON sessions(session_type_id);
CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions(project_id);

CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(rel_type_id);

CREATE INDEX IF NOT EXISTS idx_applicability_scope ON applicability_types(scope);
CREATE INDEX IF NOT EXISTS idx_projects_active ON projects(active);

-- Step 10: Update schema version
PRAGMA user_version = 3;

COMMIT;
```

---

## 4. Code Changes by File

### 4.1 `/home/w3surf/work/personal/code/mx/src/schema.sql`

**Action:** Replace entire file with new schema from section 2

**Impact:** Schema definition only - no runtime logic

---

### 4.2 `/home/w3surf/work/personal/code/mx/src/db.rs`

**Changes Required:**

1. **Update `SCHEMA_VERSION` constant:**
   - Change `const SCHEMA_VERSION: i32 = 2;` to `const SCHEMA_VERSION: i32 = 3;`

2. **Add new structs for ALL lookup tables:**
```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Category {
    pub id: String,
    pub description: String,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Project {
    pub id: String,
    pub name: String,
    pub path: Option<String>,
    pub repo_url: Option<String>,
    pub description: Option<String>,
    pub active: bool,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApplicabilityType {
    pub id: String,
    pub description: String,
    pub scope: Option<String>,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SourceType {
    pub id: String,
    pub description: String,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EntryType {
    pub id: String,
    pub description: String,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RelationshipType {
    pub id: String,
    pub description: String,
    pub directional: bool,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionType {
    pub id: String,
    pub description: String,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Session {
    pub id: String,
    pub session_type_id: String,
    pub project_id: Option<String>,
    pub started_at: String,
    pub ended_at: Option<String>,
    pub metadata: Option<String>,
}
```

3. **Update `init_schema` method:**
   - Add migration logic to detect v2->v3
   - Execute migration if `version == 2 && SCHEMA_VERSION == 3`
   - Load migration from `include_str!("migrations/v2_to_v3.sql")`

4. **Update `upsert_knowledge` method:**
   - Remove `tags` TEXT column from INSERT/UPDATE
   - Change `category` to `category_id`
   - Change `source_project` to `source_project_id`
   - Change `source_agent` to `source_agent_id`
   - Change `source_type` to `source_type_id`
   - Change `entry_type` to `entry_type_id`
   - Remove `applicability` TEXT field (now junction table)
   - After INSERT, populate `knowledge_applicability` junction table

5. **Update all query methods:**
   - `search`: Use FK column names, load applicability from junction
   - `list_by_category`: Validate category_id against categories table
   - `get`: Load applicability from junction table
   - All queries: Remove JSON deserialization for tags, query tags table

6. **Add new CRUD methods:**
```rust
// Categories
pub fn list_categories(&self) -> Result<Vec<Category>>;
pub fn get_category(&self, id: &str) -> Result<Option<Category>>;
pub fn upsert_category(&self, category: &Category) -> Result<()>;

// Projects
pub fn list_projects(&self, active_only: bool) -> Result<Vec<Project>>;
pub fn get_project(&self, id: &str) -> Result<Option<Project>>;
pub fn upsert_project(&self, project: &Project) -> Result<()>;

// Applicability Types
pub fn list_applicability_types(&self) -> Result<Vec<ApplicabilityType>>;
pub fn get_applicability_type(&self, id: &str) -> Result<Option<ApplicabilityType>>;
pub fn upsert_applicability_type(&self, atype: &ApplicabilityType) -> Result<()>;

// Source/Entry/Relationship/Session Types
pub fn list_source_types(&self) -> Result<Vec<SourceType>>;
pub fn list_entry_types(&self) -> Result<Vec<EntryType>>;
pub fn list_relationship_types(&self) -> Result<Vec<RelationshipType>>;
pub fn list_session_types(&self) -> Result<Vec<SessionType>>;

// Sessions
pub fn upsert_session(&self, session: &Session) -> Result<()>;
pub fn get_session(&self, id: &str) -> Result<Option<Session>>;
pub fn list_sessions(&self, project_id: Option<&str>) -> Result<Vec<Session>>;

// Applicability for knowledge entry
pub fn get_applicability_for_entry(&self, entry_id: &str) -> Result<Vec<String>>;
pub fn set_applicability_for_entry(&self, entry_id: &str, applicability_ids: &[String]) -> Result<()>;

// Tags for knowledge entry (already exists via junction)
pub fn get_tags_for_entry(&self, entry_id: &str) -> Result<Vec<String>>;

// Project applicability (many-to-many)
pub fn get_applicability_for_project(&self, project_id: &str) -> Result<Vec<String>>;
pub fn set_applicability_for_project(&self, project_id: &str, applicability_ids: &[String]) -> Result<()>;

// Project tags (many-to-many)
pub fn get_tags_for_project(&self, project_id: &str) -> Result<Vec<String>>;
pub fn set_tags_for_project(&self, project_id: &str, tags: &[String]) -> Result<()>;
```

7. **Update `make_entry` test helper:**
   - Use valid category_id values from seeded categories
   - Use valid project_id if source_project is set

**Estimated LOC Changes:** ~200 lines modified, ~150 lines added

---

### 4.3 `/home/w3surf/work/personal/code/mx/src/knowledge.rs`

**Changes Required:**

1. **Update `KnowledgeEntry` struct:**
```rust
pub struct KnowledgeEntry {
    pub id: String,
    pub category_id: String,                // Was: category
    pub title: String,
    pub body: Option<String>,
    pub summary: Option<String>,
    pub applicability: Vec<String>,         // Was: Option<String>, now Vec<applicability_type_ids>
    pub source_project_id: Option<String>,  // Was: source_project
    pub source_agent_id: Option<String>,    // Was: source_agent
    pub file_path: Option<String>,
    pub tags: Vec<String>,
    pub created_at: Option<String>,
    pub updated_at: Option<String>,
    pub content_hash: Option<String>,
    pub source_type_id: Option<String>,     // Was: source_type
    pub entry_type_id: Option<String>,      // Was: entry_type
    pub session_id: Option<String>,
    pub ephemeral: bool,
}
```

2. **Update `Frontmatter` struct:**
```rust
pub struct Frontmatter {
    pub title: Option<String>,
    pub category: Option<String>,           // Still accepts TEXT in frontmatter
    pub tags: Vec<String>,
    pub applicability: Vec<String>,         // Now accepts array in frontmatter
    pub source_project: Option<String>,     // Still accepts TEXT in frontmatter
    pub source_agent: Option<String>,       // Still accepts TEXT in frontmatter
    pub created: Option<String>,
}
```

3. **Update `from_markdown` method:**
   - Parse `applicability` as array in frontmatter (YAML list)
   - Convert `category` frontmatter TEXT to `category_id`
   - Convert `source_project` frontmatter TEXT to `source_project_id`
   - Convert `source_agent` frontmatter TEXT to `source_agent_id`
   - Validate against lookup tables (or queue for creation)
   - Set `source_type_id = "manual"` and `entry_type_id = "primary"`

4. **Add validation helpers:**
```rust
fn validate_category_id(db: &Database, category: &str) -> Result<String>;
fn validate_project_id(db: &Database, project: &str) -> Result<String>;
fn parse_applicability_list(input: &str) -> Vec<String>;
```

**Estimated LOC Changes:** ~40 lines modified, ~30 lines added

---

### 4.4 `/home/w3surf/work/personal/code/mx/src/main.rs`

**Changes Required:**

1. **Update `ZionCommands::Add` struct:**
```rust
Add {
    /// Category (pattern, technique, insight, etc.)
    #[arg(short, long)]
    category: Option<String>,

    /// Title of the knowledge entry
    #[arg(short, long)]
    title: String,

    /// Content from stdin or --file
    #[arg(short, long)]
    content: Option<String>,

    /// Read content from file
    #[arg(short, long)]
    file: Option<PathBuf>,

    /// Tags (comma-separated)
    #[arg(short = 'g', long)]
    tags: Option<String>,

    /// Applicability contexts (comma-separated)
    #[arg(short = 'a', long)]
    applicability: Option<String>,

    /// Source project ID
    #[arg(short = 'p', long)]
    project: Option<String>,

    /// Source agent ID
    #[arg(long)]
    source_agent: Option<String>,

    /// Source type (manual, ram, cache, agent_session)
    #[arg(long, default_value = "manual")]
    source_type: String,

    /// Entry type (primary, summary, synthesis)
    #[arg(long, default_value = "primary")]
    entry_type: String,

    /// Session ID
    #[arg(long)]
    session_id: Option<String>,

    /// Mark as ephemeral
    #[arg(long)]
    ephemeral: bool,
}
```

2. **Update `handle_zion` Add branch:**
   - Validate `category` against `db.list_categories()`
   - Validate `source_type` against `db.list_source_types()`
   - Validate `entry_type` against `db.list_entry_types()`
   - Validate `source_agent` against `db.list_agents()` (if provided)
   - Validate `project` against `db.list_projects()` (if provided)
   - Parse `applicability` CSV into Vec<String>
   - Validate each applicability against `db.list_applicability_types()`
   - Auto-create unknown applicability types with user confirmation
   - Wire all validated IDs to struct fields
   - Call `db.set_applicability_for_entry()` after upsert

3. **Add new commands:**
```rust
ZionCommands::Projects { subcommand } => {
    match subcommand {
        ProjectsSubcommand::List => { /* List all projects */ },
        ProjectsSubcommand::Add { id, name, path, repo_url, description } => {
            /* Add new project */
        },
        ProjectsSubcommand::Update { id, ... } => { /* Update project */ },
    }
}

ZionCommands::Applicability { subcommand } => {
    match subcommand {
        ApplicabilitySubcommand::List => { /* List all types */ },
        ApplicabilitySubcommand::Add { id, description, scope } => {
            /* Add new type */
        },
    }
}

ZionCommands::Sessions { subcommand } => {
    match subcommand {
        SessionsSubcommand::Create { type_id, project_id } => {
            /* Create session */
        },
        SessionsSubcommand::Close { id } => { /* Close session */ },
        SessionsSubcommand::List { project_id } => { /* List sessions */ },
    }
}
```

4. **Update category queries:**
   - Replace hardcoded category arrays with `db.list_categories()`
   - Update Stats command to query dynamically
   - Update List command to validate category filter

**Estimated LOC Changes:** ~120 lines modified, ~150 lines added

---

### 4.5 `/home/w3surf/work/personal/code/mx/src/index.rs`

**Changes Required:**

1. **Update `export_markdown` function:**
   - Query categories dynamically: `db.list_categories()?`
   - Export `category_id` instead of `category`
   - Export `source_project_id` instead of `source_project`
   - Export `source_agent_id` instead of `source_agent`
   - Export `applicability` as YAML array from junction table
   - Load applicability via `db.get_applicability_for_entry(entry.id)`

2. **Update `export_jsonl` function:**
   - Same dynamic category query
   - Serialize applicability as array

3. **Update `export_csv` function:**
   - Same dynamic category query
   - Change header: `category_id,source_project_id`
   - Serialize applicability as comma-separated string

4. **Update `import_jsonl` function:**
   - Accept new field names
   - Parse applicability array
   - Call `db.set_applicability_for_entry()` after insert

**Estimated LOC Changes:** ~30 lines modified, ~20 lines added

---

### 4.6 `/home/w3surf/.matrix/agents/zion-control.md`

**Content Additions:**

```markdown
## Database Schema (v3) - Fully Normalized

### Lookup Tables

All categorical fields now use normalized lookup tables:

- **`categories`** - pattern, technique, insight, ritual, artifact, chronicle, project, future
- **`projects`** - Known projects with metadata (mx, dotmatrix, base-d, etc.)
- **`applicability_types`** - Contexts where knowledge applies (rust, python, cross-platform, etc.)
- **`source_types`** - How knowledge entered system (manual, ram, cache, agent_session)
- **`entry_types`** - Type of entry (primary, summary, synthesis)
- **`relationship_types`** - Relationship kinds (related, supersedes, extends, implements)
- **`session_types`** - Session kinds (claude_desktop, agent_task, manual, batch_import)
- **`agents`** - Agent registry (neo, smith, trinity, oracle, etc.)

### Junction Tables

Many-to-many relationships:

- **`tags`** - Knowledge ↔ Tags
- **`knowledge_applicability`** - Knowledge ↔ Applicability Types
- **`relationships`** - Knowledge ↔ Knowledge (typed)

### Key Schema Changes from v2

| v2 Field | v3 Field | Change |
|----------|----------|--------|
| `category` (TEXT) | `category_id` (FK) | Now validates against categories table |
| `source_project` (TEXT) | `source_project_id` (FK) | Now references projects table |
| `source_agent` (TEXT) | `source_agent_id` (FK) | Now validates against agents table |
| `applicability` (TEXT) | `knowledge_applicability` (junction) | Many-to-many relationship |
| `rel_type` (TEXT in relationships) | `rel_type_id` (FK) | Now validates against relationship_types |
| `session_type` (TEXT in sessions) | `session_type_id` (FK) | Now validates against session_types |

## CLI Usage Examples

### Adding Knowledge with Full Provenance

```bash
mx zion add \
  --category pattern \
  --title "Unicode Normalization in Rust" \
  --content "Always normalize to NFC before comparison..." \
  --tags "unicode,rust,text" \
  --applicability "rust,text-processing,search" \
  --project mx \
  --source-agent smith \
  --source-type agent_session \
  --entry-type synthesis \
  --session-id "sess-2025-11-29-001"
```

### Managing Projects

```bash
# List all projects
mx zion projects list

# Add new project
mx zion projects add \
  --id myproject \
  --name "My Project" \
  --path ~/work/personal/code/myproject \
  --repo-url https://github.com/user/myproject \
  --description "Description here"

# Update project
mx zion projects update --id mx --description "Updated description"
```

### Managing Applicability Types

```bash
# List all applicability types
mx zion applicability list

# Add new applicability type
mx zion applicability add \
  --id async-rust \
  --description "Async Rust programming" \
  --scope language
```

### Session Management

```bash
# Create session
mx zion sessions create \
  --type agent_task \
  --project mx

# Close session
mx zion sessions close --id sess-2025-11-29-001

# List sessions for project
mx zion sessions list --project mx
```

### Querying by Relationships

```bash
# List all knowledge from a project
mx zion list --project mx

# List all knowledge for an applicability context
mx zion list --applicability rust

# List all synthesis entries
mx zion list --entry-type synthesis
```

## Migration Notes

- **Applicability migration:** Old TEXT field split on commas, normalized to applicability types
- **Project migration:** Existing source_project values become project IDs
- **Unknown values:** CLI prompts to create new lookup entries for unknown values
- **JSONL export:** Field names change - re-export before upgrading if you need old format

## Agent Responsibilities

When capturing knowledge:

1. **Always specify `source_agent_id`** - Your agent ID
2. **Choose appropriate `source_type_id`**:
   - `manual` - User-entered
   - `ram` - From your RAM directory
   - `agent_session` - During task execution
   - `cache` - From workflow cache
3. **Set `entry_type_id`**:
   - `primary` - Original material
   - `summary` - Condensed version
   - `synthesis` - Combined insights
4. **Use `applicability`** - List all contexts (rust, linux, async, etc.)
5. **Link `project_id`** - Which project this knowledge belongs to
6. **Provide `session_id`** - If from agent session
```

**Estimated LOC Changes:** ~120 lines added

---

## 5. Migration Execution Plan

### 5.1 Pre-Migration Checks

1. **Backup database:**
   ```bash
   cp ~/.matrix/zion/knowledge.db ~/.matrix/zion/knowledge.db.v2.backup
   ```

2. **Export data:**
   ```bash
   mx zion export --format jsonl --output ~/.matrix/zion/pre-migration.jsonl
   ```

3. **Check current data:**
   ```bash
   sqlite3 ~/.matrix/zion/knowledge.db "SELECT COUNT(*) FROM knowledge"
   sqlite3 ~/.matrix/zion/knowledge.db "SELECT DISTINCT category FROM knowledge"
   sqlite3 ~/.matrix/zion/knowledge.db "SELECT DISTINCT source_project FROM knowledge WHERE source_project IS NOT NULL"
   ```

### 5.2 Migration Execution

Migration runs automatically via `Database::open()` when v2 schema detected.

**Implementation in `db.rs::init_schema`:**

```rust
fn init_schema(&self) -> Result<()> {
    let version: i32 = self.conn.query_row(
        "PRAGMA user_version",
        [],
        |row| row.get(0),
    ).unwrap_or(0);

    match version {
        0..=1 => {
            // Apply full v3 schema
            self.conn.execute_batch(include_str!("schema.sql"))?;
            self.conn.execute("PRAGMA user_version = 3", [])?;
        }
        2 => {
            // Run migration from v2 to v3
            eprintln!("Migrating Zion schema from v2 to v3...");
            self.conn.execute_batch(include_str!("migrations/v2_to_v3.sql"))?;
            eprintln!("Migration complete. Schema now at v3.");
        }
        3 => {
            // Already current
        }
        _ => {
            anyhow::bail!("Unknown schema version: {}", version);
        }
    }

    Ok(())
}
```

### 5.3 Post-Migration Validation

1. **Check schema version:**
   ```bash
   sqlite3 ~/.matrix/zion/knowledge.db "PRAGMA user_version"
   # Should output: 3
   ```

2. **Verify table structure:**
   ```bash
   sqlite3 ~/.matrix/zion/knowledge.db ".schema knowledge"
   sqlite3 ~/.matrix/zion/knowledge.db ".schema projects"
   sqlite3 ~/.matrix/zion/knowledge.db ".schema knowledge_applicability"
   ```

3. **Check data integrity:**
   ```bash
   mx zion stats
   # Should show same entry counts as pre-migration
   ```

4. **Test queries:**
   ```bash
   mx zion list --category pattern
   mx zion projects list
   mx zion search "rust"
   ```

5. **Verify FK constraints:**
   ```bash
   sqlite3 ~/.matrix/zion/knowledge.db "PRAGMA foreign_key_check"
   # Should return empty (no violations)
   ```

### 5.4 Rollback Procedure

If migration fails:

```bash
# Restore backup
mv ~/.matrix/zion/knowledge.db ~/.matrix/zion/knowledge.db.v3.failed
cp ~/.matrix/zion/knowledge.db.v2.backup ~/.matrix/zion/knowledge.db

# Revert code to v2
git checkout HEAD~1
cargo build --release
```

---

## 6. Component Interaction Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│ Markdown Files (~/.matrix/zion/)                                 │
│  - patterns/*.md                                                 │
│  - techniques/*.md                                               │
└────────────┬─────────────────────────────────────────────────────┘
             │
             │ mx zion rebuild
             ▼
┌──────────────────────────────────────────────────────────────────┐
│ KnowledgeEntry::from_markdown()                                  │
│  - Parse frontmatter (category, tags, applicability[])          │
│  - Validate category → categories.id                            │
│  - Validate project → projects.id (or create)                   │
│  - Parse applicability array → applicability_types.id           │
└────────────┬─────────────────────────────────────────────────────┘
             │
             │ Validated entry + applicability list
             ▼
┌──────────────────────────────────────────────────────────────────┐
│ Database::upsert_knowledge()                                     │
│  - INSERT with ALL FK validation:                               │
│    → categories(id)                                             │
│    → projects(id) [nullable]                                    │
│    → agents(id) [nullable]                                      │
│    → source_types(id)                                           │
│    → entry_types(id)                                            │
│    → sessions(id) [nullable]                                    │
│  - UPDATE tags junction table                                   │
│  - UPDATE knowledge_applicability junction table                │
└────────────┬─────────────────────────────────────────────────────┘
             │
             │ Committed transaction
             ▼
┌──────────────────────────────────────────────────────────────────┐
│ SQLite Database (~/.matrix/zion/knowledge.db)                    │
│  - knowledge (all FKs, no TEXT enums)                           │
│  - categories, projects, applicability_types (lookups)          │
│  - tags, knowledge_applicability (junctions)                    │
│  - agents, sessions, source_types, entry_types (lookups)        │
│  - relationships (with rel_type_id FK)                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 7. FK Constraint Enforcement Rules

### Required FKs (NOT NULL)

| Field | References | Default | Validation |
|-------|-----------|---------|------------|
| `category_id` | categories.id | 'insight' | Must exist in categories table |
| `source_type_id` | source_types.id | 'manual' | Must exist in source_types table |
| `entry_type_id` | entry_types.id | 'primary' | Must exist in entry_types table |

### Optional FKs (NULL allowed)

| Field | References | When NULL | Validation |
|-------|-----------|-----------|------------|
| `source_project_id` | projects.id | Knowledge not project-specific | If set, must exist in projects |
| `source_agent_id` | agents.id | Manual entry, no agent | If set, must exist in agents |
| `session_id` | sessions.id | Not from session | If set, must exist in sessions |

### Junction Table FKs

| Table | FK Constraints |
|-------|----------------|
| `tags` | entry_id → knowledge.id (CASCADE DELETE) |
| `knowledge_applicability` | entry_id → knowledge.id (CASCADE DELETE), applicability_id → applicability_types.id |
| `relationships` | from_id → knowledge.id (CASCADE DELETE), to_id → knowledge.id (CASCADE DELETE), rel_type_id → relationship_types.id |

### Auto-Creation Policy

**Never auto-create:**
- Categories (fixed set)
- Source types (fixed set)
- Entry types (fixed set)
- Relationship types (fixed set)
- Session types (fixed set)

**Prompt to create:**
- Projects (user should confirm new project)
- Applicability types (could be dynamic, confirm first)

**Auto-create silently:**
- Sessions (when specified by agent)
- Agents (when new agent identity appears)

---

## 8. Testing Strategy

### 8.1 Unit Tests

**File:** `src/db.rs`

```rust
#[test]
fn test_category_fk_validation() {
    let db = Database::open_in_memory().unwrap();
    let mut entry = make_entry("kn-test", "invalid_category", "Test");

    // Invalid category should fail
    assert!(db.upsert_knowledge(&entry).is_err());

    entry.category_id = "pattern".to_string();
    assert!(db.upsert_knowledge(&entry).is_ok());
}

#[test]
fn test_project_fk_validation() {
    let db = Database::open_in_memory().unwrap();
    let mut entry = make_entry("kn-test", "pattern", "Test");

    // Invalid project should fail
    entry.source_project_id = Some("nonexistent".to_string());
    assert!(db.upsert_knowledge(&entry).is_err());

    // Create project
    let project = Project {
        id: "testproj".to_string(),
        name: "Test Project".to_string(),
        path: None,
        repo_url: None,
        description: None,
        active: true,
        created_at: chrono::Utc::now().to_rfc3339(),
        updated_at: chrono::Utc::now().to_rfc3339(),
    };
    db.upsert_project(&project).unwrap();

    entry.source_project_id = Some("testproj".to_string());
    assert!(db.upsert_knowledge(&entry).is_ok());
}

#[test]
fn test_applicability_junction() {
    let db = Database::open_in_memory().unwrap();
    let entry = make_entry("kn-test", "pattern", "Test");

    // Insert knowledge
    db.upsert_knowledge(&entry).unwrap();

    // Add applicability types
    db.upsert_applicability_type(&ApplicabilityType {
        id: "rust".to_string(),
        description: "Rust programming".to_string(),
        scope: Some("language".to_string()),
        created_at: chrono::Utc::now().to_rfc3339(),
    }).unwrap();

    db.upsert_applicability_type(&ApplicabilityType {
        id: "async".to_string(),
        description: "Async programming".to_string(),
        scope: Some("paradigm".to_string()),
        created_at: chrono::Utc::now().to_rfc3339(),
    }).unwrap();

    // Set applicability
    db.set_applicability_for_entry("kn-test", &["rust".to_string(), "async".to_string()]).unwrap();

    // Verify
    let applicability = db.get_applicability_for_entry("kn-test").unwrap();
    assert_eq!(applicability.len(), 2);
    assert!(applicability.contains(&"rust".to_string()));
    assert!(applicability.contains(&"async".to_string()));
}

#[test]
fn test_migration_v2_to_v3() {
    // Create v2 schema
    let conn = Connection::open_in_memory().unwrap();
    conn.execute_batch(include_str!("test_data/schema_v2.sql")).unwrap();
    conn.execute("PRAGMA user_version = 2", []).unwrap();

    // Insert v2 data with old field names
    conn.execute(
        "INSERT INTO knowledge (id, category, title, body, applicability, source_project, created_at, updated_at, content_hash)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9)",
        params!["kn-test", "pattern", "Test", "Body", "rust, async", "mx", "2025-01-01T00:00:00Z", "2025-01-01T00:00:00Z", "hash123"]
    ).unwrap();

    // Run migration
    let db = Database { conn };
    db.init_schema().unwrap();

    // Verify schema version
    let version: i32 = db.conn.query_row("PRAGMA user_version", [], |r| r.get(0)).unwrap();
    assert_eq!(version, 3);

    // Verify data migrated
    let entry = db.get("kn-test").unwrap().unwrap();
    assert_eq!(entry.category_id, "pattern");
    assert_eq!(entry.source_project_id, Some("mx".to_string()));

    // Verify applicability junction table
    let applicability = db.get_applicability_for_entry("kn-test").unwrap();
    assert!(applicability.len() >= 1);  // At least "rust-async" or split into "rust", "async"
}
```

### 8.2 Integration Tests

```rust
#[test]
fn test_full_provenance_workflow() {
    let temp_db = tempfile::NamedTempFile::new().unwrap();
    let db = Database::open(temp_db.path()).unwrap();

    // Create project
    let project = Project {
        id: "mx".to_string(),
        name: "MX CLI".to_string(),
        path: Some("~/work/personal/code/mx".to_string()),
        repo_url: Some("https://github.com/user/mx".to_string()),
        description: Some("Matrix CLI".to_string()),
        active: true,
        created_at: chrono::Utc::now().to_rfc3339(),
        updated_at: chrono::Utc::now().to_rfc3339(),
    };
    db.upsert_project(&project).unwrap();

    // Create applicability types
    db.upsert_applicability_type(&ApplicabilityType {
        id: "rust".to_string(),
        description: "Rust programming".to_string(),
        scope: Some("language".to_string()),
        created_at: chrono::Utc::now().to_rfc3339(),
    }).unwrap();

    // Create knowledge entry
    let entry = KnowledgeEntry {
        id: "kn-test".to_string(),
        category_id: "pattern".to_string(),
        title: "Test Pattern".to_string(),
        body: Some("Test body".to_string()),
        summary: None,
        applicability: vec!["rust".to_string()],
        source_project_id: Some("mx".to_string()),
        source_agent_id: None,
        file_path: None,
        tags: vec!["test".to_string()],
        created_at: Some(chrono::Utc::now().to_rfc3339()),
        updated_at: Some(chrono::Utc::now().to_rfc3339()),
        content_hash: Some("hash".to_string()),
        source_type_id: Some("manual".to_string()),
        entry_type_id: Some("primary".to_string()),
        session_id: None,
        ephemeral: false,
    };

    db.upsert_knowledge(&entry).unwrap();
    db.set_applicability_for_entry(&entry.id, &entry.applicability).unwrap();

    // Verify
    let fetched = db.get("kn-test").unwrap().unwrap();
    assert_eq!(fetched.source_project_id, Some("mx".to_string()));

    let applicability = db.get_applicability_for_entry("kn-test").unwrap();
    assert_eq!(applicability, vec!["rust".to_string()]);
}
```

### 8.3 Manual Testing Checklist

- [ ] Rebuild index from markdown files
- [ ] Search returns correct results
- [ ] List by category works
- [ ] Add entry with project validation
- [ ] Add entry with applicability array
- [ ] Invalid category fails gracefully
- [ ] Invalid project fails gracefully
- [ ] Projects list/add/update commands work
- [ ] Applicability list/add commands work
- [ ] Export to markdown preserves all fields
- [ ] Export to JSONL has correct field names
- [ ] Migration preserves all entries
- [ ] FK constraints prevent orphaned data

---

## 9. Implementation Checklist

### Phase 1: Schema & Migration
- [ ] Create `src/migrations/v2_to_v3.sql` (from section 3.1)
- [ ] Update `src/schema.sql` (from section 2)
- [ ] Test migration SQL on backup database
- [ ] Verify FK constraints work

### Phase 2: Database Layer
- [ ] Update `SCHEMA_VERSION` to 3
- [ ] Add all new structs (Project, ApplicabilityType, etc.)
- [ ] Update `upsert_knowledge` for FK column names
- [ ] Remove applicability TEXT field, add junction table handling
- [ ] Add CRUD methods for all lookup tables
- [ ] Add `get_applicability_for_entry` / `set_applicability_for_entry`
- [ ] Update all query methods
- [ ] Write unit tests for FK validation
- [ ] Write migration test

### Phase 3: Domain Layer
- [ ] Update `KnowledgeEntry` struct field names
- [ ] Update `Frontmatter` struct
- [ ] Update `from_markdown` for validation
- [ ] Add validation helpers for category/project
- [ ] Parse applicability as array

### Phase 4: CLI Layer
- [ ] Add new flags to `ZionCommands::Add`
- [ ] Add `ZionCommands::Projects`
- [ ] Add `ZionCommands::Applicability`
- [ ] Add `ZionCommands::Sessions`
- [ ] Update `handle_zion` Add branch
- [ ] Add validation for all FK fields
- [ ] Replace hardcoded arrays with DB queries

### Phase 5: Export/Import
- [ ] Update `export_markdown` for FK field names
- [ ] Update `export_jsonl` for FK field names
- [ ] Update `export_csv` for FK field names
- [ ] Update `import_jsonl` for new field names
- [ ] Test JSONL round-trip

### Phase 6: Documentation
- [ ] Update Zion Control agent markdown
- [ ] Add migration notes
- [ ] Document new CLI commands
- [ ] Add examples for projects/applicability management

### Phase 7: Testing & Deployment
- [ ] Run full test suite
- [ ] Manual test on dev database
- [ ] Backup production database
- [ ] Run migration on production
- [ ] Validate data integrity
- [ ] Monitor for FK violations

---

## 10. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Data loss during migration | Low | Critical | Pre-migration backup, transaction safety, JSONL export |
| FK constraint violations | Medium | High | Seed lookup tables from existing data, validate before FK creation |
| Orphaned applicability data | Low | Medium | CASCADE DELETE on junction tables |
| Invalid project references | Medium | Low | Auto-create projects table from existing source_project values |
| Performance degradation | Low | Low | Indexes on ALL FK columns |
| Breaking existing scripts | Low | Medium | CLI unchanged, only internal field names change |
| Complex many-to-many queries | Medium | Low | Provide helper methods for common queries |

---

## 11. Success Criteria

Migration succeeds when:

1. ✅ All knowledge entries preserved (count matches)
2. ✅ Tags migrated to junction table
3. ✅ Applicability migrated to junction table
4. ✅ Projects table populated from existing data
5. ✅ All FK constraints enforced
6. ✅ Invalid inserts fail gracefully
7. ✅ CLI commands work identically
8. ✅ Export/import maintains integrity
9. ✅ Query performance equivalent or better
10. ✅ Zero data loss
11. ✅ No FK violations in existing data

---

## Appendix A: Lookup Table Seed Values

### Categories
- `pattern` - Recurring structural solutions
- `technique` - Specific procedural approaches
- `insight` - Key realizations
- `ritual` - Habitual practices
- `artifact` - Tools, scripts, templates
- `chronicle` - Historical records
- `project` - Project-specific knowledge
- `future` - Ideas and plans

### Source Types
- `manual` - Manually entered
- `ram` - Absorbed from agent RAM
- `cache` - Absorbed from workflow cache
- `agent_session` - Captured during execution

### Entry Types
- `primary` - Original source material
- `summary` - Condensed summary
- `synthesis` - Combined insights

### Relationship Types
- `related` - General association (non-directional)
- `supersedes` - Replaces/deprecates (directional)
- `extends` - Builds upon (directional)
- `implements` - Concrete realization (directional)
- `contradicts` - Conflicts with (non-directional)

### Session Types
- `claude_desktop` - Claude Desktop session
- `agent_task` - Agent task execution
- `manual` - Manual entry session
- `batch_import` - Bulk import operation

### Known Projects (Seed)
- `mx` - MX CLI (~/.matrix tooling)
- `dotmatrix` - Matrix configuration repo
- `base-d` - Base-d project

### Example Applicability Types (Seed)
- `rust` - Rust programming (scope: language)
- `python` - Python programming (scope: language)
- `cross-platform` - Works everywhere (scope: platform)
- `linux-only` - Linux-specific (scope: platform)
- `async` - Async programming (scope: paradigm)
- `cli` - Command-line tools (scope: domain)

---

## Appendix B: File Locations

| File | Path | Purpose |
|------|------|---------|
| Schema definition | `/home/w3surf/work/personal/code/mx/src/schema.sql` | Complete v3 schema |
| Migration SQL | `/home/w3surf/work/personal/code/mx/src/migrations/v2_to_v3.sql` | v2→v3 migration |
| Database module | `/home/w3surf/work/personal/code/mx/src/db.rs` | Database operations |
| Knowledge module | `/home/w3surf/work/personal/code/mx/src/knowledge.rs` | Entry structs |
| CLI module | `/home/w3surf/work/personal/code/mx/src/main.rs` | CLI interface |
| Index module | `/home/w3surf/work/personal/code/mx/src/index.rs` | Export functions |
| Agent docs | `/home/w3surf/.matrix/agents/zion-control.md` | Agent instructions |
| Production DB | `/home/w3surf/.matrix/zion/knowledge.db` | SQLite database |

---

**End of Revised Architectural Design Document**
