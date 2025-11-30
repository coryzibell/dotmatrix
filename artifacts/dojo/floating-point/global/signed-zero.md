# IEEE 754 Signed Zero

**Topic:** floating-point
**Scope:** global
**Date:** 2025-11-30

## Knowledge

IEEE 754 has two distinct representations of zero: +0 and -0. Both have exponent and mantissa of all zeros, distinguished only by the sign bit. While `(-0) == (+0)` returns true, they're different bit patterns.

## Why It Matters

- **Division behavior:** `1.0/+0` yields +∞, `1.0/-0` yields -∞
- **No exceptions:** IEEE 754 division by zero produces signed infinity, not errors
- **Preserves direction:** Maintains which "side" you approached zero from
- **Real applications:** Complex analysis, logarithms near zero, inverse trig functions, detecting underflow direction

## Quiz Question

In IEEE 754 floating point arithmetic, what is the result of `1.0 / -0.0`?

A) 0
B) Positive infinity (+∞)
C) Negative infinity (-∞)
D) NaN
E) Undefined behavior / runtime error

## Answer

C) Negative infinity (-∞). Division by zero produces signed infinity following the mathematical limit. Positive divided by negative zero yields -∞.
