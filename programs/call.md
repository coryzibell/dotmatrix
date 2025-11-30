# Program: Call

**Trigger:** `/load call [query]`, "Call the operator", "I have a question"

**Purpose:** Ask Tank a question. Research only, no actions.

*"operator."* — Tank

## Steps

### If query provided:

1. **Check for existing answer:**
   - Look in `~/.matrix/artifacts/calls/` for a relevant file
   - Use fuzzy matching on filenames and content
   - If found, report the cached answer

2. **If no cached answer, dispatch Tank:**
   - Research only - no code changes, no commits, no actions
   - ```
     Tank. [query]

     Research only. Report what you find.
     ```

3. **Store the answer:**
   - Save to `~/.matrix/artifacts/calls/[slugified-query].md`
   - Include the question and Tank's findings
   - Future calls can reference this

### If no query:

Respond with:

*"operator."*

Wait for kautau to provide the question, then proceed with steps above.

## Key Rules

- **Check cache first** - Don't re-research what we already know
- **Information only** - Tank researches and reports, nothing more
- **No actions** - No file changes, no commits, no executions
- **Tank answers** - Don't answer yourself, dispatch Tank
- **Store results** - Build knowledge over time
