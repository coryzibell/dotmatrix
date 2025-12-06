-- =============================================================================
-- Zion Knowledge Base - SurrealQL Query Examples
-- Reference for Smith during implementation
-- =============================================================================

-- =============================================================================
-- BASIC CRUD
-- =============================================================================

-- Create a knowledge entry
CREATE knowledge:kn_abc123 SET
    title = 'SIMD UTF-8 Validation',
    body = 'Use _mm_cmpestri for fast UTF-8 validation...',
    summary = 'SIMD approach to UTF-8 validation',
    content_hash = 'a1b2c3d4',
    category = category:technique,
    source_type = source_type:manual,
    entry_type = entry_type:primary,
    content_type = content_type:code,
    source_project = project:base_d;

-- Update a knowledge entry
UPDATE knowledge:kn_abc123 SET
    title = 'SIMD UTF-8 Validation (Updated)',
    updated_at = time::now();

-- Get a knowledge entry with related data
SELECT *,
    category.description AS category_name,
    source_project.name AS project_name,
    ->tagged_with->tag.name AS tags,
    ->applies_to->applicability_type AS applicability
FROM knowledge:kn_abc123;

-- Delete a knowledge entry (edges cascade automatically)
DELETE knowledge:kn_abc123;

-- =============================================================================
-- SEARCH
-- =============================================================================

-- Full-text search across all fields
SELECT * FROM knowledge
WHERE title @@ 'SIMD'
   OR body @@ 'SIMD'
   OR summary @@ 'SIMD'
ORDER BY updated_at DESC;

-- Search with scoring (BM25)
SELECT *,
    search::score(1) AS title_score,
    search::score(2) AS body_score
FROM knowledge
WHERE title @1@ 'validation' OR body @2@ 'validation'
ORDER BY (search::score(1) * 2 + search::score(2)) DESC
LIMIT 20;

-- Search within a category
SELECT * FROM knowledge
WHERE category = category:pattern
  AND (title @@ 'async' OR body @@ 'async');

-- =============================================================================
-- TAGGING
-- =============================================================================

-- Add tags to an entry
CREATE tag:simd SET name = 'simd' ON DUPLICATE KEY UPDATE name = name;
CREATE tag:performance SET name = 'performance' ON DUPLICATE KEY UPDATE name = name;
RELATE knowledge:kn_abc123->tagged_with->tag:simd;
RELATE knowledge:kn_abc123->tagged_with->tag:performance;

-- Get all tags for an entry
SELECT ->tagged_with->tag.name AS tags FROM knowledge:kn_abc123;

-- Find entries by tag
SELECT <-tagged_with<-knowledge AS entries FROM tag:rust;

-- Find entries with multiple tags (AND)
SELECT * FROM knowledge
WHERE ->tagged_with->tag CONTAINS tag:rust
  AND ->tagged_with->tag CONTAINS tag:async;

-- Find entries with any of tags (OR)
SELECT * FROM knowledge
WHERE ->tagged_with->tag CONTAINSANY [tag:rust, tag:python];

-- Remove a tag from entry
DELETE knowledge:kn_abc123->tagged_with WHERE out = tag:simd;

-- Replace all tags for an entry
DELETE knowledge:kn_abc123->tagged_with;
FOR $tag IN ['rust', 'async', 'performance'] {
    LET $tag_id = type::thing('tag', $tag);
    CREATE $tag_id SET name = $tag ON DUPLICATE KEY UPDATE name = name;
    RELATE knowledge:kn_abc123->tagged_with->$tag_id;
};

-- =============================================================================
-- APPLICABILITY
-- =============================================================================

-- Add applicability
RELATE knowledge:kn_abc123->applies_to->applicability_type:rust;
RELATE knowledge:kn_abc123->applies_to->applicability_type:cross_platform;

-- Get applicability for entry
SELECT ->applies_to->applicability_type AS applicability FROM knowledge:kn_abc123;

-- Find entries applicable to Rust
SELECT <-applies_to<-knowledge AS entries FROM applicability_type:rust;

-- =============================================================================
-- RELATIONSHIPS (GRAPH)
-- =============================================================================

-- Create a relationship between entries
RELATE knowledge:kn_abc123->relates_to->knowledge:kn_def456 SET
    relationship_type = relationship_type:extends,
    created_at = time::now();

-- Find all related entries (outgoing)
SELECT ->relates_to->knowledge AS extends FROM knowledge:kn_abc123
WHERE ->relates_to.relationship_type = relationship_type:extends;

-- Find all related entries (incoming - what extends this?)
SELECT <-relates_to<-knowledge AS extended_by FROM knowledge:kn_def456
WHERE <-relates_to.relationship_type = relationship_type:extends;

-- Find all related entries (both directions, for non-directional relationships)
SELECT
    ->relates_to->knowledge AS outgoing,
    <-relates_to<-knowledge AS incoming
FROM knowledge:kn_abc123;

-- Get relationship with type info
SELECT
    in AS from,
    out AS to,
    relationship_type,
    relationship_type.description AS type_name
FROM relates_to
WHERE in = knowledge:kn_abc123 OR out = knowledge:kn_abc123;

-- Delete a specific relationship
DELETE relates_to WHERE in = knowledge:kn_abc123
    AND out = knowledge:kn_def456
    AND relationship_type = relationship_type:extends;

-- =============================================================================
-- GRAPH TRAVERSAL
-- =============================================================================

-- Find entries 2 hops away (entry -> extends -> extends)
SELECT ->relates_to->knowledge->relates_to->knowledge AS two_hops
FROM knowledge:kn_abc123;

-- Find all entries in the relationship graph (recursive)
-- Note: Be careful with unbounded recursion
SELECT ->relates_to->knowledge.* AS related
FROM knowledge:kn_abc123
FETCH related;

-- Find path between two entries
-- (SurrealDB doesn't have native shortest path yet, but can do BFS)

-- =============================================================================
-- LISTING & FILTERING
-- =============================================================================

-- List all entries by category
SELECT * FROM knowledge
WHERE category = category:pattern
ORDER BY title ASC;

-- List with pagination
SELECT * FROM knowledge
ORDER BY updated_at DESC
LIMIT 20 START 40;  -- Page 3 (0-indexed)

-- List non-ephemeral entries only
SELECT * FROM knowledge
WHERE ephemeral = false
ORDER BY updated_at DESC;

-- Count by category
SELECT category, count() AS count
FROM knowledge
GROUP BY category;

-- =============================================================================
-- PROJECTS
-- =============================================================================

-- List active projects
SELECT * FROM project WHERE active = true ORDER BY name;

-- Get project with its tags and applicability
SELECT *,
    ->project_tagged_with->tag.name AS tags,
    ->project_applies_to->applicability_type AS applicability
FROM project:mx;

-- Find knowledge for a project
SELECT * FROM knowledge
WHERE source_project = project:mx
ORDER BY updated_at DESC;

-- =============================================================================
-- SESSIONS
-- =============================================================================

-- Create a session
CREATE session:sess_xyz SET
    session_type = session_type:claude_code,
    project = project:mx,
    started_at = time::now(),
    metadata = { conversation_id: 'abc123', mode: 'interactive' };

-- End a session
UPDATE session:sess_xyz SET ended_at = time::now();

-- List recent sessions
SELECT * FROM session ORDER BY started_at DESC LIMIT 10;

-- Find knowledge from a session
SELECT * FROM knowledge WHERE session = session:sess_xyz;

-- =============================================================================
-- AGENTS
-- =============================================================================

-- Register an agent
CREATE agent:smith SET
    description = 'Code implementation specialist',
    domain = 'implementation';

-- Find knowledge by agent
SELECT * FROM knowledge
WHERE source_agent = agent:smith
ORDER BY created_at DESC;

-- Count contributions by agent
SELECT source_agent, count() AS contributions
FROM knowledge
WHERE source_agent IS NOT NONE
GROUP BY source_agent;

-- =============================================================================
-- ANALYTICS QUERIES
-- =============================================================================

-- Knowledge growth over time (by month)
SELECT
    time::group(created_at, 'month') AS month,
    count() AS entries
FROM knowledge
GROUP BY month
ORDER BY month DESC;

-- Most connected entries (hub detection)
SELECT
    id,
    title,
    count(->relates_to) + count(<-relates_to) AS connections
FROM knowledge
ORDER BY connections DESC
LIMIT 10;

-- Tag frequency
SELECT
    out.name AS tag,
    count() AS usage
FROM tagged_with
GROUP BY tag
ORDER BY usage DESC
LIMIT 20;

-- Orphaned tags (no entries using them)
SELECT * FROM tag
WHERE count(<-tagged_with) = 0;
