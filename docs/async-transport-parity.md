# Async Transport Parity Runbook

## Purpose

This runbook defines how to enable, verify, and rollback Phase 2 transport-mode behavior while preserving default external proxy semantics.

## Config Surface

Transport and parity controls:

- `transport_mode: legacy | async | auto`
- `transport_async_fallback_to_legacy_on_error: true|false`
- `transport_parity_enabled: true|false`
- `transport_parity_header_ignore: [header-name, ...]`
- `transport_parity_allowlist_file: path`
- `transport_parity_artifact_dir: artifacts/parity`
- `transport_parity_ci_hard_fail: true|false`

Default-safe posture remains:

- `transport_mode: legacy`
- `transport_parity_enabled: false`

## Enable Flow

1. Set transport mode explicitly in config.
2. Keep fallback enabled during rollout:
   - `transport_async_fallback_to_legacy_on_error: true`
3. Enable shadow parity for comparison visibility:
   - `transport_parity_enabled: true`
4. Restart RedWardenLite.

## Verification Flow

Run targeted tests:

```bash
. .venv/bin/activate
python -m pytest -q tests/test_transport_runtime.py tests/test_transport_parity.py
```

Run full suite:

```bash
. .venv/bin/activate
python -m pytest -q
```

Check parity artifacts:

- `artifacts/parity/parity-events.jsonl`
- `artifacts/parity/parity-summary.md`

## Rollback Procedure (Canonical)

1. Set `transport_mode: legacy`.
2. Optionally set `transport_parity_enabled: false`.
3. Restart RedWardenLite.

This is the only rollback mechanism for Phase 2 (no runtime hot switch).

## Rollback Smoke Command

Use the following as rollback smoke verification:

```bash
. .venv/bin/activate
python -m pytest -q tests/test_transport_runtime.py -k "legacy or fallback"
```

This confirms legacy path selection and async-error fallback behavior remain operational.

## Triage Checklist

1. If async mode errors appear, confirm fallback is enabled.
2. Review `parity-summary.md` unresolved mismatch counts.
3. Confirm allowlist patterns match only approved mismatch IDs.
4. If unresolved mismatches are unexpected, rollback to `legacy`, restart, and investigate before re-enabling async.

## Notes

- Shadow parity is non-enforcing for live responses in this phase.
- CI policy should fail when non-allowlisted mismatch conditions are encoded in deterministic tests.
