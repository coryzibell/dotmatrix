# Idea Template

Example idea from Broadcast path - demonstrates structure for exploratory GitHub discussions.

---

## Structure data at source with YAML frontmatter

**Type:** `idea`
**Labels:** `identity:spoon`

### Context

From Construct review of `matrix` project. Spoon reframed the problem during perspectives phase.

**Source:** Spoon's reframing

### The Idea

What if the data was structured at the source?

If RAM files used YAML frontmatter, one query engine could replace 24 parsers:

```markdown
---
identity: smith
status: in_progress
tags: [security, blocker]
mentions: [cypher, deus]
created: 2025-11-26
---

# Task content here...
```

Then commands become queries:
- `matrix velocity` → query frontmatter for status fields
- `matrix tension-map` → query for conflicting tags

### Questions to Consider

- Is this solving the right problem?
- Would structured frontmatter feel bureaucratic?
- Does the freeform nature of RAM files have value?

### Potential Benefits

- Single query engine replaces 24 parsers
- Flexible exploration without new commands
- Structured data enables new possibilities

### Rough Implementation Path

1. Define frontmatter schema
2. Build unified query engine
3. Migrate existing commands
4. Deprecate individual parsers

### Handoff

1. Spoon validates this is the right reframe
2. Architect designs if approved
3. Smith implements
