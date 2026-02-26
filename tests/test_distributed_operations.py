import json
from pathlib import Path

from lib.distributed_ops import (
    aggregate_fleet_telemetry,
    build_policy_advertisement,
    merge_policy_advertisements,
    write_fleet_telemetry_snapshot,
    write_policy_convergence_artifact,
)


def test_policy_merge_is_deterministic_regardless_input_order():
    advertisements = [
        build_policy_advertisement("node-a", "hash-aaa", 1, "2026-02-26T00:00:01Z"),
        build_policy_advertisement("node-b", "hash-bbb", 2, "2026-02-26T00:00:02Z"),
        build_policy_advertisement("node-c", "hash-bbb", 2, "2026-02-26T00:00:03Z"),
    ]

    first = merge_policy_advertisements(advertisements)
    second = merge_policy_advertisements(list(reversed(advertisements)))

    assert first == second
    assert first["winner_policy_hash"] == "hash-bbb"
    assert first["winner_generation"] == 2


def test_policy_merge_reports_divergent_nodes():
    advertisements = [
        build_policy_advertisement("node-a", "hash-aaa", 3, "2026-02-26T00:00:03Z"),
        build_policy_advertisement("node-b", "hash-bbb", 2, "2026-02-26T00:00:02Z"),
    ]

    merged = merge_policy_advertisements(advertisements)

    assert merged["converged"] is False
    assert merged["divergent_node_ids"] == ["node-b"]
    assert merged["consensus_node_ids"] == ["node-a"]


def test_policy_convergence_artifact_retention(tmp_path):
    report = merge_policy_advertisements(
        [build_policy_advertisement("node-a", "hash-aaa", 1, "2026-02-26T00:00:01Z")]
    )
    artifact_dir = tmp_path / "policy"

    write_policy_convergence_artifact(artifact_dir, "cluster-a", report, timestamp="20260226T000001Z", retention_count=2)
    write_policy_convergence_artifact(artifact_dir, "cluster-a", report, timestamp="20260226T000002Z", retention_count=2)
    result = write_policy_convergence_artifact(
        artifact_dir,
        "cluster-a",
        report,
        timestamp="20260226T000003Z",
        retention_count=2,
    )

    files = sorted(artifact_dir.glob("policy-convergence-cluster-a-*.json"))
    assert len(files) == 2
    assert files[0].name.endswith("000002Z.json")
    assert files[1].name.endswith("000003Z.json")
    assert len(result["removed"]) == 1


def test_fleet_telemetry_aggregation_totals():
    snapshot = aggregate_fleet_telemetry(
        [
            {
                "node_id": "node-a",
                "requests_total": [
                    {
                        "method": "GET",
                        "action": "allow",
                        "reason": "99",
                        "transport_mode": "legacy",
                        "runtime_profile": "compatible",
                        "value": 5,
                    }
                ],
                "upstream_failures_total": [
                    {"transport_mode": "async", "error_class": "timeout", "value": 1}
                ],
                "latency_seconds": {"count": 5, "sum": 1.2},
            },
            {
                "node_id": "node-b",
                "requests_total": [
                    {
                        "method": "GET",
                        "action": "allow",
                        "reason": "99",
                        "transport_mode": "legacy",
                        "runtime_profile": "compatible",
                        "value": 7,
                    }
                ],
                "upstream_failures_total": [
                    {"transport_mode": "async", "error_class": "timeout", "value": 2}
                ],
                "latency_seconds": {"count": 7, "sum": 2.3},
            },
        ]
    )

    assert snapshot["node_count"] == 2
    assert snapshot["nodes"] == ["node-a", "node-b"]
    assert snapshot["requests_total"][0]["value"] == 12
    assert snapshot["upstream_failures_total"][0]["value"] == 3
    assert snapshot["latency_seconds"]["count"] == 12
    assert snapshot["latency_seconds"]["sum"] == 3.5


def test_fleet_snapshot_retention(tmp_path):
    artifact_dir = tmp_path / "fleet"
    snapshot = aggregate_fleet_telemetry([])

    write_fleet_telemetry_snapshot(artifact_dir, snapshot, timestamp="20260226T000001Z", retention_count=2)
    write_fleet_telemetry_snapshot(artifact_dir, snapshot, timestamp="20260226T000002Z", retention_count=2)
    result = write_fleet_telemetry_snapshot(
        artifact_dir,
        snapshot,
        timestamp="20260226T000003Z",
        retention_count=2,
    )

    files = sorted(artifact_dir.glob("fleet-telemetry-*.json"))
    assert len(files) == 2
    assert files[0].name.endswith("000002Z.json")
    assert files[1].name.endswith("000003Z.json")
    assert len(result["removed"]) == 1

    payload = json.loads(files[1].read_text(encoding="utf-8"))
    assert payload["artifact_type"] == "fleet_telemetry"


def test_distributed_runbook_contains_triage_and_rollback():
    runbook = (
        Path(__file__).resolve().parents[1] / "docs" / "distributed-operations.md"
    ).read_text(encoding="utf-8")

    assert "Policy Convergence Workflow" in runbook
    assert "Fleet Telemetry Workflow" in runbook
    assert "Rollback-Safe Disable Procedure" in runbook
    assert "distributed_policy_enabled: false" in runbook
