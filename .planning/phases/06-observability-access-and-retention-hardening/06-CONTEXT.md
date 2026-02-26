# Phase 6: Observability Access and Retention Hardening - Context

**Gathered:** 2026-02-26
**Status:** Ready for planning

## Phase Boundary

Phase 6 hardens observability operations introduced in Phase 5 without changing policy decision semantics or request/response behavior. Scope is restricted to metrics access controls, event sink lifecycle guidance, and schema-safe sampling controls.

## Implementation Decisions

### Metrics Access Control
- Add explicit runtime controls for metrics endpoint exposure suitable for production.
- Default compatibility remains unchanged for existing installs unless strict observability controls are enabled.
- Access policy must be deterministic and testable (allow/deny criteria documented).

### Event Sink Lifecycle
- Keep JSONL schema unchanged from Phase 5.
- Provide explicit runbook guidance for retention and rotation (contributor-first).
- Sink write failures remain best-effort and must never block request processing.

### Event Sampling
- Sampling is configuration-driven and optional.
- Sampling must preserve required fields and one-line JSON object structure.
- Sampling behavior must be deterministic for tests (seeded or explicit threshold logic).

### Verification and CI
- Add dedicated contract tests for access controls and sampling behavior.
- Keep CI hard-fail posture on push and pull_request.
- Maintain compatibility with existing policy/transport/runtime contract suites.

### Claude's Discretion
- Specific naming for flags/options and helper functions.
- Test fixture structure and deterministic sampling strategy.
- Runbook wording and section order.

## Deferred Ideas

- Full authn/authz service integration for metrics exposure.
- Distributed event shipping pipeline.
- Dynamic sampling controlled by runtime feedback loops.

---

*Phase: 06-observability-access-and-retention-hardening*
*Context gathered: 2026-02-26*
