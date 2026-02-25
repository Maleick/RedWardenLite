# Phase 3: Policy Engine Decomposition - Context

**Gathered:** 2026-02-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 3 decomposes redirector internals into testable policy and action units while preserving external plugin behavior and decision ordering.

</domain>

<decisions>
## Implementation Decisions

### Decomposition Strategy
- Decompose by policy family, not ad-hoc or by mixed lifecycle stage.
- Preserve exact current evaluation order from `_client_request_inspect`.
- Keep `ProxyPlugin` external request/response contract unchanged.

### Decision and Action Separation
- Decision layer returns structured `DecisionResult` with:
  - `allow`
  - `action`
  - `reason`
  - `message`
  - `ipgeo`
  - `metadata`
- Decision layer must be side-effect free.
- Dedicated action executor owns `drop` / `redirect` / `proxy` (and related) action execution paths.

### Rollout and Compatibility
- Use incremental extraction behind a compatibility facade.
- Keep behavior-contract tests as hard gate throughout extraction.
- Remove legacy internal paths only after parity is proven.

### Claude's Discretion
- File/module naming details under `plugins/policy/`.
- Internal helper ergonomics and fixture structure.
- Runbook wording/format as long as compatibility requirements remain unchanged.

</decisions>

<specifics>
## Specific Ideas

- Extract checks into focused modules under `plugins/policy/checks`.
- Add `PolicyEngine` for deterministic ordered decision evaluation.
- Add `ActionExecutor` for centralized side-effect handling.

</specifics>

<deferred>
## Deferred Ideas

- Runtime externalized policy engine APIs.
- Plugin interface redesign or versioned facade changes.
- Non-deterministic/adaptive ordering heuristics.

</deferred>

---

*Phase: 03-policy-engine-decomposition*
*Context gathered: 2026-02-25*
