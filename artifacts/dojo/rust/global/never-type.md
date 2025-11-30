# The Never Type (!)

**Topic:** rust
**Scope:** global
**Date:** 2025-11-30

## Knowledge

The **`!`** type (called the "never type") indicates a function that never returns. Used as the return type for functions that:

- Always panic
- Contain infinite loops
- Always call `std::process::exit()`

```rust
fn forever() -> ! {
    loop {}
}

fn die(msg: &str) -> ! {
    panic!("{}", msg);
}
```

## Why It Matters

- Helps the compiler with control flow analysis
- `!` can coerce to any type, which is why `panic!` works in any context
- Enables exhaustive match arms: `let x = match val { Some(v) => v, None => panic!() };`
- Currently unstable as a standalone type (`#![feature(never_type)]`), but stable in return position

## Quiz Question

In Rust, what keyword do you use to indicate that a function might not return (like `panic!` or an infinite loop)?

## Answer

The `!` type (the "never type"), written as `fn foo() -> !`.
