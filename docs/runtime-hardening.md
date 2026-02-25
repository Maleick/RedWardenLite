# Runtime Hardening Runbook

## Purpose

This runbook defines how to enable, verify, and rollback Phase 4 runtime hardening controls while preserving compatibility-default behavior.

## Config Surface

- `runtime_profile: compatible | strict`
- `runtime_hardening_allow_unsafe: true|false`
- `runtime_hardening_unsafe_ack: <string>`
- `runtime_hardening_validation_output: human | json`

Default posture:

- `runtime_profile: compatible`
- `runtime_hardening_allow_unsafe: false`
- `runtime_hardening_validation_output: human`

## Enable Flow (Strict)

1. Set `runtime_profile: strict`.
2. Review listener bind/port scheme combinations and remove unsafe public HTTP listeners.
3. Keep `runtime_hardening_allow_unsafe: false` for normal enforcement.
4. Restart RedWardenLite.

## Validation Behavior

- Strict mode aggregates all startup hardening findings and fails once.
- Each finding includes:
  - setting path
  - failure reason
  - safe replacement example
- `runtime_hardening_validation_output: json` provides machine-readable output.

## Verification Flow

Run targeted runtime hardening tests:

```bash
. .venv/bin/activate
python -m pytest -q tests/test_runtime_hardening.py
```

Run transport regression tests:

```bash
. .venv/bin/activate
python -m pytest -q tests/test_transport_runtime.py tests/test_transport_parity.py
```

Run full suite:

```bash
. .venv/bin/activate
python -m pytest -q
```

## Rollback Procedure (Canonical)

1. Set `runtime_profile: compatible`.
2. Set `runtime_hardening_allow_unsafe: false`.
3. Clear `runtime_hardening_unsafe_ack`.
4. Restart RedWardenLite.

No automatic strict-to-compatible fallback is performed at runtime.

## Unsafe Override (Exceptional Use)

If strict mode blocks startup and temporary bypass is required:

1. Set `runtime_hardening_allow_unsafe: true`.
2. Set a non-empty `runtime_hardening_unsafe_ack` value documenting accepted risk.
3. Restart and remediate immediately.
4. Disable override after remediation.

## Triage Checklist

1. Read all aggregated findings from startup output.
2. Fix listener bind/scheme findings first.
3. Re-run `tests/test_runtime_hardening.py`.
4. Re-run full suite before merging.
