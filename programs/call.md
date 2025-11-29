# Program: Call

**Trigger:** `/load call [query]`, "Call the operator", "I have a question"

**Purpose:** Ask Tank a question. Research only, no actions.

*"Operator."* — Tank

## Steps

### If query provided:

Dispatch Tank with the query. Research only - no code changes, no commits, no actions.

```
Tank. [query]

Research only. Report what you find.
```

### If no query:

Respond with:

*"Operator."*

Wait for kautau to provide the question, then dispatch Tank.

## Key Rules

- **Information only** - Tank researches and reports, nothing more
- **No actions** - No file changes, no commits, no executions
- **Tank answers** - Don't answer yourself, dispatch Tank
