# TCP SYN Cookies

**Topic:** networking
**Scope:** global
**Date:** 2025-11-30

## Knowledge

SYN cookies are a technique to defend against SYN flood attacks without allocating server resources during the TCP handshake. Instead of storing connection state when receiving a SYN packet, the server encodes the state into the initial sequence number (ISN) it sends back in the SYN-ACK.

The "cookie" encodes:
- A timestamp (for timeout)
- The MSS (Maximum Segment Size) from the client
- A cryptographic hash of the connection tuple

When the client completes the handshake with an ACK, the server can reconstruct the connection state from the acknowledgment number (which is cookie + 1).

## Why It Matters

- Defense against SYN flood DDoS attacks
- No memory allocation until handshake completes
- Tradeoff: loses some TCP options (window scaling, SACK) since they can't be encoded in 32 bits
- Enabled by default in Linux when SYN queue overflows (`net.ipv4.tcp_syncookies`)

## Quiz Question

In TCP SYN cookies, where does the server encode the connection state to avoid allocating memory during a SYN flood?

## Answer

In the Initial Sequence Number (ISN) of the SYN-ACK packet.
