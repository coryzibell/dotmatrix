# Default TTL Values

**Topic:** networking
**Scope:** global
**Date:** 2025-11-30

## Knowledge

TTL (Time To Live) limits how many hops a packet can traverse before being discarded. Default values:

- **Linux/macOS:** 64
- **Windows:** 128
- **Some systems:** 255

Each router decrements TTL by 1. At 0, the packet is discarded and an ICMP "Time Exceeded" message is sent back to the source.

## Why It Matters

- Prevents routing loops from circulating packets forever
- `traceroute` exploits this: sends packets with TTL=1, 2, 3... and collects the "Time Exceeded" responses to map the path
- You can fingerprint operating systems by their TTL values (64 = likely Linux/Mac, 128 = likely Windows)
- Useful for debugging network issues

## Quiz Question

In networking, what's the maximum number of hops a packet can take before being discarded (assuming the default TTL value for most operating systems)?

## Answer

64 (Linux/macOS default). Windows uses 128.
