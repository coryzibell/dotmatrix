# Hash Collision Resistance

**Topic:** cryptography
**Scope:** global
**Date:** 2025-11-30

## Knowledge

Collision resistance is the property that makes it computationally infeasible to find two different inputs x₁ ≠ x₂ where H(x₁) = H(x₂).

Related properties:
- **Preimage resistance**: Can't reverse the hash to find the input
- **Second preimage resistance**: Given x₁, can't find x₂ that collides

## Why It Matters

- MD5 and SHA-1 are broken for collision resistance
- SHA-256 still holds
- Critical for digital signatures, certificates, and data integrity

## Quiz Question

In cryptography, what property does a hash function need to prevent finding two different inputs that produce the same output?

## Answer

Collision resistance.
