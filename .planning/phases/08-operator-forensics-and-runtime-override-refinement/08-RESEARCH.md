# Phase 8: Operator Forensics and Runtime Override Refinement — Research Notes

## Goal

Deliver operationally deterministic incident forensics workflows and refine strict-mode unsafe overrides with per-check acknowledgement semantics and actionable remediation guidance.

## Existing Baseline

- Runtime hardening already enforces:
  - `runtime_profile: compatible|strict`
  - strict denylist for public cleartext listener findings
  - global unsafe override gate (`runtime_hardening_allow_unsafe` + `runtime_hardening_unsafe_ack`)
  - aggregated startup failures with a stable non-zero exit code
- Runtime hardening tests exist in `tests/test_runtime_hardening.py`.
- Runtime hardening runbook exists in `docs/runtime-hardening.md`, but remediation coverage is broad and not check-by-check.
- Observability and deployment runbooks are contributor-first and deterministic; no dedicated operator-forensics runbook/evidence bundle procedure exists.

## Requirement Mapping

### OPS-01: Operator-deep triage and forensic collection guidance
- Add a dedicated runbook with deterministic triage tracks for:
  - policy incidents
  - transport/parity incidents
  - observability incidents
- Include command-level collection flow and artifact capture checkpoints.

### OPS-02: Deterministic evidence bundle expectations
- Define stable bundle location/layout under `artifacts/forensics/<case-id>/`.
- Define required artifacts and integrity manifest expectations.
- Add deterministic doc-contract tests for runbook anchors.

### SECX-01: Finer-grained strict override acknowledgement
- Extend runtime hardening config surface with per-check acknowledgement list.
- In strict mode with unsafe override active, require explicit acknowledgement coverage for each unsafe finding.
- Keep startup hard-fail when acknowledgement fields are missing/incomplete.

### SECX-02: Explicit remediation examples for denied strict checks
- Expand runtime hardening guidance with check-by-check remediation examples.
- Preserve report contract (`path`, `reason`, `safe_example`) and assert via tests.

## Integration Focus

- Runtime hardening logic: `lib/runtime_hardening.py`
- Runtime hardening config parsing/defaults:
  - `RedWardenLite.py`
  - `lib/optionsparser.py`
  - `example-config.yaml`
- Runbooks:
  - new `docs/operator-forensics.md`
  - updated `docs/runtime-hardening.md`
- Tests:
  - extend `tests/test_runtime_hardening.py`
  - add deterministic runbook/evidence procedure contract tests
- CI:
  - keep hard-fail gates on push + pull_request
  - include explicit operator-forensics contract step before full suite

## Constraints

- No proxy request/response behavior drift.
- No policy ordering or plugin interface changes.
- Keep strict mode opt-in and no automatic fallback behavior.
- Keep tests offline/deterministic.
