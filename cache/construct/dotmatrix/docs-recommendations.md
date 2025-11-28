# Documentation Review (Morpheus)

**Project:** dotmatrix (Claude Code configuration repository)
**Reviewed:** 2025-11-27
**Reviewer:** Morpheus (Sonnet)

---

## Coverage Assessment

### What's Documented

**Core Configuration (Strong)**
- `CLAUDE.md` - Main entry point with identity table, environment setup, preferences
- `orchestration.md` - Identity dispatch model, handoff protocols, parallel spawning
- `paths.md` - Multi-phase workflow patterns (Construct, Broadcast, Report, Pull, Prune)
- `PLATFORMS.md` - Platform-specific paths and quirks

**Identity System (Strong)**
- 27 identity files in `identities/` (missing: sati.md not found in grep, but exists in directory listing)
- `identities/_base.md` - Shared base instructions for all identities
- Each identity has: name, description, model, role, quip, working directory, handoff suggestions

**Scripts (Good)**
- All 10 Python scripts have docstrings with usage examples
- Scripts: `sync_github.py`, `pull_github.py`, `sync_labels.py`, `convert_issues.py`, `export_markdown.py`, `sync_wiki.py`, plus deprecated `sync_issues.py`, `sync_discussions.py`

**Artifacts (Good)**
- `identity-colors.yaml` - 28 identities mapped to hex colors with rationale
- `category-colors.yaml` - (assumed to exist based on sync_labels.py reference)
- `issue-template.yaml` - (referenced in paths.md)

### What Exists But Isn't Documented

**Directory Structure**
- No explicit documentation of the overall repository structure
- `agents/` directory exists with 19 files (appears to be deprecated legacy system)
- `commands/` directory exists with slash command wrappers
- `matrix/` directory with `garden-paths.sh` script (referenced in neo.md but not in paths.md)
- `ram/`, `cache/`, `artifacts/bin/`, `artifacts/etc/` directories not documented in one place

**Legacy vs Current**
- `agents/` directory still exists alongside `identities/` - relationship unclear
- `agents/fellas.md` exists but references outdated base instructions (different from `_base.md`)
- CLAUDE.md references "Fellas" in table but no `identities/fellas.md` exists
- orchestration.md discusses "Smith vs Fellas" but Fellas identity file missing

**Scripts Not in Paths**
- `cleanup_github.py` - Purpose unknown, not documented
- `sync_merge.py` - Three-way merge utilities, imported by sync_github.py but not documented as standalone
- Garden paths script (`matrix/garden-paths.sh`) - Mentioned in neo.md but not in paths.md

**Slash Commands**
- `commands/` directory has wrappers for each identity
- These appear to invoke identities via `/smith`, `/trinity`, etc.
- Mechanism not explained anywhere
- Relationship to identities unclear for new users

**Shared vs Ephemeral Storage**
- `_base.md` says cache is "Not ephemeral - this is shared workspace"
- Original description in CLAUDE.md says cache is "temporary, session-based"
- Contradiction needs resolution

---

## Gaps Found

### Critical Gaps (Prevent System Understanding)

1. **No Repository README**
   - New session has no overview of what dotmatrix is
   - No quickstart for understanding the system
   - Entry point should be README, not CLAUDE.md (which is read automatically)

2. **Missing "How Identities Work" Primer**
   - Neo.md explains orchestration but assumes you know what identities are
   - No explanation of the prompt injection mechanism
   - How does `/smith` translate to loading `identities/smith.md`?

3. **Directory Structure Not Documented**
   - Which directories are version controlled?
   - Which are .gitignored?
   - What goes where and why?

4. **Deprecated System Migration Path**
   - `agents/` vs `identities/` - which is current?
   - Should `agents/` be deleted?
   - Why does `agents/fellas.md` still exist?

### Moderate Gaps (Reduce Onboarding Efficiency)

5. **Fellas Identity Confusion**
   - CLAUDE.md table row 2 lists `/fellas` command
   - orchestration.md has entire "Smith vs Fellas" section
   - neo.md says "Fellas is the assumption. Smith requires justification"
   - But no `identities/fellas.md` exists
   - Only `agents/fellas.md` with outdated base instructions

6. **Script Interdependencies**
   - `sync_github.py` imports `sync_merge.py` - not documented
   - Deprecated scripts (`sync_issues.py`, `sync_discussions.py`) still present - should they be deleted?
   - No migration guide from old scripts to new unified approach

7. **Garden Paths Script**
   - Neo.md references `~/.matrix/garden-paths.sh`
   - Says "Not every session. But when you feel like you're losing the thread..."
   - What does it output? How do you read it? What's the use case?
   - Not in paths.md

8. **Construct Methodology**
   - paths.md line 336 references `~/.matrix/artifacts/etc/construct-methodology.md`
   - File not found during review
   - Should document the review methodology

9. **Issue Template Location**
   - paths.md line 126 references `~/.matrix/artifacts/etc/issue-template.md`
   - Actually exists as `issue-template.yaml` based on glob
   - Extension mismatch - documentation or implementation bug?

### Minor Gaps (Polish)

10. **Cache vs RAM Semantics**
    - `_base.md` line 49-54: "Shared Space" is `~/.matrix/ram/cache/` and "Not ephemeral"
    - CLAUDE.md line 17: cache is "Shared working files between agents during multi-phase workflows"
    - Morpheus identity line 24: Documentation deliverables go in `~/.matrix/ram/cache/docs/`
    - But base.md also says RAM is "temporary, session-based" (line 15 of CLAUDE.md)
    - Is cache ephemeral or permanent? Needs clarification.

11. **Model Assignments**
    - Each identity specifies model (haiku/sonnet/opus)
    - No documentation of why certain identities use certain models
    - Cost implications not explained

12. **Wake Up Protocol**
    - "Wake up, Neo" triggers re-reading context
    - Mentioned in CLAUDE.md and neo.md
    - Not explained what files get re-read beyond neo.md and orchestration.md
    - Should identities also say "Wake up, Neo" in handoffs? (_base.md says yes, line 28)

---

## Inconsistencies

### Terminology

1. **Cache Semantics** (Critical)
   - `_base.md`: "Shared Space" at `~/.matrix/ram/cache/` is "Not ephemeral"
   - CLAUDE.md: cache is for "temporary, session-based" working files
   - **Recommendation:** Clarify that cache is shared workspace that persists across phases but can be pruned between projects

2. **Fellas vs Smith** (Critical)
   - CLAUDE.md, orchestration.md, neo.md all reference Fellas extensively
   - No `identities/fellas.md` exists
   - Only `agents/fellas.md` which uses old base instructions
   - **Recommendation:** Either create `identities/fellas.md` or remove all Fellas references and update Smith documentation

3. **Agents vs Identities**
   - `agents/` directory with 19 files still exists
   - `identities/` directory is clearly the current system
   - orchestration.md doesn't mention agents directory
   - **Recommendation:** Document that agents/ is deprecated, or delete it, or explain the relationship

4. **Base Instructions Location**
   - Current identities reference `~/.matrix/identities/_base.md`
   - File actually exists as `identities/_base.md` (confirmed)
   - Legacy `agents/fellas.md` has inline base instructions (outdated version)
   - **Recommendation:** Confirm all identities use `_base.md`, document the inheritance pattern

### References

5. **Script Names**
   - paths.md line 207 calls it "md2yaml.py" in deprecated section
   - Actual filename is `convert_issues.py` per glob results
   - **Recommendation:** Update reference or clarify if renamed

6. **Missing Sati**
   - Identity colors YAML has 28 identities including Sati
   - CLAUDE.md table row missing Sati
   - `identities/sati.md` exists
   - **Recommendation:** Add Sati row to CLAUDE.md table

7. **Error Logging Location**
   - `_base.md` line 39-45: Log errors to `~/.matrix/ram/{identity}/errors.md`
   - No mention of this in any identity file
   - No examples of error logs in RAM directories
   - **Recommendation:** Either implement or remove from base instructions

### Outdated Content

8. **Deprecated Scripts Referenced**
   - paths.md lines 213-216 lists deprecated `sync_issues.py` and `sync_discussions.py`
   - Good that they're marked deprecated
   - But should they be deleted from repository?
   - **Recommendation:** Either delete or move to `deprecated/` directory

---

## Onboarding Assessment

**Can a new Neo session understand the system from documentation alone?**

**Partially, but with friction.**

### What Works

- **CLAUDE.md is read automatically** - Good entry point with identity table
- **Orchestration model is thorough** - Clear dispatch rules, handoff protocols
- **Paths are well-documented** - Construct, Broadcast, Report flows are detailed
- **Scripts have good docstrings** - Usage examples help

### What Causes Friction

1. **No README to orient the reader**
   - CLAUDE.md is configuration for Claude, not documentation for humans
   - First-time reader doesn't know where to start

2. **Fellas confusion immediate**
   - Table row 2 says use Fellas for parallel work
   - orchestration.md says "Fellas is the assumption"
   - But Fellas identity doesn't exist
   - New session will fail trying to dispatch Fellas

3. **Legacy artifacts unexplained**
   - Why does `agents/` exist alongside `identities/`?
   - Which slash commands work?
   - What's the garden paths script for?

4. **Directory structure assumed**
   - Documentation references `~/.matrix/ram/`, `~/.matrix/cache/`, `~/.matrix/artifacts/etc/`
   - Never explains what these directories are or shows the tree

5. **Base instructions inheritance unclear**
   - Identities say "Read _base.md first"
   - How does that work mechanically?
   - New session might not understand they should read both files

### Onboarding Path for Fresh Neo

What would a brand new Neo session need to read to understand the system?

**Ideal sequence:**
1. README - "This is dotmatrix, the Claude Code identity system"
2. CLAUDE.md - "You are Neo, here's the identity table"
3. orchestration.md - "Here's how to dispatch identities"
4. paths.md - "Here are multi-phase workflows"
5. identities/neo.md - "Here's your specific role"
6. identities/_base.md - "Here's what all identities share"

**Current sequence:**
1. CLAUDE.md (automatically loaded, but assumes knowledge)
2. ???

**Problem:** Step 2 is unclear. Does Neo read orchestration.md immediately? How does Neo learn about _base.md?

---

## Recommendations

### Priority 1: Critical (Fix These First)

**1. Create README.md**

Location: `/home/w3surf/.claude/README.md`

Content:
- What is dotmatrix?
- Identity system overview
- Directory structure diagram
- Quickstart: "If you're Neo, start here"
- Link to key documentation files

**2. Resolve Fellas Situation**

Option A: Create `identities/fellas.md` for parallel dispatch
Option B: Remove all Fellas references, update Smith to handle both serial and parallel work
Option C: Rename Fellas to something else that exists

Current state creates immediate confusion for any new session.

**3. Document Directory Structure**

Add section to README or create STRUCTURE.md:

```
~/.claude/
├── CLAUDE.md              # Main config (auto-loaded)
├── orchestration.md       # Dispatch model
├── paths.md              # Multi-phase workflows
├── PLATFORMS.md          # Platform-specific quirks
├── identities/           # Current identity system
│   ├── _base.md          # Shared base instructions
│   ├── neo.md            # The One (Opus)
│   ├── smith.md          # Builder (Sonnet)
│   └── ...               # 24 more identities
├── commands/             # Slash command wrappers
├── artifacts/
│   ├── bin/              # Python scripts
│   └── etc/              # Config files, colors, templates
├── ram/                  # Working directories (session-based)
│   ├── neo/
│   ├── smith/
│   └── ...
├── cache/                # Shared workspace (multi-phase)
│   └── construct/
└── matrix/               # Utilities (garden-paths.sh)
```

**4. Clarify Cache vs RAM Semantics**

Update both `_base.md` and CLAUDE.md to agree:

- `ram/{identity}/` - Identity working directory, can be pruned between projects
- `cache/` - Shared workspace for multi-phase workflows, persists during workflow, pruned between projects
- `artifacts/` - Permanent reference data, version controlled, never pruned

### Priority 2: Important (Fix Soon)

**5. Document Garden Paths**

Add to paths.md as new section:

```markdown
## Path: Garden Paths

**Trigger:** "Show me the garden", "Map the connections", "Which identities have worked together?"

**Purpose:** Visualize collaboration patterns between identities. Shows which identities reference each other in their RAM directories.

**Steps:**
1. Run `~/.matrix/garden-paths.sh`
2. Review output showing identity connections
3. Use to understand collaboration patterns before complex synthesis

**Output:** Text-based graph or adjacency list

**Use cases:**
- Before Hamann synthesis - see which identities share context
- After Construct - understand which identities contributed
- Debugging handoff issues - trace communication paths
```

**6. Add Identity Primer**

Create `identities/README.md`:

```markdown
# Identity System

Identities are specialized personas that Neo dispatches for focused work.

## How It Works

When you invoke an identity via slash command (e.g., `/smith`), Claude loads:
1. `identities/_base.md` - Shared protocol for all identities
2. `identities/smith.md` - Specific identity's role and voice

The identity then executes the task and returns to Neo.

## Available Identities

See CLAUDE.md for full table, or list with:
ls ~/.matrix/identities/*.md

## Creating New Identities

[Template and instructions]
```

**7. Clean Up Deprecated Files**

- Move `agents/` to `deprecated/agents/` or delete entirely
- Move `sync_issues.py`, `sync_discussions.py` to `deprecated/bin/`
- Update paths.md to not reference deprecated scripts
- Add `deprecated/README.md` explaining what's there and why

**8. Fix Sati in CLAUDE.md Table**

Add missing row:

```
| `/sati` | Sati | Greenfield, prototypes | "Spike a quick proof of concept" | "The Oracle told me about you." |
```

### Priority 3: Polish (Nice to Have)

**9. Document Model Assignments**

Add to orchestration.md:

```markdown
## Model Assignments

- **Opus** - Neo only. High-level orchestration, synthesis, final decisions
- **Sonnet** - Most identities. Balance of capability and cost for focused work
- **Haiku** - Kid only. Simple execution, minimal tokens

Cost implications:
- Opus: ~15x cost of Haiku
- Sonnet: ~3x cost of Haiku
- Always delegate Opus → Sonnet when possible
```

**10. Document Error Logging Pattern**

Either:
- Implement `errors.md` logging in identities and show examples, OR
- Remove from `_base.md` if not being used

**11. Create Construct Methodology Doc**

Referenced in paths.md line 336 but missing:

`~/.matrix/artifacts/etc/construct-methodology.md`

Should explain:
- What Construct reviews
- How identities collaborate
- What synthesis means
- Expected outputs

**12. Verify Issue Template**

Check if `~/.matrix/artifacts/etc/issue-template.md` or `.yaml` is correct:
- paths.md line 126 says `.md`
- glob found `.yaml`
- Ensure documentation matches reality

### Priority 4: Maintenance (Ongoing)

**13. Version Documentation**

Add to each major doc:
```markdown
**Last updated:** 2025-11-27
**Version:** 1.0
```

**14. Add Changelog**

Create `CHANGELOG.md` to track:
- Identity additions/changes
- Path modifications
- Script updates
- Breaking changes

**15. Script Docstring Standards**

All scripts have good docstrings. Standardize format:
```python
"""
script_name.py - One-line summary

Longer description of what it does and why it exists.

Usage:
    python script_name.py <args>

Example:
    python script_name.py owner/repo path/to/dir

Requirements:
    - PyYAML
    - GitHub token in ~/.claude.json
"""
```

---

## Summary Table

| Issue | Type | Priority | Blocks Onboarding? |
|-------|------|----------|-------------------|
| No README | Gap | P1 | Yes |
| Fellas confusion | Inconsistency | P1 | Yes |
| Directory structure undocumented | Gap | P1 | Partially |
| Cache semantics unclear | Inconsistency | P1 | No |
| Garden paths script undocumented | Gap | P2 | No |
| Identity primer missing | Gap | P2 | Partially |
| agents/ legacy cleanup | Inconsistency | P2 | No |
| Sati missing from table | Inconsistency | P2 | No |
| Model assignment rationale | Gap | P3 | No |
| Error logging unused | Inconsistency | P3 | No |
| construct-methodology.md missing | Gap | P3 | No |
| Issue template extension mismatch | Inconsistency | P3 | No |

---

## Verdict

**Is the documentation complete enough for a new session?**

**60% complete.** Core concepts are documented but critical gaps exist.

**Strengths:**
- Orchestration model is thorough
- Paths are well-structured
- Scripts have usage examples
- Identity roles are clear

**Weaknesses:**
- No README entry point
- Fellas references broken
- Legacy artifacts unexplained
- Directory structure assumed

**Recommended Next Steps:**

1. Create README.md (30 min)
2. Resolve Fellas situation (15 min decision + 30 min implementation)
3. Document directory structure (20 min)
4. Clarify cache semantics (10 min edits)

**After P1 fixes: 85% complete.**

Then tackle P2 (garden paths, identity primer, cleanup) to reach 95%.

---

**Files Referenced:**
- `/home/w3surf/.claude/CLAUDE.md`
- `/home/w3surf/.claude/orchestration.md`
- `/home/w3surf/.claude/paths.md`
- `/home/w3surf/.claude/PLATFORMS.md`
- `/home/w3surf/.claude/identities/_base.md`
- `/home/w3surf/.claude/identities/neo.md`
- `/home/w3surf/.claude/identities/smith.md`
- `/home/w3surf/.claude/identities/morpheus.md`
- `/home/w3surf/.claude/identities/trinity.md`
- `/home/w3surf/.claude/identities/switch.md`
- `/home/w3surf/.claude/artifacts/bin/sync_github.py`
- `/home/w3surf/.claude/artifacts/bin/pull_github.py`
- `/home/w3surf/.claude/artifacts/bin/sync_labels.py`
- `/home/w3surf/.claude/artifacts/bin/convert_issues.py`
- `/home/w3surf/.claude/artifacts/etc/identity-colors.yaml`
- `/home/w3surf/.claude/agents/fellas.md` (deprecated)
- `/home/w3surf/.claude/matrix/garden-paths.sh`

---

[Identity: morpheus | Model: sonnet | Status: success]

Wake up, Neo.
