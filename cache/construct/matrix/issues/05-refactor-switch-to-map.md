# Refactor command switch statement to map-based dispatch

**Type:** `issue`
**Labels:** `identity:ramakandra`, `improvement`, `tech-debt`
**Status:** open
**GitHub:** [#19](https://github.com/coryzibell/matrix/issues/19)

---

# Refactor command switch statement to map-based dispatch






From Construct review of `matrix` project. Sati identified code smell during fresh-eyes review.

**Source:** Sati's first-look review

## Problem

The main command dispatcher uses a 200-line switch statement. This is:
- Hard to maintain
- Prone to errors when adding commands
- Makes it difficult to introspect available commands

## Solution

Replace switch statement with `map[string]handler` pattern:

```go
type CommandHandler func(args []string) error

var commands = map[string]CommandHandler{
    "garden-paths": gardenPathsCmd,
    "tension-map":  tensionMapCmd,
    // ...
}

func dispatch(cmd string, args []string) error {
    handler, ok := commands[cmd]
    if !ok {
        return fmt.Errorf("unknown command: %s", cmd)
    }
    return handler(args)
}
```

This enables:
- Easy command introspection for help generation
- Cleaner addition of new commands
- Potential for plugin system later

## Implementation Steps

1. Define `CommandHandler` type
2. Create commands map with all handlers
3. Replace switch with map lookup
4. Update help generation to use map keys
5. Verify all commands still work

## Acceptance Criteria

- [ ] No switch statement for command dispatch
- [ ] All 24 commands work as before
- [ ] Help text generated from map keys
- [ ] Tests pass
- [ ] Code is more maintainable

## Handoff

1. Ramakandra refactors the dispatch logic
2. Deus verifies all commands still work
3. Neo reviews and merges

---

*Last synced: Nov 26, 2025 at 09:21 PM*