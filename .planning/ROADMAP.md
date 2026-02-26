# Roadmap: RedWardenLite Evolution

## Overview

v1.0 and v1.1 delivered a stable, operationally hardened proxy baseline. v2.0 focuses on scale-ready internals: plugin extensibility contracts and distributed fleet operations.

## Milestones

- ✅ **v1.0 milestone** — Phases 1-5 shipped on 2026-02-25 ([archive roadmap](.planning/milestones/v1.0-ROADMAP.md), [archive requirements](.planning/milestones/v1.0-REQUIREMENTS.md))
- ✅ **v1.1 operational maturity** — Phases 6-8 shipped on 2026-02-26 ([archive roadmap](.planning/milestones/v1.1-ROADMAP.md), [archive requirements](.planning/milestones/v1.1-REQUIREMENTS.md))
- 🚧 **v2.0 extensibility + distributed operations** — Phases 9-10 (in progress; Phase 9 complete)

## Phases

- [x] **Phase 9: Plugin Capability Contracts and Isolation Boundaries** - Formalize plugin compatibility metadata and strengthen plugin execution boundaries (completed 2026-02-26).
- [ ] **Phase 10: Distributed Policy Coordination and Fleet Telemetry** - Add multi-node policy convergence and centralized telemetry aggregation controls.

## Phase Details

### Phase 9: Plugin Capability Contracts and Isolation Boundaries
**Goal**: Make plugin integration safer and explicitly versioned without breaking current plugin-facing behavior.
**Depends on**: Phase 8
**Requirements**: EXT-01, EXT-02
**Success Criteria** (what must be TRUE):
  1. Plugin capability/version metadata is defined and validated deterministically at load time.
  2. Plugin isolation controls prevent boundary violations with explicit failure semantics.
  3. Compatibility and isolation contracts are covered by deterministic tests and CI hard gates.
**Plans**: 2 plans

Plans:
- [x] 09-01: Plugin capability metadata schema and compatibility validation path
- [x] 09-02: Plugin isolation boundary enforcement and contract verification

### Phase 10: Distributed Policy Coordination and Fleet Telemetry
**Goal**: Provide deterministic fleet-level policy coordination and telemetry aggregation foundations.
**Depends on**: Phase 9
**Requirements**: DIST-01, DIST-02
**Success Criteria** (what must be TRUE):
  1. Multi-node policy coordination converges deterministically and is verifiable.
  2. Fleet telemetry aggregation and retention controls are documented and test-verified.
  3. Operator runbooks include distributed incident and rollback-safe triage guidance.
**Plans**: 2 plans

Plans:
- [ ] 10-01: Distributed policy state coordination model and verification harness
- [ ] 10-02: Fleet telemetry aggregation contracts, retention controls, and runbook closure

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Contract Foundation | 2/2 | Complete | 2026-02-25 |
| 2. Async Transport Parity | 3/3 | Complete | 2026-02-25 |
| 3. Policy Engine Decomposition | 3/3 | Complete | 2026-02-25 |
| 4. Runtime Hardening | 2/2 | Complete | 2026-02-25 |
| 5. Observability Upgrade | 2/2 | Complete | 2026-02-25 |
| 6. Observability Access and Retention Hardening | 2/2 | Complete | 2026-02-26 |
| 7. Deployment Templates and Compatibility Matrix | 2/2 | Complete | 2026-02-26 |
| 8. Operator Forensics and Runtime Override Refinement | 2/2 | Complete | 2026-02-26 |
| 9. Plugin Capability Contracts and Isolation Boundaries | 2/2 | Complete | 2026-02-26 |
| 10. Distributed Policy Coordination and Fleet Telemetry | 0/2 | Not started | - |
