# Observability Upgrade Runbook

## Purpose

Phase 5 adds structured request telemetry and low-cardinality metrics so contributors can triage issues without enabling debug mode.

## Defaults

- Structured events: enabled
- Event sink: `artifacts/observability/events.jsonl`
- Metrics: enabled
- Metrics endpoint: `/metrics`
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
- Disable metrics:
  - `observability_metrics_enabled: false`
- Move metrics path:
  - `observability_metrics_path: /metrics`

Telemetry is best-effort: sink failures are logged and do not block request handling.

## CI Gate

CI runs observability contract tests as a hard-fail gate on both `push` and `pull_request` before the full test suite.
