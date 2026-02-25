# Behavior Lockdown Testing

## Purpose

Behavior-lockdown tests preserve externally observable policy behavior so refactors can proceed without semantic drift.

Primary contract target: `plugins/redirector.py`.

## Contract Scope

Current contract coverage includes:

- Reason outcomes for allow/drop paths (`0`, `1`, `2`, `3`, `4a`, `4b`, `4c`, `4d`, `4e`, `5`, `6`, `7`, `8`, `99`)
- Core side effects:
  - `drop_action` observable outcomes for `reset`, `redirect`, `proxy`
  - keep-alive/drop request connection behavior
  - host-header override semantics via `expected_headers_value`

All coverage is deterministic and offline.

## Local Setup

From repository root:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pytest
```

## One-Command Verification

Run both behavior-lockdown suites:

```bash
python -m pytest -q tests/test_policy_reason_codes.py tests/test_policy_side_effect_contracts.py
```

## Targeted vs Full Suite

- Targeted behavior-lockdown suites:

```bash
python -m pytest -q tests/test_policy_reason_codes.py tests/test_policy_side_effect_contracts.py
```

- Full repository suite:

```bash
python -m pytest -q
```

## Failure Triage Checklist

1. Confirm virtualenv is active and dependencies are installed.
2. Re-run only the failing test with `-k` to isolate behavior.
3. Inspect failing reason/action assertions first; preserve external contract unless phase scope explicitly changes it.
4. Ensure fixtures remain deterministic (no outbound DNS/network dependencies).
5. Re-run targeted behavior-lockdown suites, then run full suite.

## Add New Contract Scenario Checklist

1. Add one drop-path assertion with exact reason/action outcome.
2. Add one non-drop path for the same policy (override or compliant input).
3. Add side-effect assertions when behavior changes are externally visible (`drop_action`, headers, keep-alive/drop).
4. Keep tests offline and deterministic (mock/monkeypatch external lookups).
5. Validate with targeted suites, then full suite.

## CI Gate

CI runs pytest as a hard-fail gate on both `push` and `pull_request` via `.github/workflows/tests.yml`.

## Determinism Notes

- IP lookup and geolocation decisions use static helper objects.
- DNS reverse lookups are monkeypatched where needed.
- SQLite plugin files (`.peers.sqlite`, `.anti-replay.sqlite`) are redirected to per-test temp paths.

## Known Gaps

- End-to-end Tornado request lifecycle is not covered in this contract suite.
- CONNECT tunnel behavior is not covered in this contract suite.
- Performance and concurrency behavior are intentionally out of scope.
