# Ideas

## Agent Audio Cues

### Matrix Sound Effects on Dispatch
- **Concept:** Play film audio clips when agents are dispatched
- **Examples:**
  - Spoon: *"There is no spoon"*
  - Tank: *"Operator"*
  - Morpheus: *"Free your mind"*
  - Trinity: *"Dodge this"*
- **Implementation Options:**
  - `rodio` crate - native Rust, but needs `libasound.so` at runtime on Linux
  - Shell out to `ffplay`/`aplay`/`afplay` - more portable, external dependency
  - Consider: hook into Claude Code's hook system? Or mx CLI?
- **Research:** See `ram/tank/rust-audio-playback-research.md`

---

## Zion Enhancements

### Project Status Field
- **Context:** Compress program needs to know which projects are active vs closed
- **Problem:** Currently no status field in projects table
- **Solution:** Add `status` column (active/dormant/closed) to projects schema
- **Benefit:** Zion Control can skip archiving RAM for closed projects, keep working notes for active ones
