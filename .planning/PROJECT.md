# RedWardenLite Evolution

## What This Is

RedWardenLite is a lightweight Python HTTP/HTTPS reverse proxy used to filter, redirect, or proxy traffic based on configurable policies. This project is focused on evolving the existing brownfield codebase into a safer, more testable, and more operable system without breaking established behavior. Primary users are security operators and engineers running policy-gated redirector infrastructure.

## Core Value

Legitimate traffic must pass reliably while non-conformant or suspicious traffic is blocked predictably with auditable policy reasons.

## Requirements

### Validated

- ✓ Multi-port HTTP/HTTPS reverse proxy execution works in production-style host environments — existing
- ✓ Plugin-driven request/response policy pipeline (allow/drop/redirect/proxy) is implemented — existing
- ✓ SSL interception and certificate handling are integrated (`ca-cert`, dynamic cert generation) — existing
- ✓ IP/CIDR, reverse-lookup, and header-based filtering controls are available — existing
- ✓ Access and operational logging paths (Apache2/RedELK formats) are supported — existing

### Active

- [ ] Expand behavior-lockdown tests to cover drop-action and connection side-effect contracts
- [ ] Add async upstream fetch path with parity checks against current behavior
- [ ] Decompose redirector policy logic into smaller maintainable modules
- [ ] Add strict runtime hardening profile (TLS verification + safer operational defaults)
- [ ] Add structured observability outputs (JSON logs and service-level counters)
- [ ] Add first-class config validation and deployment templates for repeatable operations

### Out of Scope

- Full rewrite into a new language/runtime — preserve proven Python/Tornado deployment footprint first
- Major protocol redesign beyond current HTTP/HTTPS reverse-proxy model — not required for current value
- Building a full management UI/control-plane product — focus remains core proxy behavior and operator workflows

## Context

The repository is an actively used brownfield proxy implementation with established policy behavior and operational assumptions. Existing architecture centers around `lib/proxyhandler.py` and `plugins/redirector.py`, with limited modular boundaries and historically minimal automated test coverage. Recent work introduced a policy reason-code behavior-lockdown suite and CI test execution to protect refactors. The immediate roadmap should preserve externally visible behavior while reducing maintenance risk and improving reliability under load.

## Constraints

- **Tech stack**: Python/Tornado codebase remains the primary runtime — avoid disruptive rewrites during this milestone
- **Behavior compatibility**: Existing policy reason semantics must remain stable unless explicitly changed and documented — protects operator expectations
- **Operational safety**: No secrets or sensitive credentials in planning artifacts or prompts — required for secure collaboration
- **Execution style**: Fast iterative delivery (`quick` depth, parallel execution where safe) — supports momentum on modernization backlog

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Incremental brownfield modernization over rewrite | Existing proxy behavior is already deployed and valuable; replacement risk is high | — Pending |
| Lock behavior with tests before major refactors | Prevent regressions while changing high-coupling modules | ✓ Good |
| Initialize with auto workflow in YOLO mode | Reduce setup friction and create full planning baseline in one pass | ✓ Good |

---
*Last updated: 2026-02-25 after initialization*
