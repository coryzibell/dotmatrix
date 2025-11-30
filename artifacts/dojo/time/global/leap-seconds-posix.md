# Leap Seconds and POSIX Time

**Topic:** time
**Scope:** global
**Date:** 2025-11-30

## Knowledge

Leap seconds are irregular one-second adjustments to UTC to account for Earth's irregular rotation. Unlike leap years (predictable), they're announced by IERS only 6 months in advance. The last one: December 31, 2016 at 23:59:60 UTC.

POSIX time_t explicitly does NOT represent leap seconds - it assumes every day has exactly 86400 seconds. The `23:59:60` notation exists in ISO 8601 but not in POSIX time.

## Why It Matters

Real production incidents:
- **Cloudflare 2017 outage:** RRDTOOL assumed time always moves forward
- **Google uses "leap smear":** spreads extra second across 24 hours
- **AWS smears differently:** causes sync issues between providers
- Systems can crash, log negative time deltas, or break monotonic assumptions
- Can't predict when next one will be - depends on Earth's rotation

Ongoing debate about abolishing leap seconds entirely.

## Quiz Question

A distributed system logs event timestamps with microsecond precision. On December 31, 2016, engineers notice some events have timestamps like `2016-12-31T23:59:60.500000Z` in UTC. The system uses standard POSIX time_t internally. What is the most likely behavior when these timestamps are processed?

## Answer

Timestamps will either be rejected as invalid, converted to `2017-01-01T00:00:00.500000Z`, or cause time_t to temporarily appear to go backwards (same value twice). POSIX time_t has no representation for 23:59:60.
