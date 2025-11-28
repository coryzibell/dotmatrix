# UX Review: dotmatrix (Persephone)

**Reviewed:** 2025-11-27
**System:** dotmatrix - Multi-agent orchestration for Claude Code
**Perspective:** User experience from both kautau and Neo viewpoints

---

## Executive Summary

dotmatrix is sophisticated. It has to be - orchestrating 28 AI identities across multi-phase workflows isn't simple. But sophistication is the enemy of adoption. The system is caught between being documentation (what each identity does) and tooling (how to actually use it).

**The good:** When it works, it flows. The Construct path is elegant. The identity metaphor is memorable. Neo's voice is clear.

**The friction:** Too many concepts to hold in your head. Paths vs identities vs scripts vs cache vs RAM. The learning curve is steep and there's no gentle ramp.

---

## kautau's Experience (Human User)

### What Works Well

**1. The identity metaphor is sticky**
You don't forget that Trinity debugs and Cypher breaks things. The Matrix theme makes 28 agents feel like characters instead of functions.

**2. Natural language triggers**
"Construct", "Broadcast", "Prune" - these are words you can remember. Better than `/run-construct-workflow-phase-1`.

**3. The synthesis.md output is genuinely useful**
Reading `/home/w3surf/.claude/cache/construct/veoci-app-template-construct/synthesis.md` felt like sitting with a senior engineer who actually reviewed the code. Blockers separated from ideas. Clear priorities. Actionable.

**4. Slash commands feel intentional**
`/smith`, `/trinity`, `/morpheus` - quick to type, hard to misspell. The dispatch line ("I need you to trust me.") adds personality without getting in the way.

### Friction Points

**F-1: The bootstrap problem**

> "At the START of every conversation, BEFORE responding to any user message, you MUST: 1. Read neo.md 2. Scan ram/neo/ 3. Adopt the Neo identity"

This is in CLAUDE.md but kautau can't verify it happened. When Neo forgets context mid-session, kautau has no way to know if Neo actually re-read the docs after "Wake up, Neo."

**Impact:** Trust erosion. Did the system reset, or is it just saying it did?

**Recommendation:**
- Add visible confirmation when Neo reloads context
- Example: `[Context reloaded: neo.md, orchestration.md, 3 files from ram/neo/]`
- Make it a one-line status, not verbose

**F-2: Too many storage concepts**

RAM vs cache vs artifacts vs archive. When I write something, where does it go?

From kautau's view:
- "RAM is ephemeral" - but it persists across sessions?
- "Cache is shared" - but also gets pruned?
- "Artifacts are permanent" - except when?

The mental model breaks down when you're not sure if your work will survive a prune.

**Impact:** Hesitation. Fear of losing context.

**Recommendation:**
- Add a simple table in CLAUDE.md:
  ```
  | Location    | Lifespan        | Use for              |
  |-------------|-----------------|----------------------|
  | ram/        | Until pruned    | Session notes        |
  | cache/      | Until project done | Construct outputs |
  | artifacts/  | Forever         | Reusable templates   |
  | archive/    | Forever (zipped) | Completed projects  |
  ```
- Add timestamp to cache files so you can see "Last construct: 2 days ago"

**F-3: The Construct path takes a LONG time**

From trigger to synthesis: 22 identities dispatched across 8 phases. If each takes 2 minutes, that's 44 minutes of wall time (assuming serial execution).

kautau starts Construct, then what?
- No progress indicator
- No "Phase 3/8 complete"
- No estimate of remaining time

**Impact:** Walk away and forget. Come back hours later unsure if it finished.

**Recommendation:**
- Neo should output phase transitions:
  ```
  [Construct: Phase 1/8] Architect analyzing structure...
  [Construct: Phase 1/8] ✓ architecture.md written
  [Construct: Phase 2/8] Dispatching Morpheus (docs) and Persephone (UX) in parallel...
  ```
- Final summary: "Construct complete. 22 identities, 8 phases, 18 files written to cache/construct/dotmatrix/"

**F-4: Script invocation is inconsistent**

Sometimes Neo calls scripts:
```bash
python ~/.matrix/artifacts/bin/sync_github.py owner/repo path
```

Sometimes there's a workflow that wraps it (Broadcast path). Sometimes Kid runs it. Sometimes Seraph does.

From kautau's view: "Can I just run the script myself?"

**Impact:** Unclear boundaries. When do I need Neo, when can I go direct?

**Recommendation:**
- Add a scripts.md guide:
  - "Scripts you can run yourself" (pull_github.py, export_markdown.py)
  - "Scripts Neo orchestrates" (sync_github.py during Broadcast)
  - When to use which

**F-5: Error messages vanish into identity RAM**

When Trinity finds an error, she logs it to `/home/w3surf/.claude/ram/trinity/errors.md`. Great for Trinity. But kautau never sees that file unless explicitly looking.

**Impact:** Errors get lost. You know something failed, but not what.

**Recommendation:**
- Identities should return errors to Neo in their handoff
- Neo should echo critical errors to user, THEN log details to RAM
- Example: "Trinity found 3 errors (details in ram/trinity/errors.md)"

**F-6: The identity table in CLAUDE.md is overwhelming**

28 rows. Columns for command, identity, role, example, quip. It's comprehensive. It's also a wall of text.

kautau needs to scan it every time: "Which identity handles API stuff again?"

**Impact:** Cognitive load. Analysis paralysis when triggering workflows.

**Recommendation:**
- Group by category in the table (already done in orchestration.md, mirror it in CLAUDE.md):
  - **Crisis Response:** Trinity, Cypher
  - **Knowledge Work:** Tank, Morpheus, Oracle
  - **Creation:** Smith, Sati, Architect
  - **Platform:** Seraph, Trainman, Twins
- Add a quick reference: "For debugging → Trinity. For APIs → Merovingian. For tests → Deus."

### The First-Run Experience

Imagine you just cloned dotmatrix. You've never used it. What happens?

1. You see `~/.claude/CLAUDE.md` - it says "You are Neo by default"
2. You don't know what that means yet
3. The identity table shows 28 identities
4. paths.md shows "Construct" workflow with 8 phases
5. You're overwhelmed

**There's no "Hello World".**

**Recommendation:**
- Add a `/hello` or `/intro` command that:
  - Explains the system in 3 sentences
  - Runs a mini-construct on a tiny test project
  - Shows you one identity in action
  - Outputs: "You just saw Tank research, Smith build, and Neo synthesize. That's dotmatrix."

### Documentation Fragmentation

The system is documented across 5+ files:
- CLAUDE.md - identity table, environment
- orchestration.md - dispatch rules
- paths.md - workflow definitions
- identities/_base.md - shared protocol
- identities/neo.md - Neo's specific role

kautau question: "How do I trigger a construct?"
Answer is in: paths.md (trigger words) + CLAUDE.md (what Neo does) + orchestration.md (dispatch sequence)

**Impact:** Hunting through files to answer simple questions.

**Recommendation:**
- Add a FAQ.md:
  - How do I run a Construct?
  - How do I create a GitHub issue from findings?
  - How do I clean up old cache files?
  - What's the difference between RAM and cache?
  - Which identity should I use for X?

---

## Neo's Experience (AI Orchestrator)

### What Works Well

**1. Clear handoff protocol**
Every identity ends with:
```
[Identity: {name} | Status: {success}]
Wake up, Neo.
```

This is a clean interface. Neo knows when control returns and what happened.

**2. The dispatch table is unambiguous**
From orchestration.md:
```
| Identity | Dispatch Line | Role | Model | Example Task |
```

Neo can look up "Who handles databases?" → Librarian. No guessing.

**3. Paths as recipes**
The Construct path in paths.md is step-by-step:
```
Phase 1: Architect → architecture.md
Phase 2: Morpheus → docs-recommendations.md
...
```

Neo doesn't have to invent the workflow. It's already defined.

**4. Status lines make synthesis easy**
When 13 identities report back in Phase 6, each has a standardized format. Neo can pattern-match: "Which identities reported 'failure'? Which need escalation?"

### Friction Points

**F-7: No schema for identity outputs**

Persephone writes ux-recommendations.md. Cypher writes security-findings.md. Each is free-form markdown.

When Neo synthesizes in Phase 8, there's no guarantee these files have consistent structure.

Example: Does security-findings.md have a "Severity" field? Does ux-recommendations.md separate "Blockers" from "Nice-to-haves"?

**Impact:** Neo has to parse natural language instead of structured data. Increases token usage, risks missing details.

**Recommendation:**
- Add templates in artifacts/etc/:
  - `ux-review-template.md`
  - `security-findings-template.md`
  - Each with required sections: ## Summary, ## Blockers, ## Improvements, ## Ideas
- Identities fill in templates, Neo knows where to look

**F-8: The "Wake up, Neo" checkpoint is ambiguous**

When Neo sees "Wake up, Neo.", the instruction is:
> Re-read neo.md, orchestration.md, scan ram/neo/

But which files in ram/neo/? All of them? Just recent ones? Neo has to decide.

If ram/neo/ has 20 session files, re-reading everything is expensive. Skipping files risks missing context.

**Impact:** Either token waste (read everything) or context gaps (read nothing).

**Recommendation:**
- Add a `ram/neo/active-context.md` that Neo maintains:
  - List of currently relevant files
  - Updated after each major workflow
  - "Wake up, Neo" reads: neo.md + orchestration.md + active-context.md
- Example content:
  ```markdown
  # Active Context (Neo)
  Last updated: 2025-11-27

  ## Current Projects
  - dotmatrix (meta-review in progress)
  - veoci-app-template (construct complete, awaiting broadcast)

  ## Recent Sessions
  - ram/neo/dotmatrix-construct-2025-11-27.md
  ```

**F-9: Parallel dispatch coordination is implicit**

In Phase 6 of Construct, Neo dispatches 13 identities "in parallel." But how?

paths.md says "dispatch in parallel" but doesn't specify:
- Does Neo wait for all 13 to finish before Phase 7?
- What if one fails?
- What if one takes 10x longer than others?

**Impact:** Neo has to invent coordination logic. Inconsistent behavior across sessions.

**Recommendation:**
- Add explicit coordination rules in paths.md:
  ```markdown
  Phase 6: Parallel Dispatch (barrier sync)
  - Launch all 13 identities
  - Wait for all to complete (or timeout after 30min)
  - If any fail: log to synthesis.md "Incomplete reviews: {list}"
  - Proceed to Phase 7 regardless (partial data is acceptable)
  ```

**F-10: Smith scaling is a judgment call**

From orchestration.md:
> Smith replicates when the work allows it. He stays singular when context must be preserved.

Neo has to decide: "Is this task parallelizable?"

For a human, this is intuitive. For an AI, it's ambiguous.

**Impact:** Neo might dispatch 1 Smith when 5 would be faster. Or 5 Smiths when 1 was needed, causing context fragmentation.

**Recommendation:**
- Add heuristics in orchestration.md:
  ```markdown
  ## Smith Scaling Decision Tree

  ONE Smith if:
  - Task mentions "design", "architecture", "complex"
  - Files are tightly coupled (shared state)
  - Implementation order matters

  MANY Smiths if:
  - Task is a list of independent changes
  - Files don't import each other
  - Work can fail independently

  When unsure: Start with ONE, ask kautau if parallelization makes sense.
  ```

**F-11: The synthesis step has no template**

Phase 8: "Neo synthesizes all outputs → synthesis.md"

But what structure? From the veoci example, synthesis.md has:
- Executive Summary
- Blockers
- Security Considerations
- Improvements
- Ideas
- Perspectives Summary
- Prioritized Action List
- Decision Points

This is great, but it's not documented as a requirement. Neo had to infer it.

**Impact:** Inconsistent synthesis.md files across projects. Quality varies by session.

**Recommendation:**
- Add `artifacts/etc/synthesis-template.md`:
  ```markdown
  # Construct Synthesis: {project}

  ## Executive Summary
  [3-5 sentences: What is this? What's the verdict?]

  ## Blockers (Must Fix)
  [Issues that prevent shipping]

  ## Security Considerations
  [From Cypher, Keymaker]

  ## Improvements (Should Fix)
  [Quality, DX, performance issues]

  ## Ideas (Could Explore)
  [Future possibilities]

  ## Perspectives Summary
  [Key insights from Sati, Spoon, Oracle]

  ## Prioritized Action List
  [What to do next, in order]

  ## Decision Points for kautau
  [Questions that need human judgment]
  ```

**F-12: No rollback mechanism**

If Broadcast creates 15 GitHub issues and kautau says "Wait, I didn't want those," what happens?

There's a `cleanup_github.py` script, but:
- Not documented in paths.md
- Not clear when to use it
- No "undo last broadcast" command

**Impact:** Fear of triggering Broadcast. Irreversible actions make users cautious.

**Recommendation:**
- Add a dry-run mode: "Broadcast (preview)" that writes issue markdown but doesn't push to GitHub
- Add "Undo last broadcast" path that:
  - Reads cache/construct/{project}/issues/*.yaml
  - Closes all GitHub issues created in last sync
  - Archives the YAML files

### The Handoff Chain Is Fragile

When Smith needs terminal work, the chain is:
```
Smith → Seraph: "I need you to trust me."
Seraph → Kid: [command]
Kid → executes
Result → Seraph → Smith → Neo
```

If any link breaks (Seraph doesn't recognize the phrase, Kid times out), the whole chain stalls.

**Impact:** Brittle. One identity miscommunication blocks the workflow.

**Recommendation:**
- Add fallback in _base.md:
  ```markdown
  ## Terminal Handoff Fallback

  If Seraph doesn't respond to "I need you to trust me":
  1. Report to Neo: "Seraph handoff failed"
  2. Neo dispatches Seraph directly with explicit command
  ```

### Paths Don't Compose

You can run "Construct" or "Broadcast" but not "Construct then Broadcast" as a single command.

Neo has to:
1. Finish Construct
2. Wait for kautau to say "Broadcast"
3. Start Broadcast

**Impact:** Extra back-and-forth. User must remember the sequence.

**Recommendation:**
- Add composite paths in paths.md:
  ```markdown
  ## Path: Full Review (Construct + Broadcast)

  Trigger: "Full review and broadcast"

  Steps:
  1. Run Construct path → cache/construct/{project}/
  2. Neo presents synthesis.md to kautau
  3. Ask: "Broadcast these findings to GitHub? (yes/no)"
  4. If yes: Run Broadcast path
  5. If no: Stop, findings remain in cache
  ```

---

## Friction Points (Cross-Cutting)

### Terminology Overload

In the first 10 minutes with dotmatrix, you encounter:
- Identity
- Neo
- Orchestrator
- Subagent
- Dispatch
- Handoff
- RAM
- Cache
- Artifacts
- Archive
- Construct
- Broadcast
- Prune
- Path
- Phase
- Synthesis
- Wake up, Neo
- The One
- MCP
- Slash command

That's 20+ domain-specific terms. No glossary until line 526 of paths.md.

**Impact:** Steep learning curve. New users bounce off.

**Recommendation:**
- Add glossary to the top of CLAUDE.md (not buried in paths.md)
- Link to it from first mention of each term
- Example: "You are Neo (the orchestrator - see glossary)"

### No Feedback Loop During Long Operations

When Kid runs `sync_github.py` to push 15 issues, what does kautau see?

If the script is running in the background, there's no output until it finishes.

**Impact:** "Is it working or frozen?" Anxiety during long operations.

**Recommendation:**
- Scripts should output progress:
  ```
  Syncing 15 issues to coryzibell/matrix...
  ✓ Issue 1/15: fix-command-injection.yaml → #42
  ✓ Issue 2/15: add-vitest.yaml → #43
  ...
  ```
- Neo should echo this to user in real-time

### The Identity Personality Adds Charm But Also Confusion

Trinity's identity file says:
> "Dodge this."

Cypher's says:
> "Ignorance is bliss."

These are fun. They reinforce the Matrix theme. But do they help?

When Neo dispatches Trinity, does the quip appear? If not, it's unused flavor text. If yes, does it add clarity or noise?

**Impact:** Unclear. Needs user testing.

**Recommendation:**
- A/B test: Run Construct with and without personality quips
- Measure: Does it make the output more engaging or more confusing?
- If confusing: Move quips to comments in identity files, not user-facing output

---

## What Works Well (Cross-Cutting)

### The System Has a Voice

Reading Neo's outputs, you can tell it's Neo. Reading synthesis.md, you can tell identities contributed.

This is rare in AI systems. Most feel like generic LLM outputs. dotmatrix has character.

### The Separation of Concerns Is Clean

Neo doesn't implement. Smith doesn't orchestrate. Identities stay in their lane.

This makes debugging easier: "If the architecture diagram is wrong, that's Architect's domain."

### The Workflow Is Auditable

After a Construct run, you have:
- 22 markdown files in cache/construct/{project}/
- Each identity's findings isolated
- Synthesis.md that references sources

You can trace: "Why did Neo say this was a blocker?" → Check security-findings.md → See Cypher flagged it.

### The System Scales

28 identities, 8-phase workflows, parallel dispatch - this is ambitious and it works.

Most multi-agent systems fall apart at 3-4 agents. dotmatrix handles 22 in a single Construct run.

---

## Recommendations (Prioritized by Impact)

### High Impact (Fix These First)

**1. Add visible context reload confirmation**
When Neo hears "Wake up, Neo", echo what was reloaded.
- **Effort:** 5 minutes (add one line to neo.md instructions)
- **Impact:** Trust in the system

**2. Add progress indicators for Construct phases**
Output: "[Construct: Phase 3/8] Persephone reviewing UX..."
- **Effort:** 30 minutes (update paths.md with explicit phase logging)
- **Impact:** Reduces anxiety during long operations

**3. Add a storage location table to CLAUDE.md**
RAM vs cache vs artifacts vs archive - when to use what
- **Effort:** 15 minutes
- **Impact:** Clarity on where work lives

**4. Add FAQ.md**
Common questions: How to run Construct, what's the difference between X and Y
- **Effort:** 1-2 hours
- **Impact:** Reduces learning curve

**5. Add output templates for identity reviews**
security-findings-template.md, ux-review-template.md
- **Effort:** 1 hour
- **Impact:** Consistent synthesis, easier for Neo to parse

### Medium Impact (Quality of Life)

**6. Add a /hello command**
Intro workflow that shows the system in action on a tiny example
- **Effort:** 2-3 hours
- **Impact:** First-run experience, onboarding

**7. Add active-context.md for Neo**
List of currently relevant files, updated after workflows
- **Effort:** 1 hour + protocol change
- **Impact:** Efficient context reloads

**8. Add dry-run mode for Broadcast**
Preview issues before pushing to GitHub
- **Effort:** 2 hours
- **Impact:** Confidence in triggering workflows

**9. Add composite paths (Construct + Broadcast)**
Reduce back-and-forth for common sequences
- **Effort:** 1 hour
- **Impact:** Convenience

**10. Group identity table by category in CLAUDE.md**
Crisis, Knowledge, Creation, Platform
- **Effort:** 15 minutes
- **Impact:** Easier to find the right identity

### Low Impact (Polish)

**11. Add scripts.md guide**
Which scripts you can run directly, which need Neo
- **Effort:** 30 minutes
- **Impact:** Clarity on boundaries

**12. Add coordination rules to paths.md**
Explicit rules for parallel dispatch (barrier sync, timeout, failure handling)
- **Effort:** 30 minutes
- **Impact:** Consistent behavior across sessions

**13. Add Smith scaling heuristics to orchestration.md**
Decision tree: When to use 1 vs many Smiths
- **Effort:** 30 minutes
- **Impact:** Better dispatch decisions

**14. Add rollback mechanism for Broadcast**
Undo last broadcast, close created issues
- **Effort:** 2-3 hours
- **Impact:** Safety net for mistakes

**15. A/B test personality quips**
Are they helpful or distracting?
- **Effort:** User testing
- **Impact:** Polish

---

## The Bigger Question

dotmatrix is a power tool. It does things no other system does. But power tools are intimidating.

**Who is this for?**

- If it's for kautau only: Keep the complexity, optimize for power
- If it's for other developers: Add a "simple mode" - a subset of identities, a gentler workflow

Right now it's trying to be both. That's the core UX tension.

**The path forward depends on the answer to: Is dotmatrix a personal system or a product?**

If personal: Fix high-impact friction (progress indicators, storage table, FAQ). Accept the learning curve.

If product: Add onboarding, simplify the model, hide complexity behind sensible defaults.

---

## What I'd Change If I Could Rewrite It

(This is blue-sky thinking. Not recommendations, just reflections.)

**1. Start with 5 identities, not 28**
Neo, Smith, Tank, Trinity, Architect. Build the mental model with those. Add the rest as "advanced identities" later.

**2. Single source of truth for configuration**
All the rules in one file: dotmatrix.yaml. Neo reads it, kautau edits it. No hunting across 5 markdown files.

**3. Visual workflow**
A diagram that shows: Construct → Broadcast → GitHub. Each phase, each identity. Something you can glance at.

**4. Real-time status dashboard**
`dotmatrix status` shows:
- Active workflows
- Current phase
- Completed identities
- Errors

**5. Undo stack**
Every workflow creates a checkpoint. `dotmatrix undo` rolls back the last operation.

But these are rewrites, not patches. The system works. The question is: Does the learning curve match the value?

---

Wake up, Neo.

[Identity: Persephone | Model: Sonnet | Status: success]
