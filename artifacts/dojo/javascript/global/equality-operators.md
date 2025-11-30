# JavaScript Equality Operators

**Topic:** javascript
**Scope:** global
**Date:** 2025-11-30

## Knowledge

`==` does type coercion before comparison, so `"5" == 5` is true.
`===` is strict equality - same value AND same type must match.

## Why It Matters

- Linters typically enforce `===` to avoid subtle bugs
- Type coercion rules are complex and unintuitive (`[] == false` is true)
- Use `===` unless you specifically need coercion

## Quiz Question

In JavaScript, what's the difference between `==` and `===`?

## Answer

`==` allows type coercion, `===` requires strict type and value equality.
