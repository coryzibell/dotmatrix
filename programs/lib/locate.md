# locate - Project Detection

**Include:** Referenced by programs that need to find a target repo/project.

## Logic

1. **Explicit argument** - `/load <program> <path>` or `/load <program> <project-name>`
   - If absolute path: use directly
   - If project name: look up in `~/.matrix/zion/project/INDEX.md`

2. **Current directory** - Check if cwd is a git repo
   - `git rev-parse --show-toplevel` succeeds → use that

3. **Conversation context** - Review recent discussion
   - Look for repo paths, project names mentioned
   - If one obvious candidate: use it
   - If multiple candidates: ask which one

4. **Ask** - If none of the above work, or if ambiguous
   - "Which project?" with list from INDEX.md if available

**When in doubt, ask.** Don't guess at the target repo.

## Output

- Absolute path to repo root
- Project name (for STATUS.md lookup)

## Usage in Programs

```markdown
### Phase 0: Locate

> See `_locate.md` for project detection logic.

Output: Absolute path to repo, project name
```
