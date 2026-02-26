# RedWardenLite Evolution

## What This Is

RedWardenLite is a Python/Tornado HTTP/HTTPS reverse proxy that filters, redirects, or proxies traffic through policy decisions with auditable reason codes. The codebase now has locked behavior contracts, transport parity checks, runtime hardening, and structured observability from milestone v1.0.

## Core Value

Legitimate traffic must pass reliably while non-conformant or suspicious traffic is blocked predictably with auditable policy reasons.

## Requirements

### Validated

- ✓ Policy reason-code and side-effect behavior contracts with deterministic CI gates — v1.0
- ✓ Async transport parity framework with fallback and artifacts — v1.0
- ✓ Internal policy engine decomposition with compatibility facade — v1.0
- ✓ Runtime hardening profile and startup validation UX — v1.0
- ✓ Structured observability events and Prometheus metrics contracts — v1.0

### Active

- [ ] Protect observability surfaces (metrics access and event handling) for production-grade operation
- [ ] Add repeatable deployment templates and upgrade-safe operational packaging
- [ ] Expand CI compatibility matrix across supported Python versions
- [ ] Add operator-deep incident/forensic workflows built on telemetry outputs
- [ ] Refine strict-mode override ergonomics with finer-grained safety controls

### Out of Scope

- Full rewrite into a new runtime/language — maintain Python/Tornado compatibility path
- External control-plane/UI productization — focus remains core proxy runtime and operator workflows
- Distributed multi-node orchestration in this milestone — single-node operational maturity first

## Context

Milestone v1.0 closed all planned phases (1-5) and established a stable baseline of automated verification (`67` tests passing). The next milestone targets operational maturity: safer exposure of telemetry, deployment standardization, broader runtime compatibility validation, and deeper operator runbooks. Existing artifacts in `.planning/milestones/` are the historical source of v1.0 decisions and scope.

## Constraints

- **Tech stack**: Python/Tornado remains the runtime baseline — avoid disruptive stack churn.
- **Compatibility**: External proxy behavior and policy ordering must remain stable unless explicitly versioned.
- **Operational safety**: No secrets in planning artifacts, prompts, logs, or generated docs.
- **Delivery pace**: Keep incremental phase-scoped changes with deterministic verification gates.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Incremental brownfield modernization over rewrite | Existing deployed behavior has value and rewrite risk is high | ✓ Good |
| Behavior-lockdown before major refactors | Prevent regressions while decoupling core modules | ✓ Good |
| Async transport parity before removal of legacy internals | Preserve response contract safety during transport evolution | ✓ Good |
| Strict runtime profile as opt-in first | Reduce rollout risk while introducing hardening controls | ✓ Good |
| v1.1 focus on operational maturity and deployability | Baseline behavior is stable; next risk is operations lifecycle | — Pending |

---
*Last updated: 2026-02-26 after v1.0 milestone completion and v1.1 kickoff*
