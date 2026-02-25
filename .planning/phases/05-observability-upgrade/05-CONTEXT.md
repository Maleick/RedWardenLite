# Phase 5: Observability Upgrade - Context

**Gathered:** 2026-02-25
**Status:** Ready for planning

## Phase Boundary

Phase 5 delivers structured observability for production operations: stable structured request events, low-cardinality runtime metrics, and contributor-first triage guidance usable without debug mode. This phase does not alter proxy decision semantics, policy ordering, plugin interfaces, or request behavior.

## Implementation Decisions

### Structured Event Contract
- Emit one structured summary event per completed request.
- Required fields:
  - `timestamp`
  - `method`
  - `path` (query excluded by default)
  - `status`
  - `action`
  - `reason`
  - `duration_ms`
  - `transport_mode`
  - `runtime_profile`
- Continue plain logs and add structured JSONL output.
- Structured event emission is enabled by default.
- Default sampling policy is no sampling (every completed request emits one event).

### Metrics Contract
- Required metric families:
  - request totals
  - outcome/reason distribution counts
  - upstream failure counts
  - request latency histogram
- Reason metrics include both allow and drop outcomes.
- Label policy is low-cardinality and fixed (no path/query labels).
- Latency representation is histogram buckets with count/sum companions.

### Telemetry Export and Failure Behavior
- Structured events sink: configurable JSONL file with explicit enable flag.
- Metrics exposure: Prometheus text format on `/metrics`.
- `/metrics` is bound on existing listener surface in this phase.
- File retention uses external rotation policy (documented runbook guidance).
- Telemetry sink failures are best-effort: log failures and continue request flow.

### Triage Workflow and Gating
- Runbook scope is contributor-first.
- Default triage sequence is metrics-first, then structured-event drilldown.
- Structured observability detail remains usable at normal verbosity.
- CI gate is hard-fail for observability contract checks on both push and pull_request.

### Claude's Discretion
- Exact wording of structured telemetry and runbook examples.
- Helper structure, naming, and fixture composition for observability tests.
- Minor config/help text ergonomics and docs section ordering.

## Specific Ideas

- Keep path/query privacy default conservative by excluding query parameters from events.
- Keep operational adoption simple with out-of-box defaults enabled.
- Keep metrics scrape compatibility standard via Prometheus exposition text.

## Deferred Ideas

- Token-guarded metrics endpoint.
- High-cardinality path-level metric labels.
- Event sampling modes.
- Operator-deep forensic incident playbook.

---

*Phase: 05-observability-upgrade*
*Context gathered: 2026-02-25*
