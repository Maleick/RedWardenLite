from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNBOOK_FILE = REPO_ROOT / "docs" / "operator-forensics.md"


def _runbook_text():
    return RUNBOOK_FILE.read_text(encoding="utf-8")


def test_operator_forensics_runbook_exists():
    assert RUNBOOK_FILE.exists()


def test_runbook_includes_incident_class_workflows():
    content = _runbook_text()

    assert "## Policy Incident Workflow" in content
    assert "## Transport Incident Workflow" in content
    assert "## Observability Incident Workflow" in content


def test_runbook_defines_deterministic_bundle_path_and_artifacts():
    content = _runbook_text()

    assert "artifacts/forensics/<case-id>/" in content
    assert "00-case-summary.txt" in content
    assert "05-metrics.prom" in content
    assert "06-events-sample.jsonl" in content
    assert "99-sha256sums.txt" in content


def test_runbook_references_contract_suites_and_metrics_collection():
    content = _runbook_text()

    assert "tests/test_policy_reason_codes.py tests/test_policy_side_effect_contracts.py" in content
    assert "tests/test_transport_runtime.py tests/test_transport_parity.py" in content
    assert "tests/test_observability_contracts.py" in content
    assert "curl -fsS http://127.0.0.1:8080/metrics" in content
