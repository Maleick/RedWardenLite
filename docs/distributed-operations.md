# Distributed Operations Runbook

## Purpose

Phase 10 introduces deterministic multi-node policy convergence modeling and fleet telemetry aggregation with retention-managed artifacts.

## Config Surface

- `distributed_policy_enabled: true|false`
- `distributed_policy_node_id: <node-id>`
- `distributed_policy_peer_nodes: [list]`
- `distributed_policy_artifact_dir: <dir>`
- `distributed_policy_retention_count: <int>`
- `fleet_telemetry_enabled: true|false`
- `fleet_telemetry_artifact_dir: <dir>`
- `fleet_telemetry_retention_count: <int>`

Defaults are disabled for compatibility:

- `distributed_policy_enabled: false`
- `fleet_telemetry_enabled: false`

## Policy Convergence Workflow

1. Build node advertisements (`node_id`, `policy_hash`, `generation`, `updated_at`).
2. Merge advertisements with deterministic tie-breaks:
   - higher `generation`
   - lexical `policy_hash`
   - lexical `node_id`
3. Write convergence artifact to `artifacts/distributed/policy`.
4. Verify convergence fields:
   - `converged`
   - `winner_policy_hash`
   - `winner_generation`
   - `divergent_node_ids`

## Fleet Telemetry Workflow

1. Collect node telemetry payloads:
   - request totals by low-cardinality labels
   - upstream failure totals
   - latency count/sum
2. Aggregate into fleet snapshot.
3. Write snapshot to `artifacts/distributed/fleet`.
4. Verify retention cleanup removes oldest snapshots beyond configured count.

## Verification Commands

```bash
. .venv/bin/activate
python -m pytest -q tests/test_distributed_operations.py
python -m pytest -q
```

## Distributed Incident Triage

1. Validate policy convergence artifact and check `divergent_node_ids`.
2. Validate fleet snapshot node membership and totals.
3. Check retention behavior by listing artifact directories in timestamp order.
4. Re-run distributed contract suite before applying remediation.

## Rollback-Safe Disable Procedure

1. Set `distributed_policy_enabled: false`.
2. Set `fleet_telemetry_enabled: false`.
3. Restart service.
4. Re-run distributed contract tests to verify deterministic local-only behavior.
