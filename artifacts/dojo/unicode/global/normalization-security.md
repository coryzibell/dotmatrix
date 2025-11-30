# Unicode Normalization Security

**Topic:** unicode
**Scope:** global
**Date:** 2025-11-30

## Knowledge

Unicode has multiple ways to represent the same visual character. For example, "é" can be:
- A single codepoint: U+00E9 (LATIN SMALL LETTER E WITH ACUTE)
- Two codepoints: U+0065 (e) + U+0301 (COMBINING ACUTE ACCENT)

These are visually identical but have different byte representations. Unicode defines four normalization forms (NFC, NFD, NFKC, NFKD) to handle this. Most programming languages and databases compare strings byte-by-byte, NOT after normalization.

## Why It Matters

Real security vulnerabilities:
- **Authentication bypass:** username "café" (NFC) and "café" (NFD) might be different accounts in DB but look identical
- **File system exploits:** macOS (HFS+) normalizes to NFD, Windows uses NFC - files can "disappear" across platforms
- **Validation bypass:** URL filters checking for `../` might miss normalized equivalents
- **Deduplication failures:** payment systems might process same transaction twice

Has caused real CVEs in Spring, Apache Commons, etc.

## Quiz Question

A web application validates usernames must be unique by checking `SELECT COUNT(*) FROM users WHERE username = ?`. The database uses case-sensitive UTF-8 collation with no normalization. A user registers as "café" (U+00E9). What happens if someone tries to register "café" (U+0065 U+0301)?

## Answer

Registration succeeds - two separate accounts exist. The database performs byte-level comparison without normalization. Fix: normalize to NFC before storage or use Unicode-aware collation.
