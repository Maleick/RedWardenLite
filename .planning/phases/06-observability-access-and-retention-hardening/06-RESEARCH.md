# Phase 6: Observability Access and Retention Hardening — Research Notes

## Goal

Harden observability surfaces introduced in Phase 5 without changing proxy decision semantics or request behavior.

## Existing Baseline

- Structured events are emitted to JSONL via `lib/observability.py` with best-effort writes.
- Prometheus metrics are exposed from `MetricsHandler` on configurable path (default `/metrics`).
- Event emission has no sampling control; every completed request is emitted when enabled.
- Metrics endpoint has no access policy beyond listener/network boundaries.
- CI includes an observability contract step running `tests/test_observability_contracts.py`.

## Requirement Mapping

### OBSX-01: Metrics access restriction via runtime config
- Add explicit access policy config for `/metrics` endpoint.
- Preserve current compatibility by default (`open` access mode).
- Enforce policy in `MetricsHandler` with deterministic allow/deny behavior.
- Add tests for `open`, `loopback`, and CIDR-based access evaluation.

### OBSX-02: Event sink lifecycle guidance and verification
- Keep event schema unchanged.
- Add contributor runbook sections for sink path management, retention, and rotation.
- Include explicit verification commands for sink behavior and file rotation checks.

### OBSX-03: Configurable schema-safe sampling
- Add deterministic sampling controls with default full emission (`rate=1.0`).
- Sampling decisions should be stable for identical event payloads.
- Never break required event fields or JSONL one-object-per-line contract.
- Keep metrics unsampled in this phase (event sampling only).

## Implementation Focus

- Extend `lib/observability.py` with:
  - metrics access policy evaluator (`open|loopback|cidr`)
  - deterministic event sampling predicate
- Extend config surface in `RedWardenLite.py` and `lib/optionsparser.py`:
  - `observability_metrics_access_mode`
  - `observability_metrics_allowed_cidrs`
  - `observability_events_sampling_rate`
- Enforce access policy in `lib/proxyhandler.py` `MetricsHandler.get`.
- Apply sampling gate in request event emission path before JSONL write.
- Expand `tests/test_observability_contracts.py` with access/sampling cases.

## Constraints

- No path/query labels in metrics.
- No request-path blocking from observability failures.
- Maintain existing policy/transport/runtime contracts.
- Keep defaults backward compatible.
