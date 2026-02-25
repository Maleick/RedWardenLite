# Feature Research

**Domain:** Security reverse proxy / redirector hardening
**Date:** 2026-02-25

## Feature Landscape

### Table Stakes (Users Expect These)

- Deterministic allow/drop/redirect behavior based on explicit policy rules
- Stable support for HTTP/HTTPS listener modes and CONNECT handling
- Reliable header/method/URI gating and ban/allow lists
- Audit-friendly request and decision logging
- Safe handling of TLS interception assets and upstream communication

### Differentiators (Competitive Advantage)

- Behavior-lockdown reason-code test contracts (reduces regression fear)
- Async upstream pipeline with parity guarantees and controlled rollout
- Structured observability (decision counters, latency, upstream error classes)
- Strict runtime profile that enforces safer defaults
- Config validation tool that catches invalid combinations before startup

### Anti-Features (Commonly Requested, Often Problematic)

- Silent behavioral changes to policy decisions without migration notes
- “Magic” auto-learning policy decisions without operator visibility
- Broad architectural rewrites in one milestone

## Feature Dependencies

| Feature | Depends On | Why |
|---------|------------|-----|
| Async upstream fetch | Behavior contract tests | Need parity guard before runtime path change |
| Policy modularization | Locked reason-code semantics | Avoid changing behavior while splitting code |
| Strict runtime mode | Config validation | Must prevent invalid unsafe combinations |
| Metrics and JSON logs | Stable reason/event taxonomy | Metrics dimensions depend on consistent events |

### Dependency Notes

- Behavior contracts are the highest-leverage prerequisite for all internal refactors.
- Observability and strict mode can progress in parallel once config schema and event naming are agreed.

## MVP Definition

### Launch With (v1)

- Complete policy reason contract coverage for active checks
- 4b bugfix and CI regression gate
- Initial structured metrics/log outputs
- Strict mode baseline controls (TLS verify + safe bind guidance)

### Add After Validation (v1.x)

- Async upstream flag rollout with parity report tooling
- Redirector modular split with no semantic changes

### Future Consideration (v2+)

- Advanced config UX (profiles + migration helpers)
- Optional packaging targets (container/service templates)

## Feature Prioritization Matrix

| Feature | User Impact | Risk Reduction | Complexity | Priority |
|---------|-------------|----------------|------------|----------|
| Behavior contract suite | High | Very High | Medium | P0 |
| CI enforcement | High | High | Low | P0 |
| Async parity path | High | High | High | P1 |
| Strict runtime mode | Medium | High | Medium | P1 |
| Structured metrics/logs | Medium | Medium | Medium | P1 |
| Modular policy split | Medium | High | High | P2 |

## Competitor Feature Analysis

- **Nginx/OpenResty + rulesets:** strong performance, but behavior customization often requires more complex Lua/rule authoring.
- **Envoy-based policy layers:** rich observability and control planes, but significantly higher operational complexity.
- **RedWardenLite positioning:** lightweight operator-managed proxy with customizable policy checks; modernization focus should preserve simplicity.

## Sources

- Existing project docs: `README.md`, `.planning/codebase/*.md`, `idea.md`
- HTTP Semantics (RFC 9110): https://www.rfc-editor.org/rfc/rfc9110
