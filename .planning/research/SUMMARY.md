# Project Research Summary

**Project:** RedWardenLite Evolution
**Date:** 2026-02-25

## Executive Summary

The strongest path for this milestone is incremental brownfield hardening: lock behavior contracts, improve observability and safety defaults, then evolve transport and architecture behind parity protections. The existing code already delivers core proxy value, so roadmap quality depends on reducing regression risk while modernizing internal structure.

## Key Findings

### Recommended Stack

- Keep Python/Tornado runtime intact for compatibility.
- Treat pytest contracts + CI as first-order platform dependencies.
- Add minimal observability support (structured events + metrics) before deeper refactors.

### Expected Features

- Stable reason-code policy outcomes with test coverage
- Async upstream parity path behind feature flag
- Strict runtime profile + config validation
- Incremental policy-engine modularization

### Architecture Approach

- Maintain plugin facade contract (`ProxyPlugin`) and extract internals gradually.
- Separate policy decisions from action side effects.
- Roll out risky transport changes with parity instrumentation, not big-bang replacement.

### Critical Pitfalls

- Refactoring before behavior lockdown
- Async migration without output parity checks
- Hardening features that are optional but undocumented

## Implications for Roadmap

### Phase 1: Contract Foundation

Lock policy behavior, stabilize CI regression gates, and document expected reason semantics.

### Phase 2: Transport Safety Upgrade

Introduce async upstream path behind flag with parity checks and rollback safety.

### Phase 3: Runtime Hardening + Observability

Add strict safety defaults, config validation, and operational telemetry.

### Phase Ordering Rationale

Contracts first lowers risk for every subsequent change. Transport and architecture updates then become measurable and reversible.

### Research Flags

- Potential contention between file-backed state and higher-concurrency transport.
- Existing global state patterns require careful extraction strategy.

## Confidence Assessment

- **High confidence:** behavior-lockdown-first ordering, need for CI gates, and strict profile benefits.
- **Medium confidence:** exact extraction boundaries for redirector modules (depends on implementation details).
- **Medium confidence:** async path performance gains in all deployment profiles.

### Gaps to Address

- Collect baseline latency/error metrics before transport changes.
- Define final metrics schema for drop reasons and upstream failures.

## Sources

### Primary (HIGH confidence)

- `.planning/codebase/*.md`
- `idea.md`
- Existing repository code (`lib/`, `plugins/`)

### Secondary (MEDIUM confidence)

- Tornado docs: https://www.tornadoweb.org/
- Requests docs: https://requests.readthedocs.io/

### Tertiary (LOW confidence)

- Broader industry comparisons (implementation details vary by environment)
