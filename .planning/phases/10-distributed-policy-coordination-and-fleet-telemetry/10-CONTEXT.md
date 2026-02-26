# Phase 10: Distributed Policy Coordination and Fleet Telemetry - Context

**Gathered:** 2026-02-26
**Status:** Ready for planning

## Phase Boundary

Phase 10 delivers deterministic multi-node policy coordination and fleet-level telemetry aggregation controls with contributor-runnable runbooks. Scope is limited to distributed coordination/aggregation contracts and operational guidance; it does not introduce control-plane UI, protocol expansion, or automatic rollback orchestration.

## Implementation Decisions

### Policy Coordination Model
- Use deterministic policy advertisement records per node containing:
  - `node_id`
  - `policy_hash`
  - `generation`
  - `updated_at`
- Define convergence by deterministic merge order and tie-break rules:
  - higher `generation` wins
  - if tied, lexical `policy_hash` tie-break
  - if still tied, lexical `node_id` tie-break
- Expose convergence output as stable JSON artifacts for verification.

### Fleet Telemetry Aggregation Contract
- Aggregate node-local telemetry into centralized fleet snapshots with low-cardinality labels.
- Fleet snapshot contract includes:
  - aggregated request outcome/reason totals
  - aggregated upstream failure totals
  - latency count/sum totals
  - node membership list
- Keep snapshot schema deterministic and versioned.

### Retention and Artifact Controls
- Both policy and fleet telemetry artifacts use explicit retention-by-count controls.
- Artifact directories are configurable and auto-created if missing.
- Retention cleanup must be deterministic (oldest-by-name/timestamp first).

### Runtime Controls and Safety
- Add explicit config/CLI controls for distributed policy and fleet telemetry features.
- Defaults remain disabled to avoid behavior drift for existing deployments.
- Any distributed artifact write/aggregation failures are non-blocking and logged.

### Runbook and CI Expectations
- Add contributor-first distributed operations runbook covering:
  - convergence verification workflow
  - fleet telemetry validation workflow
  - rollback-safe disable sequence
- Add deterministic distributed contract tests and a CI hard-fail gate before full suite.

### Claude's Discretion
- Exact config option names and helper function layout.
- Artifact filename conventions and timestamp formatting.
- Test fixture shape and edge-case coverage depth.

## Deferred Ideas

- Live peer-to-peer transport/protocol for state exchange.
- Control-plane APIs for cluster-wide policy rollout orchestration.
- Automated rollback triggers based on fleet telemetry thresholds.
- Multi-tenant fleet aggregation and long-term archival backends.

---

*Phase: 10-distributed-policy-coordination-and-fleet-telemetry*
*Context gathered: 2026-02-26*
