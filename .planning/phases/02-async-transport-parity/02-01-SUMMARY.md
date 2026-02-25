---
phase: 02-async-transport-parity
plan: 01
subsystem: transport-runtime
tags: [transport, async, config]
provides: [transport mode selection, async fallback scaffold]
affects: [lib/proxyhandler.py, RedWardenLite.py, lib/optionsparser.py]
tech-stack:
  added: [lib/transport_runtime.py]
  patterns: [explicit transport mode resolution, request-level fallback]
key-files:
  created: [lib/transport_runtime.py, tests/test_transport_runtime.py]
  modified:
    - RedWardenLite.py
    - lib/optionsparser.py
    - lib/proxyhandler.py
    - example-config.yaml
key-decisions:
  - Keep legacy as default mode
  - Auto mode only active when explicitly configured
patterns-established: [transport mode config contract]
duration: 22min
completed: 2026-02-25
---

# Phase 2: async-transport-parity Summary

**Introduced transport-mode selection with safe legacy default and async request-level fallback scaffold.**

## Performance
- **Duration:** 22min
- **Tasks:** 3 completed
- **Files modified:** 6

## Accomplishments
- Added runtime transport configuration surface (`legacy|async|auto`) with default-safe behavior.
- Added request-level async fallback path that logs structured fallback reason and continues via legacy path.
- Wired transport selection into proxy upstream fetch flow while preserving baseline legacy semantics.
- Added deterministic transport-runtime tests for mode resolution and fallback behavior.

## Task Commits
1. **Task 1-3: transport mode and fallback scaffold** - `a5310a9`

## Files Created/Modified
- `lib/transport_runtime.py` - transport mode normalization, auto selection, and fallback execution helpers.
- `tests/test_transport_runtime.py` - deterministic mode/fallback tests.
- `RedWardenLite.py` - transport defaults in runtime options.
- `lib/optionsparser.py` - transport/parity config argument and path handling support.
- `lib/proxyhandler.py` - transport-aware upstream fetch integration.
- `example-config.yaml` - operator-facing transport config examples.

## Decisions & Deviations
No deviations from scope. Async path is scaffolded without changing default legacy behavior.

## Next Phase Readiness
Parity comparator and shadow reporting can now plug into explicit primary transport selection logic.
