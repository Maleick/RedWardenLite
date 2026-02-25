# Phase 5: Observability Upgrade — Research Notes

## Goal

Deliver operational observability that works under normal verbosity: structured request events, low-cardinality metrics, and contributor triage guidance.

## Existing Observability Baseline

- Human-readable request/response log lines exist in `lib/proxyhandler.py`.
- Access log supports apache2 and redelk text formats.
- Transport parity emits dedicated JSONL + Markdown artifacts in `artifacts/parity/`.
- No global structured request-event schema currently exists.
- No runtime `/metrics` endpoint currently exists.

## Locked Decisions to Encode

1. Structured event contract
- one summary event per completed request
- required fields: timestamp/method/path/status/action/reason/duration_ms/transport_mode/runtime_profile
- path only by default (no query)
- plain logs retained + JSONL events added

2. Metrics contract
- request totals
- outcome/reason counts
- upstream failure counts
- request latency histogram
- low-cardinality labels only

3. Export behavior
- event sink: configurable JSONL file with enable flag
- metrics exposure: Prometheus text on `/metrics`
- best-effort emission (failures never block request path)

4. Ops posture
- enabled by default
- contributor-first runbook
- CI hard-fail observability contracts on push + pull_request

## Integration Focus

- Add observability helper module for event emission and in-process metrics registry rendering.
- Hook event/metric recording into request completion path.
- Add `/metrics` route ahead of catch-all routes.
- Add deterministic tests for schema/metrics/endpoint/failure resilience.

## Constraints

- Preserve existing proxy external behavior and policy semantics.
- No path/query-cardinality explosion in metrics labels.
- Keep telemetry non-blocking and safe in normal operation.
