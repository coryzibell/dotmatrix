# Max Signed 32-bit Integer

**Topic:** computing
**Scope:** global
**Date:** 2025-11-30

## Knowledge

**2,147,483,647** (2³¹ - 1) is the maximum value of a signed 32-bit integer.

Quick reference:
- i8: 127 (2⁷ - 1)
- i16: 32,767 (2¹⁵ - 1)
- i32: 2,147,483,647 (2³¹ - 1) ~2.1 billion
- i64: 9,223,372,036,854,775,807 (2⁶³ - 1) ~9.2 quintillion

For unsigned, double the range (no sign bit):
- u16: 65,535 (2¹⁶ - 1)
- u32: 4,294,967,295 (2³² - 1) ~4.3 billion

## Why It Matters

- Classic interview question
- Explains why early systems had "year 2038 problem" (Unix timestamps are signed 32-bit)
- YouTube hit this limit with Gangnam Style views
- Know your bounds to avoid overflow bugs

## Quiz Question

What's the maximum value of a signed 32-bit integer?

## Answer

2,147,483,647 (2³¹ - 1, approximately 2.1 billion).
