# Pitfalls Research

**Domain:** Brownfield reverse proxy hardening
**Date:** 2026-02-25

## Critical Pitfalls

### Pitfall 1: Refactoring Before Behavioral Lockdown

**Why it hurts:** Internal cleanup silently changes allow/drop semantics and breaks operator expectations.

**Warning signs:**
- Reason-code changes discovered only after deployment
- Tests assert implementation details, not outcome contracts

**Prevention:**
- Lock reason-code behavior with matrix tests first
- Require CI pass for contract suites before merge

### Pitfall 2: Async Migration Without Parity Instrumentation

**Why it hurts:** Throughput improves but edge behavior shifts (headers/encoding/timeout semantics).

**Warning signs:**
- Increased upstream errors after transport changes
- Divergent response metadata across old/new path

**Prevention:**
- Feature flag async path
- Compare parity against current path for sampled traffic

### Pitfall 3: Security Hardening as a One-Off Toggle

**Why it hurts:** Inconsistent deployments and false sense of safety.

**Warning signs:**
- Mixed TLS verification posture across environments
- Operators unsure which settings are mandatory

**Prevention:**
- Introduce explicit strict profile
- Add config validation with actionable failures

## Technical Debt Patterns

- Large multipurpose methods in `proxyhandler` and `redirector`
- Global mutable state shared across modules
- Error handling via broad exception blocks in critical paths

## Integration Gotchas

- External IP lookup providers have rate limits and availability variance.
- Reverse-DNS behavior depends on environment and can be inconsistent in tests.
- File-backed sqlite state can conflict with ephemeral container environments.

## Performance Traps

- Blocking upstream requests in request handler hot path.
- Excessive per-request disk I/O from logging/state updates.
- Heavy debug logging in high-throughput scenarios.

## Security Mistakes

- Running with TLS verification disabled in production contexts.
- Storing CA/private key materials without strict operational controls.
- Treating proxy as open-access edge without network boundary controls.

## UX Pitfalls

- Policy actions not clearly explainable to operators.
- Config options with ambiguous interactions.
- Failure messages that do not identify violating requirement/rule.

## "Looks Done But Isn't" Checklist

- Contracts pass locally and in CI, including known edge policies.
- Strict profile tested in realistic deployment config.
- Metrics/logs include enough dimensions for incident triage.
- Rollback path documented for transport-layer changes.

## Recovery Strategies

- Keep feature flags for risky path changes.
- Maintain behavior snapshots and quick rollback commits.
- Stage deployments with synthetic and real traffic checks.

## Pitfall-to-Phase Mapping

| Pitfall | Phase to Address |
|---------|------------------|
| Behavior drift during refactor | Phase 1/2 |
| Async parity mismatch | Phase 2 |
| Incomplete hardening controls | Phase 3 |
| Low observability during incidents | Phase 3/4 |

## Sources

- `.planning/codebase/CONCERNS.md`
- `idea.md`
- OWASP ASVS: https://owasp.org/www-project-application-security-verification-standard/
