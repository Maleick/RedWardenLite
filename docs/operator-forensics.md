# Operator Forensics Runbook

## Purpose

Phase 8 adds deterministic incident-response workflows for policy, transport, and observability failures. This runbook is contributor-runnable and artifact-driven so incident evidence is reproducible.

## Incident Classes

- **Policy incident**: Unexpected allow/drop/alter-host outcome or wrong policy reason.
- **Transport incident**: Upstream fetch fallback/parity mismatch/timeout behavior anomaly.
- **Observability incident**: Missing/incorrect metrics/events or telemetry pipeline degradation.

## Global Workflow (Deterministic)

1. Create a UTC case id and bundle directory.

```bash
CASE_ID="INC-$(date -u +%Y%m%dT%H%M%SZ)"
BUNDLE_DIR="artifacts/forensics/${CASE_ID}"
mkdir -p "${BUNDLE_DIR}"
```

2. Capture environment and startup-hardening baseline.

```bash
{
  echo "case_id=${CASE_ID}"
  echo "captured_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "python=$(python --version 2>&1)"
} > "${BUNDLE_DIR}/00-case-summary.txt"

. .venv/bin/activate && python -m pytest -q tests/test_runtime_hardening.py > "${BUNDLE_DIR}/01-runtime-hardening.txt" 2>&1
```

3. Run incident-specific workflow below.
4. Materialize evidence bundle files and checksum manifest.

## Policy Incident Workflow

1. Reproduce policy contract behavior:

```bash
. .venv/bin/activate && python -m pytest -q tests/test_policy_reason_codes.py tests/test_policy_side_effect_contracts.py > "${BUNDLE_DIR}/02-policy-contract.txt" 2>&1
```

2. Capture recent drop/allow decisions from structured events:

```bash
tail -n 200 artifacts/observability/events.jsonl > "${BUNDLE_DIR}/06-events-sample.jsonl" 2>/dev/null || true
```

3. Classify affected reason/action pairs and add notes to `00-case-summary.txt`.

## Transport Incident Workflow

1. Reproduce transport contracts:

```bash
. .venv/bin/activate && python -m pytest -q tests/test_transport_runtime.py tests/test_transport_parity.py > "${BUNDLE_DIR}/03-transport-contract.txt" 2>&1
```

2. Capture latest parity markdown artifact when present:

```bash
LATEST_PARITY_MD="$(ls -1t artifacts/parity/*.md 2>/dev/null | head -n 1 || true)"
if [ -n "${LATEST_PARITY_MD}" ]; then cp "${LATEST_PARITY_MD}" "${BUNDLE_DIR}/07-parity-latest.md"; fi
```

3. Record fallback/mismatch timeline in `00-case-summary.txt`.

## Observability Incident Workflow

1. Reproduce observability contracts:

```bash
. .venv/bin/activate && python -m pytest -q tests/test_observability_contracts.py > "${BUNDLE_DIR}/04-observability-contract.txt" 2>&1
```

2. Capture metrics snapshot:

```bash
curl -fsS http://127.0.0.1:8080/metrics > "${BUNDLE_DIR}/05-metrics.prom"
```

3. If event ingest is suspected, inspect event sink growth and recent lines:

```bash
wc -l artifacts/observability/events.jsonl >> "${BUNDLE_DIR}/00-case-summary.txt" 2>/dev/null || true
```

## Evidence Bundle Procedure

Expected deterministic layout under `artifacts/forensics/<case-id>/`:

- `00-case-summary.txt`
- `01-runtime-hardening.txt`
- `02-policy-contract.txt`
- `03-transport-contract.txt`
- `04-observability-contract.txt`
- `05-metrics.prom`
- `06-events-sample.jsonl`
- `07-parity-latest.md` (when parity artifact exists)
- `98-command-log.txt`
- `99-sha256sums.txt`

Recommended finalization command:

```bash
{
  echo "Commands executed for ${CASE_ID}";
  echo "policy=tests/test_policy_reason_codes.py tests/test_policy_side_effect_contracts.py";
  echo "transport=tests/test_transport_runtime.py tests/test_transport_parity.py";
  echo "observability=tests/test_observability_contracts.py";
} > "${BUNDLE_DIR}/98-command-log.txt"

(cd "${BUNDLE_DIR}" && sha256sum * > 99-sha256sums.txt)
```

The checksum manifest is the integrity anchor for incident handoff and audit follow-up.
