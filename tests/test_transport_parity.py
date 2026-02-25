import gzip
import json

from lib.transport_parity import (
    apply_allowlist,
    compare_transport_results,
    load_allowlist_patterns,
    normalize_headers,
    write_parity_artifacts,
)


def test_normalize_headers_ignores_hop_by_hop_and_volatile_headers():
    headers = {
        "Connection": "keep-alive",
        "Date": "Wed, 25 Feb 2026 14:00:00 GMT",
        "Content-Type": "application/json",
        "X-Custom": "ok",
    }

    normalized = normalize_headers(headers, extra_ignored=["x-custom"])

    assert "connection" not in normalized
    assert "date" not in normalized
    assert "x-custom" not in normalized
    assert normalized["content-type"] == "application/json"


def test_compare_transport_results_detects_status_header_body_mismatches():
    primary = {
        "status": 200,
        "reason": "OK",
        "headers": {"Content-Type": "text/plain", "X-Test": "a", "Content-Encoding": "identity"},
        "body": b"hello",
    }
    shadow = {
        "status": 502,
        "reason": "Bad Gateway",
        "headers": {"Content-Type": "text/plain", "X-Test": "b", "Content-Encoding": "identity"},
        "body": b"world",
    }

    result = compare_transport_results(primary, shadow, header_ignore=["content-encoding"])

    assert result["match"] is False
    mismatch_ids = {entry["id"] for entry in result["mismatches"]}
    assert "status:200!=502" in mismatch_ids
    assert "header:x-test" in mismatch_ids
    assert "body:sha256" in mismatch_ids


def test_compare_transport_results_decodes_gzip_before_body_compare():
    zipped = gzip.compress(b"same-body")
    primary = {
        "status": 200,
        "reason": "OK",
        "headers": {"Content-Encoding": "gzip"},
        "body": zipped,
    }
    shadow = {
        "status": 200,
        "reason": "OK",
        "headers": {"Content-Encoding": "identity"},
        "body": b"same-body",
    }

    result = compare_transport_results(primary, shadow, header_ignore=["content-encoding"])

    assert result["match"] is True
    assert result["mismatches"] == []


def test_apply_allowlist_filters_matching_mismatch_ids():
    mismatches = [
        {"id": "header:x-request-id"},
        {"id": "body:sha256"},
    ]

    allowlisted, unresolved = apply_allowlist(mismatches, [r"^header:x-request-id$"])

    assert len(allowlisted) == 1
    assert allowlisted[0]["id"] == "header:x-request-id"
    assert len(unresolved) == 1
    assert unresolved[0]["id"] == "body:sha256"


def test_load_allowlist_patterns_accepts_dict_or_list(tmp_path):
    dict_file = tmp_path / "allowlist-dict.json"
    dict_file.write_text(json.dumps({"patterns": ["^status:", "header:x-test"]}), encoding="utf-8")

    list_file = tmp_path / "allowlist-list.json"
    list_file.write_text(json.dumps(["body:sha256"]), encoding="utf-8")

    assert load_allowlist_patterns(str(dict_file)) == ["^status:", "header:x-test"]
    assert load_allowlist_patterns(str(list_file)) == ["body:sha256"]
    assert load_allowlist_patterns(str(tmp_path / "missing.json")) == []


def test_write_parity_artifacts_creates_jsonl_and_markdown(tmp_path):
    event = {
        "timestamp": "2026-02-25T14:00:00Z",
        "method": "GET",
        "path": "/beacon",
        "primary_transport": "legacy",
        "shadow_transport": "async",
        "allowlisted_count": 0,
        "unresolved_count": 1,
        "allowlisted_mismatches": [],
        "unresolved_mismatches": [{"id": "status:200!=500"}],
    }

    output = write_parity_artifacts(str(tmp_path / "parity"), event)

    assert "jsonl" in output and "summary" in output
    assert (tmp_path / "parity" / "parity-events.jsonl").exists()
    assert (tmp_path / "parity" / "parity-summary.md").exists()

    summary = (tmp_path / "parity" / "parity-summary.md").read_text(encoding="utf-8")
    assert "Transport Parity Summary" in summary
    assert "Events with unresolved mismatches: 1" in summary
