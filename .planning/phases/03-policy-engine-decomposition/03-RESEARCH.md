# Phase 3: Policy Engine Decomposition - Research

**Date:** 2026-02-25
**Scope:** Internal policy/action decomposition with strict behavior parity

## Current Baseline

- `plugins/redirector.py` contains policy checks, decision flow, and side effects intertwined.
- `_client_request_inspect` currently defines de facto policy evaluation order.
- `drop_check` and `_drop_action` rely on this behavior and are already covered by behavior-lockdown tests.

## Main Decomposition Risks

1. Ordering drift risk.
- Reordering checks changes reason outcomes and side effects.
- Mitigation: preserve exact order contract and keep tests as hard gate.

2. Side-effect bleed in decision logic.
- Existing check paths can log/report while deciding.
- Mitigation: decision engine evaluates in side-effect-free mode and action executor applies effects.

3. Compatibility drift at plugin boundary.
- Request/response handler flows must remain backward compatible.
- Mitigation: compatibility facade in `redirector.py` delegates to internal modules without changing caller contract.

## Proposed Internal Structure

- `plugins/policy/checks/` for policy-family grouped checks.
- `plugins/policy/engine.py` for deterministic ordered decision evaluation.
- `plugins/policy/actions.py` for centralized side-effect execution.
- `plugins/policy/types.py` for structured decision type.

## Verification Focus

- Ensure `test_policy_reason_codes.py` and side-effect suites remain unchanged in outcomes.
- Add targeted decomposition tests that assert:
  - structured decision output,
  - side-effect-free decision evaluation,
  - compatibility of action executor behavior.

## Out of Scope

- Public API changes.
- Plugin contract versioning.
- Runtime control-plane changes.
