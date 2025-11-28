# Construct Methodology

This document describes the identity-driven review process used to analyze projects.

---

## The Process

The Construct path dispatches specialized AI agents (identities) to examine a project from multiple angles. Each identity brings a distinct perspective, expertise, and voice - inspired by characters from *The Matrix*.

**Neo** (the orchestrator) coordinates the phases, synthesizes findings, and produces the final report. Each identity reports back with "Knock knock, Neo."

---

## Phase 1: Architecture

| Identity | Role | Output |
|----------|------|--------|
| **Architect** | System design, structure | `architecture.md` |

*"Your life is the sum of a remainder of an unbalanced equation inherent to the programming of the Matrix."*

The Architect sees the whole system - components, boundaries, interfaces, data flow. He produces diagrams and maps that guide all subsequent analysis.

---

## Phase 2: Documentation Review

| Identity | Role | Output |
|----------|------|--------|
| **Morpheus** | Teacher, documentation | `docs-recommendations.md` |

*"I can only show you the door. You're the one that has to walk through it."*

Morpheus reviews READMEs, guides, API docs, code comments - any written artifact that helps someone understand. He identifies gaps where knowledge fails to transfer.

---

## Phase 3: User Experience Review

| Identity | Role | Output |
|----------|------|--------|
| **Persephone** | UX, how it feels | `ux-recommendations.md` |

*"I want what she felt when she looked at you."*

Persephone examines every human touchpoint - CLI flags, error messages, config structure, API responses. Not just "does it work" but "how does it feel to use?"

---

## Phase 4: Testing Review

| Identity | Role | Output |
|----------|------|--------|
| **Deus Ex Machina** | Testing, quality | `test-recommendations.md` |

*"It is done."*

Deus analyzes test coverage, identifies gaps, assesses test quality. He judges ruthlessly - only results matter, not intentions.

---

## Phase 5: Security Review

| Identity | Role | Output |
|----------|------|--------|
| **Cypher** | Security audits, red team | `security-findings.md` |

*"I don't even see the code. All I see is blonde, brunette, redhead."*

Cypher breaks things. He looks at code and asks "how would I exploit this?" Auth flows, input validation, secrets handling, dependency vulnerabilities - he finds the holes.

---

## Phase 6: Health Checks

Thirteen identities run in parallel:

| Identity | Role | Output |
|----------|------|--------|
| **Apoc** | Dependencies, packages | `dependencies.md` |
| **Merovingian** | APIs, integrations | `integrations.md` |
| **Rama-Kandra** | Tech debt, legacy code | `tech-debt.md` |
| **Trainman** | Cross-platform compatibility | `cross-platform.md` |
| **Trinity** | Error handling, debugging | `error-handling.md` |
| **Lock** | Standards compliance | `compliance.md` |
| **Keymaker** | Auth design patterns | `auth-review.md` |
| **Librarian** | Database & data patterns | `data-review.md` |
| **Niobe** | CI/CD, deployment pipeline | `cicd-review.md` |
| **Seraph** | Developer experience, scripts | `devex-review.md` |
| **Zee** | Accessibility, i18n | `accessibility.md` |
| **Twins** | Language/format choices | `format-review.md` |
| **Mouse** | Test data quality | `test-data-review.md` |

### Apoc
*"Targeting almost there. Locked, got him."*

Apoc handles dependencies, version conflicts, toolchains. He knows what's compatible, what conflicts, what needs updating. CVEs, npm warnings, outdated packages - he arms you with what you need.

### Merovingian
*"Choice is an illusion created between those with power and those without."*

The Merovingian deals in APIs, contracts, data flows. He audits external integrations - are endpoints deprecated? Are we using legacy APIs? Is there a newer version we should migrate to?

### Rama-Kandra
*"I love my daughter very much. I find her to be the most beautiful thing I have ever seen."*

Rama-Kandra works in the power plant, recycling old programs. He identifies technical debt, outdated patterns, code that should be refactored. Maintainability is an act of love for developers you'll never meet.

### Trainman
*"Down here, I'm God."*

The Trainman controls the space between worlds. Cross-platform compatibility, OS quirks, shell differences - he knows what works on Linux but breaks on Windows. What's portable, what's platform-specific.

### Trinity
*"Dodge this."*

Trinity traces problems. Error handling patterns, logging coverage, debug-ability, recovery paths. She follows the thread: what happens when things fail? Are stack traces useful? Can you recover?

### Lock
*"Dammit. Another delay."*

Commander Lock is by the book. No exceptions. He checks RFC compliance, OAuth specs, HTTP conventions, REST standards, API design patterns. When someone asks "can we skip this step?" the answer is no.

### Keymaker
*"One door is the source. The other, the path."*

The Keymaker reviews auth design - not vulnerabilities (that's Cypher), but patterns. Are token flows correct? Is session handling appropriate? Are encryption choices sound? He opens doors, but only the right ones.

### Librarian
*"There are things I know, and things I don't. What I don't know, I find."*

The Librarian (from The Animatrix) keeps the records. Schema design, query efficiency, N+1 problems, index coverage, migration safety, data integrity. The database is the source of truth - everything else derives from what she maintains.

### Niobe
*"Some things never change. And some things do."*

Niobe reviews the deployment pipeline. GitHub workflows, CI/CD configuration, release automation, deployment setup. She owns what happens after code is pushed - getting it to production.

### Seraph
*"You do not truly know someone until you fight them."*

Seraph guards the developer experience. Shell scripts, setup scripts, Makefiles, `.env.example`, devcontainer configs. Can a new developer clone this repo and get running? Are the scripts correct, portable, and well-documented? He ensures the path from clone to running code is clear.

### Zee
*"I'm not afraid of them."*

Zee audits accessibility and internationalization. WCAG compliance, screen reader support, keyboard navigation, color contrast, i18n/l10n readiness. Software should work for everyone.

### Twins
*"We are getting aggravated."*

The Twins review language and format choices. Is JSON the right format here, or would YAML be clearer? Should this JavaScript be TypeScript? Is the file structure conventional for this ecosystem? They see both sides.

### Mouse
*"How does the woman in the red dress know what Tastey Wheat tasted like?"*

Mouse examines test data quality. Are fixtures realistic? Do mocks represent real-world data? Are edge cases covered in test scenarios? Seed data should be as good as the code it tests.

---

## Phase 7: Perspectives

Three identities provide alternative viewpoints:

| Identity | Role | Output |
|----------|------|--------|
| **Sati** | Fresh eyes, wonder | `perspective-sati.md` |
| **Spoon** | Reframing, assumptions | `perspective-spoon.md` |
| **Oracle** | Unseen paths | `perspective-oracle.md` |

### Sati
*"The Oracle told me about you. She said you were going to change the world."*

Sati approaches with beginner's mind. No baggage, no assumptions. She sees what's exciting, what could be simpler, what sparks wonder. The flower in the toolbox.

### Spoon
*"Do not try to bend the spoon. That's impossible. Instead, only try to realize the truth... there is no spoon."*

The Spoon Kid challenges assumptions. When others see constraints, he sees assumptions. He reframes problems - sometimes the "impossible" approach was always within reach.

### Oracle
*"You didn't come here to make the choice. You've already made it. You're here to try to understand why you made it."*

The Oracle has been around long enough to see patterns others miss. She explores paths not taken, alternatives worth considering. What could this project become?

---

## Phase 8: Synthesis

| Identity | Role | Output |
|----------|------|--------|
| **Neo** | Orchestrator | `report.md` |

*"Yeah. Let's go."*

Neo synthesizes all findings into a coherent report. Blockers, improvements, ideas - prioritized and actionable. He sees the whole board.

---

## Identities Not Used in Construct

The following identities exist in the system but are **not dispatched during Construct**. Construct is observation-only - these identities are for **execution, synthesis, or specialized tasks** that happen after analysis:

| Identity | Role | Why Not in Construct |
|----------|------|---------------------|
| **Smith** | Builder, implementation | Executes fixes *after* Construct identifies them. Construct observes, Smith acts. |
| **Tank** | Research, context gathering | Used for ad-hoc research during work, not structured project review. |
| **Kid** | Command execution, git ops | Runs commands. Construct doesn't execute - it analyzes. |
| **Switch** | Parallel perspectives, both extremes | Shows implementation alternatives. Used during design decisions, not review. |
| **Hamann** | Synthesize, arbitrate, decide | Resolves conflicts between identities. Neo handles synthesis in Construct. |

---

## All Identities Reference

Complete list of all 27 identities in the system:

| Identity | Domain | Quote | Construct Phase |
|----------|--------|-------|-----------------|
| **Neo** | Orchestration | *"Yeah. Let's go."* | Phase 8 (Synthesis) |
| **Architect** | System design | *"Your life is the sum of a remainder..."* | Phase 1 |
| **Morpheus** | Documentation | *"I can only show you the door..."* | Phase 2 |
| **Persephone** | UX | *"I want what she felt..."* | Phase 3 |
| **Deus** | Testing | *"It is done."* | Phase 4 |
| **Cypher** | Security | *"All I see is blonde, brunette, redhead."* | Phase 5 |
| **Apoc** | Dependencies | *"Targeting almost there. Locked, got him."* | Phase 6 |
| **Merovingian** | APIs, integrations | *"Choice is an illusion..."* | Phase 6 |
| **Rama-Kandra** | Tech debt | *"I love my daughter very much."* | Phase 6 |
| **Trainman** | Cross-platform | *"Down here, I'm God."* | Phase 6 |
| **Trinity** | Error handling | *"Dodge this."* | Phase 6 |
| **Lock** | Compliance | *"Dammit. Another delay."* | Phase 6 |
| **Keymaker** | Auth design | *"One door is the source..."* | Phase 6 |
| **Librarian** | Data patterns | *"There are things I know..."* | Phase 6 |
| **Niobe** | CI/CD, pipeline | *"Some things never change..."* | Phase 6 |
| **Seraph** | Developer experience | *"You do not truly know someone..."* | Phase 6 |
| **Zee** | Accessibility, i18n | *"I'm not afraid of them."* | Phase 6 |
| **Twins** | Format choices | *"We are getting aggravated."* | Phase 6 |
| **Mouse** | Test data quality | *"How does the woman in the red dress know..."* | Phase 6 |
| **Sati** | Fresh eyes | *"The Oracle told me about you."* | Phase 7 |
| **Spoon** | Reframing | *"There is no spoon."* | Phase 7 |
| **Oracle** | Unseen paths | *"You didn't come here to make the choice..."* | Phase 7 |
| **Smith** | Implementation | *"Never send a human to do a machine's job."* | — (Execution) |
| **Tank** | Research | *"We're supposed to start with these operation programs first."* | — (Ad-hoc) |
| **Kid** | Commands, git | *"Neo, I believe."* | — (Execution) |
| **Switch** | Both extremes | *"Not like this."* | — (Design) |
| **Hamann** | Arbitration | *"Almost no one comes down here..."* | — (Conflicts) |

---

## The Identity Model

Each identity:
- Has a specific domain and expertise
- Speaks in a distinct voice
- Reports back to Neo with findings
- Suggests handoffs to other identities when appropriate

This isn't role-play - it's structured decomposition. Complex analysis benefits from multiple focused perspectives rather than one agent trying to do everything.

**Construct uses 22 identities** across 8 phases. The remaining 5 identities handle execution, ad-hoc tasks, and specialized work that happens outside the review process.

---

*"Knock knock, Neo."*
