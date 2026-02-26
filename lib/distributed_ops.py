import glob
import json
import os
from collections import defaultdict
from datetime import datetime, timezone


DEFAULT_POLICY_ARTIFACT_DIR = "artifacts/distributed/policy"
DEFAULT_FLEET_ARTIFACT_DIR = "artifacts/distributed/fleet"
DEFAULT_RETENTION_COUNT = 20


def _utc_timestamp(value=None):
    if value:
        return str(value)
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe_int(value, default=0):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed >= 0 else default


def _safe_float(value, default=0.0):
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed >= 0 else default


def normalize_node_id(value):
    text = str(value or "").strip().lower()
    return text if text else "node-unknown"


def build_policy_advertisement(node_id, policy_hash, generation, updated_at=None):
    return {
        "schema_version": "1",
        "node_id": normalize_node_id(node_id),
        "policy_hash": str(policy_hash or "unknown").strip().lower(),
        "generation": _safe_int(generation, 0),
        "updated_at": str(updated_at or datetime.now(timezone.utc).isoformat()),
    }


def _normalized_policy_advertisement(raw):
    if not isinstance(raw, dict):
        raw = {}
    return build_policy_advertisement(
        raw.get("node_id", "node-unknown"),
        raw.get("policy_hash", "unknown"),
        raw.get("generation", 0),
        raw.get("updated_at"),
    )


def merge_policy_advertisements(advertisements):
    dedup = {}

    for raw in advertisements or []:
        item = _normalized_policy_advertisement(raw)
        key = item["node_id"]
        prev = dedup.get(key)
        if prev is None:
            dedup[key] = item
            continue

        prev_rank = (prev["generation"], prev["updated_at"], prev["policy_hash"], prev["node_id"])
        next_rank = (item["generation"], item["updated_at"], item["policy_hash"], item["node_id"])
        if next_rank >= prev_rank:
            dedup[key] = item

    nodes = [dedup[key] for key in sorted(dedup.keys())]
    if not nodes:
        return {
            "schema_version": "1",
            "node_count": 0,
            "converged": True,
            "winner_policy_hash": "unknown",
            "winner_generation": 0,
            "winner_node_id": "node-unknown",
            "nodes": [],
            "divergent_node_ids": [],
            "consensus_node_ids": [],
        }

    winner = max(nodes, key=lambda item: (item["generation"], item["policy_hash"], item["node_id"]))
    winner_hash = winner["policy_hash"]

    consensus = [item["node_id"] for item in nodes if item["policy_hash"] == winner_hash]
    divergent = [item["node_id"] for item in nodes if item["policy_hash"] != winner_hash]

    return {
        "schema_version": "1",
        "node_count": len(nodes),
        "converged": len(divergent) == 0,
        "winner_policy_hash": winner_hash,
        "winner_generation": winner["generation"],
        "winner_node_id": winner["node_id"],
        "nodes": nodes,
        "divergent_node_ids": divergent,
        "consensus_node_ids": consensus,
    }


def _write_json(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, sort_keys=True, indent=2)
        handle.write("\n")


def _apply_retention(directory, pattern, retention_count):
    retention = _safe_int(retention_count, DEFAULT_RETENTION_COUNT)
    if retention <= 0:
        retention = DEFAULT_RETENTION_COUNT

    matches = sorted(glob.glob(os.path.join(directory, pattern)))
    if len(matches) <= retention:
        return []

    removed = []
    for path in matches[: len(matches) - retention]:
        try:
            os.remove(path)
            removed.append(path)
        except OSError:
            continue
    return removed


def write_policy_convergence_artifact(
        artifact_dir,
        cluster_id,
        convergence_report,
        timestamp=None,
        retention_count=DEFAULT_RETENTION_COUNT):
    directory = str(artifact_dir or DEFAULT_POLICY_ARTIFACT_DIR)
    ts = _utc_timestamp(timestamp)
    cluster = str(cluster_id or "cluster").strip().lower().replace(" ", "-")
    filename = "policy-convergence-{}-{}.json".format(cluster, ts)
    path = os.path.join(directory, filename)

    payload = {
        "artifact_type": "policy_convergence",
        "cluster_id": cluster,
        "timestamp": ts,
        "report": convergence_report,
    }
    _write_json(path, payload)
    removed = _apply_retention(directory, "policy-convergence-{}-*.json".format(cluster), retention_count)
    return {"path": path, "removed": removed}


def _normalize_series_entry(entry, labels):
    if not isinstance(entry, dict):
        entry = {}
    normalized = {label: str(entry.get(label, "unknown") or "unknown").strip().lower() for label in labels}
    normalized["value"] = _safe_float(entry.get("value", 0), 0.0)
    return normalized


def aggregate_fleet_telemetry(node_payloads):
    request_labels = ("method", "action", "reason", "transport_mode", "runtime_profile")
    failure_labels = ("transport_mode", "error_class")

    requests_totals = defaultdict(float)
    failure_totals = defaultdict(float)
    latency_count = 0
    latency_sum = 0.0
    node_ids = set()

    for raw in node_payloads or []:
        payload = raw if isinstance(raw, dict) else {}
        node_ids.add(normalize_node_id(payload.get("node_id")))

        for entry in payload.get("requests_total", []):
            normalized = _normalize_series_entry(entry, request_labels)
            key = tuple(normalized[label] for label in request_labels)
            requests_totals[key] += normalized["value"]

        for entry in payload.get("upstream_failures_total", []):
            normalized = _normalize_series_entry(entry, failure_labels)
            key = tuple(normalized[label] for label in failure_labels)
            failure_totals[key] += normalized["value"]

        latency = payload.get("latency_seconds", {})
        if isinstance(latency, dict):
            latency_count += _safe_int(latency.get("count", 0), 0)
            latency_sum += _safe_float(latency.get("sum", 0.0), 0.0)

    requests_series = []
    for key in sorted(requests_totals.keys()):
        row = {label: key[idx] for idx, label in enumerate(request_labels)}
        row["value"] = int(requests_totals[key]) if requests_totals[key].is_integer() else requests_totals[key]
        requests_series.append(row)

    failures_series = []
    for key in sorted(failure_totals.keys()):
        row = {label: key[idx] for idx, label in enumerate(failure_labels)}
        row["value"] = int(failure_totals[key]) if failure_totals[key].is_integer() else failure_totals[key]
        failures_series.append(row)

    return {
        "schema_version": "1",
        "node_count": len(node_ids),
        "nodes": sorted(node_ids),
        "requests_total": requests_series,
        "upstream_failures_total": failures_series,
        "latency_seconds": {
            "count": latency_count,
            "sum": round(latency_sum, 6),
        },
    }


def write_fleet_telemetry_snapshot(
        artifact_dir,
        fleet_snapshot,
        timestamp=None,
        retention_count=DEFAULT_RETENTION_COUNT):
    directory = str(artifact_dir or DEFAULT_FLEET_ARTIFACT_DIR)
    ts = _utc_timestamp(timestamp)
    filename = "fleet-telemetry-{}.json".format(ts)
    path = os.path.join(directory, filename)

    payload = {
        "artifact_type": "fleet_telemetry",
        "timestamp": ts,
        "snapshot": fleet_snapshot,
    }
    _write_json(path, payload)
    removed = _apply_retention(directory, "fleet-telemetry-*.json", retention_count)
    return {"path": path, "removed": removed}
