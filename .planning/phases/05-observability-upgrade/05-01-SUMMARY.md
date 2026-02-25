---
phase: 05-observability-upgrade
plan: 01
subsystem: telemetry-core
tags: [observability, metrics, telemetry]
provides:
  - structured request event schema
  - low-cardinality metrics registry
  - /metrics endpoint exposure
affects:
  - RedWardenLite.py
  - lib/optionsparser.py
  - lib/proxyhandler.py
  - lib/observability.py
  - plugins/redirector.py
  - example-config.yaml
  - tests/test_observability_contracts.py
tech-stack:
  added: [lib/observability.py, tests/test_observability_contracts.py]
  patterns: [best-effort event sink, low-cardinality metrics labels, one-event-per-completed-request]
key-files:
  created:
    - lib/observability.py
    - tests/test_observability_contracts.py
  modified:
    - RedWardenLite.py
    - lib/optionsparser.py
    - lib/proxyhandler.py
    - plugins/redirector.py
    - example-config.yaml
key-decisions:
  - Keep plain logs and add structured JSONL events
  - Expose Prometheus metrics on /metrics with bounded labels
  - Keep telemetry best-effort to avoid request path blocking
patterns-established: [request completion telemetry contract]
duration: 35min
completed: 2026-02-25
---

# Phase 5: observability-upgrade Summary

**Implemented telemetry core contracts with structured request events, Prometheus metrics, and request-path-safe best-effort emission.**

## Performance
- **Duration:** 35min
- **Tasks:** 3 completed
- **Files modified:** 7

## Accomplishments
- Added observability config/CLI surface with defaults enabled.
- Added `lib/observability.py` with event builder, JSONL sink, metrics registry, and Prometheus renderer.
- Added `/metrics` routing before proxy catch-all handlers.
- Integrated request completion event+metrics emission into `ProxyRequestHandler.my_handle_request`.
- Captured policy action/reason onto request scope in `redirector.report` so events reflect policy outcomes.
- Added deterministic observability contract tests for schema, sink resilience, metrics families, endpoint response, and route ordering.

## Files Created/Modified
- `lib/observability.py` - structured event and metrics helpers.
- `tests/test_observability_contracts.py` - observability contract coverage.
- `RedWardenLite.py` - observability defaults + metrics route ordering helper.
- `lib/optionsparser.py` - observability CLI/config options.
- `lib/proxyhandler.py` - telemetry emission and metrics endpoint handler.
- `plugins/redirector.py` - request-scoped action/reason propagation.
- `example-config.yaml` - observability configuration section.

## Decisions & Deviations
No deviations from locked Phase 5 telemetry scope.
