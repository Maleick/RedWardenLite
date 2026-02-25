# Policy Engine Decomposition

This document describes the Phase 3 internal decomposition that preserves existing `ProxyPlugin` external behavior.

## Architecture

- `plugins/policy/checks/*`: family adapters that keep deterministic policy ordering while delegating to existing check logic.
- `plugins/policy/engine.py`: side-effect-free decision computation returning `DecisionResult`.
- `plugins/policy/actions.py`: centralized side-effect executor for allow/drop outcomes.
- `plugins/redirector.py`: compatibility facade that keeps legacy request/response handler behavior while routing policy evaluation through engine + executor.

## Ordering Contract

`PolicyEngine` evaluates families in this exact order:

1. `whitelist`
2. `blacklist_reverse`
3. `header_checks`
4. `expectation_checks`
5. `ipgeo_checks`

This order must remain stable to preserve current reason-code precedence.

## Decision Contract

`DecisionResult` fields:

- `allow: bool`
- `action: "allow" | "drop" | "alter_host"`
- `reason: str`
- `message: str`
- `ipgeo: dict`
- `metadata: dict`

Decision evaluation is side-effect free. Side effects are expressed as metadata (for example `override_host_header`) and applied by `ActionExecutor`.

## Side-Effect Ownership

`ActionExecutor.execute(decision, peer_ip, ts, req)` owns policy side effects:

- `drop_reason` annotation for drop decisions
- peer-info printing parity for drop reasons `2`, `3`, `4a`, `4b`
- report contract invocation (`plugin.report(...)`)
- host-header override metadata application

## Contributor Workflow

Use these commands for compatibility checks:

```bash
. .venv/bin/activate && python -m pytest -q tests/test_policy_engine_decomposition.py tests/test_policy_reason_codes.py tests/test_policy_side_effect_contracts.py
. .venv/bin/activate && python -m pytest -q
```

When adding a new policy check:

1. Place it in the correct family adapter under `plugins/policy/checks/`.
2. Add/adjust deterministic tests for reason precedence and side effects.
3. Preserve ordering unless there is an explicit contract update.
4. Keep decision-time code side-effect free; pass side-effect intent via decision metadata.
