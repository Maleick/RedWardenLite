# Roadmap: RedWardenLite Evolution

## Overview

This roadmap modernizes RedWardenLite in low-risk increments: lock externally visible behavior first, then evolve transport and internal architecture with parity guardrails, and finish with runtime hardening plus operational observability.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Contract Foundation** - Lock policy behavior with tests, CI gates, and runbook clarity (completed 2026-02-25)
- [x] **Phase 2: Async Transport Parity** - Introduce async upstream path with controlled parity checks (completed 2026-02-25)
- [x] **Phase 3: Policy Engine Decomposition** - Split redirector internals into testable maintainable modules (completed 2026-02-25)
- [x] **Phase 4: Runtime Hardening** - Add strict safety defaults and validation for secure operation (completed 2026-02-25)
- [x] **Phase 5: Observability Upgrade** - Deliver structured telemetry for incident response and tuning (completed 2026-02-25)

## Phase Details

### Phase 1: Contract Foundation
**Goal**: Establish behavior-lockdown as a hard gate for future refactors.
**Depends on**: Nothing (first phase)
**Requirements**: PLAT-01, PLAT-02, PLAT-03
**Success Criteria** (what must be TRUE):
  1. Policy reason-code contract tests are deterministic and pass in local and CI environments.
  2. CI enforces the contract suite on pushes and pull requests.
  3. Contributors can run and interpret behavior-lockdown checks from project docs.
**Plans**: 2 plans

Plans:
- [x] 01-01: Expand and stabilize policy reason-code contract matrix
- [x] 01-02: CI enforcement and test runbook integration

### Phase 2: Async Transport Parity
**Goal**: Introduce an async fetch path without changing external proxy behavior.
**Depends on**: Phase 1
**Requirements**: NET-01, NET-02, NET-03
**Success Criteria** (what must be TRUE):
  1. Async upstream path can be toggled by explicit configuration.
  2. Parity checks show no unacceptable divergence for status/header/body behavior.
  3. Operators can revert to legacy path via configuration-only rollback.
**Plans**: 3 plans

Plans:
- [x] 02-01: Add feature-flagged async fetch path scaffold
- [x] 02-02: Build parity comparison harness and baseline report
- [x] 02-03: Add rollback/operational guidance for transport switching

### Phase 3: Policy Engine Decomposition
**Goal**: Reduce coupling by separating policy checks and action logic while preserving behavior.
**Depends on**: Phase 2
**Requirements**: POL-01, POL-02, POL-03
**Success Criteria** (what must be TRUE):
  1. Redirector policy checks are extracted into smaller units with unchanged outcomes.
  2. Decision and action paths are independently testable.
  3. Existing plugin integration behavior remains backward compatible.
**Plans**: 3 plans

Plans:
- [x] 03-01: Extract policy-check modules with compatibility facade
- [x] 03-02: Separate decision/action flow and validate contracts
- [x] 03-03: Backward compatibility verification and cleanup

### Phase 4: Runtime Hardening
**Goal**: Enforce secure-by-default runtime behavior with explicit validation.
**Depends on**: Phase 3
**Requirements**: SEC-01, SEC-02, SEC-03
**Success Criteria** (what must be TRUE):
  1. Strict runtime profile enables safer defaults without breaking compatibility path.
  2. Unsafe bind/TLS combinations are rejected with actionable startup errors.
  3. Config validation catches conflicting security settings before runtime.
**Plans**: 2 plans

Plans:
- [x] 04-01: Implement strict profile enforcement toggles
- [x] 04-02: Add configuration validation and failure messaging

### Phase 5: Observability Upgrade
**Goal**: Make production behavior measurable and diagnosable without verbose debug dependence.
**Depends on**: Phase 4
**Requirements**: OBS-01, OBS-02, OBS-03
**Success Criteria** (what must be TRUE):
  1. Structured logs include stable outcome fields and reason codes.
  2. Metrics expose request volume, reason distributions, failures, and latency.
  3. Operators can diagnose incidents with telemetry and normal log verbosity.
**Plans**: 2 plans

Plans:
- [x] 05-01: Introduce structured event/log schema
- [x] 05-02: Add metrics emission and operational dashboard guide

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Contract Foundation | 2/2 | Complete    | 2026-02-25 |
| 2. Async Transport Parity | 3/3 | Complete   | 2026-02-25 |
| 3. Policy Engine Decomposition | 3/3 | Complete | 2026-02-25 |
| 4. Runtime Hardening | 2/2 | Complete | 2026-02-25 |
| 5. Observability Upgrade | 2/2 | Complete | 2026-02-25 |
