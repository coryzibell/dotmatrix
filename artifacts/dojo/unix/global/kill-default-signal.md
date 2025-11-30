# Kill Default Signal

**Topic:** unix
**Scope:** global
**Date:** 2025-11-30

## Knowledge

`kill` sends **SIGTERM (15)** by default, which politely asks the process to terminate and lets it clean up.

`kill -9` sends **SIGKILL** - the uncatchable, unblockable nuclear option. Processes can't trap or ignore it, so no cleanup happens.

## Why It Matters

- Always try SIGTERM first - it allows graceful shutdown
- SIGKILL (-9) is the last resort when a process won't respond
- Other useful signals: SIGHUP (1) for reload, SIGINT (2) for interrupt (Ctrl+C)

## Quiz Question

What Unix signal does `kill` send by default when you don't specify one?

## Answer

SIGTERM (signal 15).
