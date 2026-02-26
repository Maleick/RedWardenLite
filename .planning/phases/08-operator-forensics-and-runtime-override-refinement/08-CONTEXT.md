# Phase 8: Operator Forensics and Runtime Override Refinement - Context

**Gathered:** 2026-02-26
**Status:** Ready for planning

## Phase Boundary

Phase 8 improves operational response depth and strict-mode hardening ergonomics without changing proxy policy ordering, external plugin contracts, or request action semantics. Scope is limited to operator forensics workflows/evidence expectations and finer-grained strict-mode unsafe override acknowledgements plus remediation guidance.

## Implementation Decisions

### Incident Workflow Depth
- Add contributor-usable but operator-deep workflows for three incident classes:
  - policy outcome anomalies
  - transport/parity anomalies
  - observability pipeline anomalies
- Keep triage deterministic with a fixed sequence: stabilize service, collect evidence, classify incident, verify regression gates.

### Evidence Bundle Contract
- Define a deterministic evidence bundle procedure rooted at `artifacts/forensics/<case-id>/`.
- Bundle must include stable artifact categories:
  - runtime/config snapshot
  - policy/transport/observability command outputs
  - metrics snapshot and structured-event sample
  - verification command results
  - checksum manifest
- Document exact expected artifact names and commands so two contributors can produce equivalent bundles.

### Strict-Mode Unsafe Override Granularity
- Preserve existing global strict override gate (`runtime_hardening_allow_unsafe` + `runtime_hardening_unsafe_ack`).
- Add per-check acknowledgement semantics for strict-mode unsafe findings so each denied finding must be explicitly acknowledged.
- Keep strict startup behavior as hard-fail when required acknowledgement fields are missing or incomplete.

### Remediation UX Expectations
- Denied strict checks must continue to emit:
  - setting path
  - failure reason
  - safe replacement example
- Migration guidance must include explicit remediation examples for each denied strict check in scope.

### CI and Verification Posture
- Keep deterministic/offline tests and hard-fail CI semantics.
- Add explicit tests for:
  - forensics runbook/evidence procedure contract anchors
  - per-check unsafe acknowledgement enforcement
  - strict remediation guidance coverage

### Claude's Discretion
- Exact runbook section wording and artifact naming details, while preserving deterministic expectations.
- Internal helper function names for runtime hardening acknowledgement parsing/matching.
- Exact test fixture structure and assertion granularity.

## Deferred Ideas

- Automated evidence bundle packaging command/tooling.
- Risk-scored unsafe override policy with severity thresholds.
- Time-bound override expiration and automatic rollback orchestration.
- Remote incident evidence shipping/inventory pipeline.

---

*Phase: 08-operator-forensics-and-runtime-override-refinement*
*Context gathered: 2026-02-26*
