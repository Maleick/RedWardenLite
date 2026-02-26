# Observability Upgrade Runbook

## Purpose

Phase 5 adds structured request telemetry and low-cardinality metrics so contributors can triage issues without enabling debug mode.

## Defaults

- Structured events: enabled
- Event sink: `artifacts/observability/events.jsonl`
- Event sampling rate: `1.0` (emit all events)
- Metrics: enabled
- Metrics endpoint: `/metrics`
- Metrics access mode: `open`
- Query-string capture in events: disabled by default

## Quick Verification

```bash
. .venv/bin/activate
python -m pytest -q tests/test_observability_contracts.py tests/test_transport_runtime.py tests/test_transport_parity.py
python -m pytest -q
```

## Triage Flow (Metrics First)

1. Check request volume and outcome shape:
- `redwardenlite_requests_total{action,reason,transport_mode,runtime_profile}`

2. Check transport health:
- `redwardenlite_upstream_failures_total{transport_mode,error_class}`

3. Check latency distribution:
- `redwardenlite_request_duration_seconds_bucket`
- `redwardenlite_request_duration_seconds_count`
- `redwardenlite_request_duration_seconds_sum`

4. If an anomaly appears in metrics, drill into structured events by `action` and `reason`.

## Event Drilldown (Logs Second)

Each completed request writes one JSONL event with:

- `timestamp`
- `method`
- `path` (query excluded unless explicitly enabled)
- `status`
- `action`
- `reason`
- `duration_ms`
- `transport_mode`
- `runtime_profile`

Useful examples:

```bash
tail -n 200 artifacts/observability/events.jsonl | jq -c '. | {timestamp,method,path,status,action,reason,transport_mode,runtime_profile,duration_ms}'
```

```bash
jq -r 'select(.action=="drop") | [.timestamp,.reason,.path,.status] | @tsv' artifacts/observability/events.jsonl
```

## Rollback/Control Knobs

- Disable events:
  - `observability_events_enabled: false`
- Change events sink:
  - `observability_events_file: <path>`
- Set event sampling:
  - `observability_events_sampling_rate: 0.0..1.0`
- Disable metrics:
  - `observability_metrics_enabled: false`
- Move metrics path:
  - `observability_metrics_path: /metrics`
- Restrict metrics access:
  - `observability_metrics_access_mode: open | loopback | cidr`
  - `observability_metrics_allowed_cidrs: ["10.0.0.0/8"]` (for `cidr` mode)

Telemetry is best-effort: sink failures are logged and do not block request handling.

## Event Sink Lifecycle (Retention + Rotation)

Contributor verification checklist:

1. Confirm sink path and writeability:

```bash
test -w "$(dirname artifacts/observability/events.jsonl)" && echo "sink path writable"
```

2. Validate events are being appended:

```bash
wc -l artifacts/observability/events.jsonl
tail -n 5 artifacts/observability/events.jsonl
```

3. Validate rotated file handling (external rotation policy):
- Ensure rotation keeps JSONL line boundaries.
- Ensure current file is recreated and writable after rotation.

4. Re-run contract checks:

```bash
python -m pytest -q tests/test_observability_contracts.py
```

## Sampling Notes

- Sampling is deterministic for the same event payload.
- `1.0` emits all events, `0.0` emits none, intermediate values apply deterministic selection.
- Sampling affects event sink writes only; metrics remain unsampled in this phase.

## CI Gate

CI runs observability contract tests as a hard-fail gate on both `push` and `pull_request` before the full test suite.
