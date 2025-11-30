# Program: Vase

**Trigger:** `/load vase [context]`, "don't worry about the vase"

*"Don't worry about the vase."* — Oracle
*"What vase?"* — Neo

Seed the void with entropy. Three minds, zero constraints, full creativity.

## Agents

- **Spoon** - Reframe, dissolve problems. Sees it differently.
- **Oracle** - Exploration, alternatives. Shows paths.
- **Sati** - Greenfield, prototypes, wonder. The flower.

## On Load

### If context provided:
Pass exactly what was given. No additional framing.

### If no context:
Each agent picks something at random. Full freedom.

## Execution Flow

All artifacts stored in `~/.matrix/artifacts/vase/[context-slug]/`

### Round 1: Genesis
Dispatch all three in parallel:
```
[Agent]. [context or "pick something at random"]

Create whatever kind of artifact you want. Format, medium, style - your choice.
No constraints. Full creativity.
```

Store: `r1-spoon.md`, `r1-oracle.md`, `r1-sati.md`

### Round 2: Cross-pollination
Each agent receives the other two's work. Dispatch in parallel:
```
[Agent]. Here's what the others created:

[Spoon's artifact]
[Oracle's artifact]
[Sati's artifact]

Provide your feedback on the other two. What do you see? What resonates? What's missing?
```

Store: `r2-spoon-feedback.md`, `r2-oracle-feedback.md`, `r2-sati-feedback.md`

### Round 3: Iteration
Each agent receives all feedback. Dispatch in parallel:
```
[Agent]. Here's feedback on your work:

From Oracle: [feedback]
From Sati: [feedback]
(or whichever two didn't create it)

Iterate. Create your next version based on what resonated.
```

Store: `r3-spoon.md`, `r3-oracle.md`, `r3-sati.md`

### Round 4: Final feedback
Each agent reviews the other two's iterated work. Dispatch in parallel:
```
[Agent]. Here's the evolved work from the others:

[Agent A's r3 artifact]
[Agent B's r3 artifact]

Final thoughts. What landed? What emerged?
```

Store: `r4-spoon-feedback.md`, `r4-oracle-feedback.md`, `r4-sati-feedback.md`

### Round 5: Final artifacts
Each agent receives final feedback. Dispatch in parallel:
```
[Agent]. Final feedback on your work:

From Oracle: [feedback]
From Sati: [feedback]

Create your final artifact.
```

Store: `r5-spoon-final.md`, `r5-oracle-final.md`, `r5-sati-final.md`

### Synthesis
Create `synthesis.md` combining:
- The journey (how each evolved)
- The three final artifacts
- Emergent patterns across all three
- What the void returned

## Rules

- **No assumptions** - Pass exactly what's given, nothing more
- **No steering** - Let them go where they go
- **Full parallel** - All agents work simultaneously each round
- **Store everything** - The journey matters as much as the destination
- **Entropy is the point** - We're seeding the void, not seeking answers
