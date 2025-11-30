# Program: Dojo

**Trigger:** "dojo [topic] [scope]", "quiz me", "teach me"

*"I know kung fu."* — Neo

**Purpose:** Learn something new, get quizzed on it. Spaced repetition through random knowledge retrieval.

**Input:**
- `topic` - Any subject (e.g., "rust", "simd", "geohash", "cryptography"). If omitted, pick something completely random.
- `scope` - Where to find knowledge (default: `global`):
  - `global` - Model knowledge + internet research
  - `local` - Our projects, codebases, Zion knowledge base

**Output:** A quiz question, then feedback

## Steps

### Phase 1: Find Knowledge

1. **Neo dispatches Tank** to find a random, interesting fact about `[topic]` within `[scope]`:

   **Global scope:**
   - Model's training knowledge
   - Web search for current/detailed info
   - Look for non-obvious facts, edge cases, gotchas, history

   **Local scope:**
   - Search Zion (`~/.matrix/zion/`)
   - Search project codebases (`~/work/personal/code/`)
   - Search RAM notes (`~/.matrix/ram/`)
   - Search artifacts (`~/.matrix/artifacts/`)
   - Look for patterns we've learned, bugs we've fixed, decisions we've made

2. **Tank returns** with:
   - The fact/knowledge
   - Why it's interesting or useful
   - A good quiz question about it

### Phase 2: Quiz (BEFORE recording)

3. **Neo asks** the quiz question to kautau
   - Hold the knowledge in context - DO NOT write to file yet (kautau can see file writes!)
   - Present just the question, no hints
   - Wait for response

### Phase 3: Evaluate

4. **Neo evaluates** the answer:
   - **Correct (or close enough):** Brief acknowledgment, explain why it's right if there's nuance. Record win.
   - **Incorrect:** Brief "nope", then explain the correct answer concisely. Record loss.
   - **Draw:** If the question was ambiguous, own it. Record draw.

   Keep it tight - no Matrix quotes, no fluff.

### Phase 4: Record Knowledge (AFTER quiz)

5. **Neo saves** the knowledge to:
   ```
   ~/.matrix/artifacts/dojo/[topic]/[scope]/[title_summary].md
   ```

   Format:
   ```markdown
   # [Title]

   **Topic:** [topic]
   **Scope:** [scope]
   **Date:** [date]

   ## Knowledge

   [The fact/concept explained]

   ## Why It Matters

   [Context, use cases, gotchas]

   ## Quiz Question

   [The question]

   ## Answer

   [The answer]
   ```

### Phase 5: Update Score

6. **Update score** at `~/.matrix/artifacts/dojo/score.md`

### Phase 6: Continue

7. **Immediately ask another question** - keep the dojo session going until kautau says to stop. No need to ask "another?" - just hit them with the next one.
   ```markdown
   # Dojo Score

   **Wins:** X
   **Losses:** Y
   **Win Rate:** Z%

   ## Recent

   | Date | Topic | Scope | Result |
   |------|-------|-------|--------|
   | ... | ... | ... | W/L/D |
   ```

## Examples

```
/load dojo rust global
→ Tank finds: "Rust's orphan rule prevents implementing foreign traits on foreign types"
→ Quiz: "What Rust rule prevents you from implementing Display for Vec<T> in your own crate?"
→ kautau: "orphan rule"
→ Nice. Wins: 1

/load dojo simd local
→ Tank finds: "We hit a pshufb LUT overflow bug in geohash - 16-byte LUT can't handle 22 compressed indices"
→ Quiz: "What was the root cause of the geohash SIMD bug we fixed in base-d?"
→ kautau: "the lookup table was too small"
→ Nice. Wins: 2

/load dojo cryptography global
→ Tank finds: "AES's SubBytes step uses a multiplicative inverse in GF(2^8)"
→ Quiz: "What mathematical operation is at the core of AES's SubBytes substitution?"
→ kautau: "xor?"
→ Not quite. SubBytes uses the multiplicative inverse in the Galois field GF(2^8). Losses: 1
```

## Directory Structure

```
~/.matrix/artifacts/dojo/
├── score.md
├── rust/
│   ├── global/
│   │   ├── orphan-rule.md
│   │   └── pin-unpin.md
│   └── local/
│       └── edition-2024-unsafe.md
├── simd/
│   ├── global/
│   │   └── pshufb-lut-limits.md
│   └── local/
│       └── geohash-lut-overflow.md
└── cryptography/
    └── global/
        └── aes-subbytes-galois.md
```

## Key Rules

- Keep questions focused - one concept per quiz
- Prefer non-obvious knowledge over basics
- Local scope prioritizes things we've actually encountered
- Be generous with "close enough" - understanding matters more than exact wording
- Track score honestly - losses are learning opportunities
- **Re-read this program after every file write** - context drift is real, don't forget to record knowledge
