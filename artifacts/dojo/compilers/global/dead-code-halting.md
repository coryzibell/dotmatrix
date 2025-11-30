# Dead Code Elimination and the Halting Problem

**Topic:** compilers
**Scope:** global
**Date:** 2025-11-30

## Knowledge

Dead code elimination can't be 100% accurate because determining if a code path is truly unreachable is equivalent to solving the halting problem. To prove code never executes, you'd need to prove certain conditions can never be true - which requires knowing if preceding code halts and with what values.

## Why It Matters

- Explains why `-Wunreachable-code` warnings can be both overly aggressive AND miss obvious cases
- Shows how fundamental CS theory (Turing, 1936) constrains modern tooling
- Rust's borrow checker hits similar undecidability boundaries - conservative because perfect precision is mathematically impossible
- Lint tools and static analyzers are "best effort" by necessity, not laziness

## Quiz Question

Why can't a compiler's dead code elimination be 100% accurate?

A) Too much memory needed
B) Different processors execute differently
C) Equivalent to solving the halting problem
D) Compilers prioritize speed over accuracy

## Answer

C) Halting problem. Proving code is unreachable requires proving conditions can never be true, which requires knowing if code halts with what values - undecidable.
