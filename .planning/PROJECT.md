# RedWardenLite Evolution

## What This Is

RedWardenLite is a Python/Tornado HTTP/HTTPS reverse proxy that enforces request policy decisions with auditable reason/action outcomes. The platform now has locked behavior contracts, transport parity controls, runtime hardening, and deterministic observability/forensics guidance.

## Core Value

Legitimate traffic must pass reliably while non-conformant or suspicious traffic is blocked predictably with auditable policy reasons.

## Requirements

### Validated

- ✓ v1.0 modernization baseline (policy contracts, async parity, policy decomposition, runtime hardening, observability contracts)
- ✓ v1.1 operational maturity baseline (observability hardening, deployment templates, compatibility matrix, operator forensics, strict override refinement)

### Active

- [ ] Publish formal plugin capability/version compatibility contracts and validation flow.
- [ ] Introduce stronger plugin execution isolation and boundary controls.
- [ ] Define deterministic multi-node policy state distribution and coordination model.
- [ ] Add centralized fleet-level telemetry aggregation and retention controls.

### Out of Scope

- Runtime control-plane web UI productization — milestone focus remains runtime contracts and operator workflows.
- Full protocol expansion beyond HTTP/HTTPS proxy — current customer value remains within existing protocol scope.
- Automatic rollback orchestration — deferred until distributed operations controls are in place.

## Context

Milestones v1.0 and v1.1 are complete and archived in `.planning/milestones/`. The next cycle (v2.0) focuses on extensibility contracts and distributed operations maturity, while preserving backward-compatible proxy behavior and deterministic verification gates.

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
| v2.0 will target extensibility + distributed operations | Next growth risk is plugin/fleet scale, not core policy correctness | — Pending |

---
*Last updated: 2026-02-26 after v2.0 milestone kickoff*
