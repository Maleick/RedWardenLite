# Roadmap: RedWardenLite Evolution

## Overview

v1.0 delivered the modernization baseline (contracts, parity, decomposition, hardening, observability). v1.1 focuses on operational maturity: hardened observability exposure, deployment templates, wider compatibility gates, and deeper incident runbooks.

## Milestones

- ✅ **v1.0 milestone** — Phases 1-5 shipped on 2026-02-25 ([archive roadmap](.planning/milestones/v1.0-ROADMAP.md), [archive requirements](.planning/milestones/v1.0-REQUIREMENTS.md))
- ✅ **v1.1 operational maturity** — Phases 6-8 shipped on 2026-02-26

## Phases

- [x] **Phase 6: Observability Access and Retention Hardening** - Add safe metrics exposure controls and production event lifecycle guidance (completed 2026-02-26)
- [x] **Phase 7: Deployment Templates and Compatibility Matrix** - Ship repeatable deployment paths and multi-version CI coverage (completed 2026-02-26)
- [x] **Phase 8: Operator Forensics and Runtime Override Refinement** - Add deep incident workflows and finer strict-mode safety controls (completed 2026-02-26)

## Phase Details

### Phase 6: Observability Access and Retention Hardening
**Goal**: Harden observability surfaces without breaking existing telemetry contracts.
**Depends on**: Phase 5
**Requirements**: OBSX-01, OBSX-02, OBSX-03
**Success Criteria** (what must be TRUE):
  1. Metrics endpoint access control is explicitly configurable and documented.
  2. Event retention/rotation guidance is contributor-usable and verified.
  3. Event sampling controls preserve stable schema and non-blocking behavior.
**Plans**: 2 plans

Plans:
- [x] 06-01: Metrics access controls and event sink lifecycle contract updates
- [x] 06-02: Sampling controls, runbook integration, and verification closure

### Phase 7: Deployment Templates and Compatibility Matrix
**Goal**: Make deployment and upgrade paths repeatable across supported environments.
**Depends on**: Phase 6
**Requirements**: DPLY-01, DPLY-02, CI-01
**Success Criteria** (what must be TRUE):
  1. Standard deployment templates are provided and validated.
  2. Upgrade smoke workflow is documented and executable.
  3. CI validates contract suites across supported Python versions.
**Plans**: 2 plans

Plans:
- [x] 07-01: Deployment template package (systemd + container baseline)
- [x] 07-02: Multi-version CI and upgrade smoke verification

### Phase 8: Operator Forensics and Runtime Override Refinement
**Goal**: Improve incident response depth and strict-mode operational ergonomics.
**Depends on**: Phase 7
**Requirements**: OPS-01, OPS-02, SECX-01, SECX-02
**Success Criteria** (what must be TRUE):
  1. Forensic runbook flows are deterministic and artifact-driven.
  2. Runtime unsafe override model supports finer-grained acknowledgement.
  3. Strict-mode remediation messages are complete and actionable.
**Plans**: 2 plans

Plans:
- [x] 08-01: Incident forensics workflow and evidence bundle procedure
- [x] 08-02: Runtime override granularity and remediation UX updates

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
