# Structure data at source with YAML frontmatter

**Type:** `idea`
**Labels:** `identity:spoon`, `idea`
**Status:** unknown
**GitHub:** [#21](https://github.com/coryzibell/matrix/discussions/21)

---

# Structure data at source with YAML frontmatter






From Construct review of `matrix` project. Spoon reframed the problem during perspectives phase.

**Source:** Spoon's reframing

## Problem

Matrix has 24 parsers for 24 commands, each extracting data from markdown files in different ways. This is the assumption that created complexity.

## Reframe

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
- `matrix garden-paths` → query mentions field

## Questions to Consider

- Is this solving the right problem?
- Would structured frontmatter feel bureaucratic?
- Does the freeform nature of RAM files have value?

## Implementation Steps

1. Define frontmatter schema
2. Update RAM file templates (garden-seeds)
3. Build unified query engine
4. Migrate existing commands to use queries
5. Deprecate individual parsers

## Acceptance Criteria

- [ ] Frontmatter schema defined
- [ ] Query engine handles all current command needs
- [ ] Existing commands work with new approach
- [ ] RAM files remain human-readable

## Handoff

1. Spoon validates this is the right reframe
2. Architect designs the schema and query engine
3. Smith implements

---

*Last synced: Nov 26, 2025 at 09:21 PM*