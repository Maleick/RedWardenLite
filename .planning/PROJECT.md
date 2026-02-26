# RedWardenLite Evolution

## What This Is

RedWardenLite is a Python/Tornado HTTP/HTTPS reverse proxy that enforces request policy decisions with auditable reason/action outcomes. The platform now includes deterministic policy/transport/runtime/observability contracts plus plugin compatibility/isolation and distributed coordination/telemetry contract layers.

## Core Value

Legitimate traffic must pass reliably while non-conformant or suspicious traffic is blocked predictably with auditable policy reasons.

## Current State

- Latest shipped milestone: **v2.0 extensibility + distributed operations** (2026-02-26)
- Current quality gate: `98` deterministic tests passing
- Archived milestone artifacts:
  - `.planning/milestones/v1.0-ROADMAP.md`
  - `.planning/milestones/v1.1-ROADMAP.md`
  - `.planning/milestones/v2.0-ROADMAP.md`

## Next Milestone Goals

- Define control-plane API/authn model for safe fleet policy/runtime profile management.
- Add policy/transport/observability health-driven rollback orchestration contracts.
- Keep existing proxy behavior contracts backward compatible while introducing control-plane capabilities.

## Requirements

### Validated

- ✓ v1.0 modernization baseline (policy contracts, async parity, policy decomposition, runtime hardening, observability contracts)
- ✓ v1.1 operational maturity baseline (observability hardening, deployment templates, compatibility matrix, operator forensics, strict override refinement)
- ✓ v2.0 extensibility + distributed operations baseline (plugin contracts/isolation and distributed policy/telemetry contracts)

### Active

- [ ] Define secure fleet control-plane API for policy/runtime management.
- [ ] Add deterministic rollback orchestration contracts with health-threshold triggers.

### Out of Scope

- Runtime control-plane web UI productization in next cycle — API/control contracts first.
- Full protocol expansion beyond HTTP/HTTPS proxy — current customer value remains within existing protocol scope.
- Autonomous rollback actions without explicit operator policy thresholds.

## Context

Milestones v1.0, v1.1, and v2.0 are complete and archived in `.planning/milestones/`. The next cycle targets fleet control-plane and rollback orchestration contracts while preserving backward-compatible proxy behavior and deterministic verification gates.

## Constraints

- **Tech stack**: Python/Tornado runtime remains baseline — avoid disruptive stack migration.
- **Compatibility**: External proxy behavior and policy ordering must stay stable unless explicitly versioned.
- **Operational safety**: No secrets in planning artifacts, prompts, logs, or generated docs.
- **Delivery pace**: Keep incremental phase-scoped changes with deterministic verification and CI hard gates.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Incremental brownfield modernization over rewrite | Existing deployed behavior has value and rewrite risk is high | ✓ Good |
| Behavior-lockdown before major refactors | Prevent regressions while decoupling internals | ✓ Good |
| Runtime hardening opt-in before strict-by-default | Reduce rollout risk while introducing safety controls | ✓ Good |
| v1.1 focused on operational maturity | Baseline behavior stability exposed ops/deploy gaps as highest risk | ✓ Good |
| v2.0 targeted extensibility + distributed operations | Next growth risk was plugin/fleet scale, not core policy correctness | ✓ Good |
| Next cycle should focus on control-plane + rollback contracts | Fleet scale now requires safe orchestration and rollback semantics | — Pending |

<details>
<summary>Archived Prior Focus Snapshot</summary>

v2.0 pre-ship active requirements:
- Publish formal plugin capability/version compatibility contracts and validation flow.
- Introduce stronger plugin execution isolation and boundary controls.
- Define deterministic multi-node policy state distribution and coordination model.
- Add centralized fleet-level telemetry aggregation and retention controls.

</details>

---
*Last updated: 2026-02-26 after v2.0 milestone completion*
