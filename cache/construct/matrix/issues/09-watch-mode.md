# Add watch mode for real-time updates

**Type:** `idea`
**Labels:** `identity:sati`, `idea`
**Status:** unknown
**GitHub:** [#23](https://github.com/coryzibell/matrix/discussions/23)

---

# Add watch mode for real-time updates






From Construct review of `matrix` project. Sati proposed during greenfield thinking phase.

**Source:** Sati's first-look review

## Idea

Add `--watch` flag to commands for real-time garden viewing:

```bash
matrix garden-paths --watch
matrix tension-map --watch
```

The display updates as RAM files change, like a live dashboard.

## Benefits

- See the garden grow in real-time during work sessions
- Spot emerging patterns immediately
- Better visibility into multi-agent workflows

## Questions to Consider

- Which commands benefit from watch mode?
- Performance impact of file watching?
- Terminal UI considerations (clearing, redrawing)

## Implementation Steps

1. Add file watcher using fsnotify or polling
2. Implement terminal clearing/redrawing
3. Add `--watch` flag to relevant commands
4. Handle graceful exit (Ctrl+C)
5. Consider refresh interval configuration

## Acceptance Criteria

- [ ] `--watch` flag works on key commands
- [ ] Display updates when files change
- [ ] Clean exit on Ctrl+C
- [ ] Reasonable CPU usage while watching
- [ ] Works across platforms

## Handoff

1. Sati prototypes the watch mechanism
2. Smith implements across commands
3. Trainman verifies cross-platform behavior

---

*Last synced: Nov 26, 2025 at 09:30 PM*