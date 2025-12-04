# Markdown Parser for fiche

## Concept

```
Model writes → Markdown (natural for LLMs)
Model reads ← fiche (efficient for LLMs)
```

Markdown-to-fiche parser for feeding structured content back into context efficiently.

## Open Questions

1. **What markdown structures matter most?**
   - Tables (obvious fit - rows/columns → fiche)
   - Lists (nested → flattened paths)
   - Frontmatter YAML (metadata)
   - Headers as hierarchy?
   - Code blocks (preserve as strings?)

2. **Is this bidirectional?**
   - `md → fiche` (for feeding back to models)
   - `fiche → md` (for human output)
   - Or just one direction?

3. **Where does this live?**
   - New command in base-d: `bd markdown encode`?
   - Separate tool?

## Initial Thinking

Tables and lists are the high-value targets. Headers provide context but aren't structured data. Code blocks are just strings.

## Status

Parked - kautau has another task first.
