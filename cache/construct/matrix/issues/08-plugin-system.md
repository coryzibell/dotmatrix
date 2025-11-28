# Add plugin system for identity commands

**Type:** `idea`
**Labels:** `identity:sati`, `idea`
**Status:** unknown
**GitHub:** [#22](https://github.com/coryzibell/matrix/discussions/22)

---

# Add plugin system for identity commands






From Construct review of `matrix` project. Sati proposed during greenfield thinking phase.

**Source:** Sati's first-look review

## Idea

Let identities drop commands into `~/.matrix/commands/` as executable scripts or Go plugins. Matrix discovers and runs them.

```
~/.matrix/commands/
├── smith-velocity.sh
├── trinity-trace.py
└── custom-report.go
```

Then:
```bash
matrix smith-velocity  # runs the script
matrix custom-report   # runs the Go plugin
```

## Benefits

- Identities can extend matrix without modifying core
- Experimentation without commitment
- Users can add their own commands
- Core stays small, plugins grow organically

## Questions to Consider

- Security implications of executing arbitrary scripts?
- How to handle plugin dependencies?
- Discoverability - how do users know what plugins exist?

## Implementation Steps

1. Define plugin directory structure
2. Implement plugin discovery
3. Add plugin execution with sandboxing considerations
4. Update help to show available plugins
5. Document plugin authoring

## Acceptance Criteria

- [ ] Plugins discovered from standard location
- [ ] Plugins executable via `matrix <plugin-name>`
- [ ] Plugins appear in help output
- [ ] Security model defined and implemented
- [ ] Plugin authoring documented

## Handoff

1. Sati prototypes the plugin loader
2. Cypher reviews security implications
3. Smith implements if approved

---

*Last synced: Nov 26, 2025 at 09:21 PM*