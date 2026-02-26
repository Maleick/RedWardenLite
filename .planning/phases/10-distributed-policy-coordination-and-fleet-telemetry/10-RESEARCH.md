# Phase 10: Distributed Policy Coordination and Fleet Telemetry — Research Notes

## Goal

Deliver deterministic distributed policy convergence and fleet telemetry aggregation/retention contracts with contributor-runnable operational guidance.

## Existing Baseline

- Local policy and transport behavior contracts are strongly locked through deterministic tests.
- Observability metrics/events exist at node scope (`lib/observability.py`).
- No multi-node coordination model, fleet aggregation module, or distributed runbook currently exists.
- CI currently hard-gates policy/transport/runtime/observability/plugin contract suites.

## Requirement Mapping

### DIST-01: Deterministic multi-node policy coordination
- Add deterministic policy advertisement and merge model.
- Implement verifiable convergence summary with stable tie-break rules.
- Persist policy convergence artifacts with retention controls.

### DIST-02: Fleet telemetry aggregation + retention controls
- Add deterministic fleet aggregation for request totals, upstream failures, and latency totals.
- Add retention-managed fleet snapshot artifact writing.
- Add operator runbook with verification and rollback-safe procedures.

## Integration Focus

- New distributed module:
  - `lib/distributed_ops.py`
- Runtime/config surface:
  - `RedWardenLite.py`
  - `lib/optionsparser.py`
  - `example-config.yaml`
- Docs:
  - `docs/distributed-operations.md`
- Tests + CI:
  - `tests/test_distributed_operations.py`
  - `.github/workflows/tests.yml`

## Constraints

- Preserve existing proxy behavior by keeping distributed features disabled by default.
- Keep distributed artifact operations deterministic and offline-testable.
- Ensure failures in distributed artifact/aggregation logic are non-blocking.
- Avoid introducing control-plane networking in this phase.
