# RedWardenLite Ideas

**Created:** 2026-02-25
**Purpose:** Fast idea capture + decision workspace for roadmap planning.

## North Star

Build a safer, more observable, and more scalable policy-driven reverse proxy without losing RedWardenLite's simple deployment model.

## Problem Statements

- Request handling currently mixes network transport, policy decisions, logging, and encoding concerns in large files.
- Upstream fetch path is blocking inside Tornado request handling, which limits concurrency under load.
- There is no automated regression suite for policy outcomes.
- Runtime artifacts and secrets-sensitive files are easy to mishandle in operator workflows.

## Idea Backlog

### 1) Async Upstream Fetch Pipeline (High)

- Replace blocking `requests` calls in `lib/proxyhandler.py` with fully async upstream fetches.
- Expected upside: better throughput, less head-of-line blocking, cleaner timeout handling.
- Risk: behavior drift in headers/content-encoding edge cases.
- First spike: implement async fetch behind a feature flag and compare response parity on sample traffic.

### 2) Policy Engine Refactor (High)

- Split `plugins/redirector.py` into focused modules:
- peer identity extraction
- static checks (headers/method/URI)
- IP reputation/geolocation checks
- drop/redirect/proxy action selection
- Expected upside: easier testing and lower change risk.
- Risk: subtle ordering changes in checks.

### 3) Golden Test Matrix for Policy Reasons (High)

- Build tests that assert reason-code behavior for representative requests (`0`, `2`, `3`, `4a`-`4e`, `5`-`8`).
- Include explicit fixtures for headers, methods, URIs, and IP metadata.
- Expected upside: safe refactoring and clearer contract.

### 4) Runtime Hardening Mode (Medium)

- Add strict mode toggles:
- enforce upstream TLS verification
- disallow world-open bind in production profile
- fail startup if key files are too permissive
- Expected upside: safer default production posture.

### 5) Observability Upgrade (Medium)

- Add structured JSON logs and simple counters:
- total requests, allowed, dropped by reason, upstream failures, avg latency
- Optionally expose metrics endpoint.
- Expected upside: faster incident triage and policy tuning.

### 6) Plugin SDK Cleanup (Medium)

- Formalize plugin lifecycle contract and compatibility checks.
- Add plugin sandbox constraints and clearer error isolation.
- Expected upside: safer extension ecosystem and less core coupling.

### 7) Config UX Improvements (Medium)

- Add `redwarden config validate` command with semantic checks and warnings.
- Add starter profiles: `safe-default`, `lab-debug`, `high-throughput`.
- Expected upside: fewer misconfigurations and faster onboarding.

### 8) Packaging + Service Templates (Low)

- Add optional Docker image and systemd unit templates.
- Expected upside: easier reproducible deployment.

## Near-Term Experiments

### Experiment A: Async Fetch Parity

- Goal: prove no functional regression for common traffic patterns.
- Scope: one endpoint path, one plugin-enabled flow, one CONNECT flow.
- Success criteria: status/header/body parity above 99% on replayed fixtures.

### Experiment B: Policy Contract Tests

- Goal: lock current behavior before refactor.
- Scope: reason-code matrix for 15-20 scenarios.
- Success criteria: deterministic pass/fail in CI.

## Open Questions

- Should reason codes be treated as stable external API for operators?
- Do we want strict and permissive runtime profiles, or one profile with warnings?
- Is plugin compatibility a versioned contract or best-effort?
- Should IP intelligence lookups be synchronous, cached async, or fully optional per route?

## Decision Log

- 2026-02-25: Initial backlog seeded from `.planning/codebase/*` map.
- 2026-02-25: Selected direction `1` (Behavior Lockdown First).

## Active Execution Phase: BL-01 Behavior Lockdown

### Objective

Lock current request-policy behavior into automated tests before refactoring performance or architecture.

### Scope

- Build a deterministic policy contract test suite for drop/allow reason codes.
- Add a stable local test harness that does not require real network calls.
- Document how to run behavior-lockdown tests in one command.

### Out of Scope

- Refactoring `lib/proxyhandler.py` or `plugins/redirector.py` internals.
- Throughput/performance optimization.
- New runtime features beyond testing support seams.

### Deliverables

- `tests/` test harness for policy contract scenarios.
- `tests/test_policy_reason_codes.py` covering reason-code matrix.
- Mock/fake helpers for request objects and IP lookup outcomes.
- `docs/testing-behavior-lockdown.md` with execution instructions and scenario list.

### Task Breakdown

1. Test harness foundation
- Add `pytest`-based structure and base fixtures for proxy options and plugin instance construction.
- Ensure tests run offline with no dependency on external IP geolocation APIs.

2. Policy matrix definition
- Capture canonical scenarios for allow/drop paths:
- allow baseline (`reason:0`/`99`)
- header-name/value checks (`2`, `3`)
- blacklist/reverse/ipgeo checks (`4a`, `4b`, `4c`, `4d`, `4e`)
- expected header/value/method/URI checks (`5`, `6`, `7`, `8`)

3. Contract tests implementation
- For each scenario, assert:
- action decision (allow/drop)
- reported reason code
- key side effects (e.g., redirect intent or connection handling when applicable)

4. Stability hardening
- Add deterministic fixtures for time/IP metadata inputs.
- Remove flakiness from random provider selection by monkeypatching provider paths.

5. Documentation and handoff
- Document commands, test layout, and how to add new policy scenarios.
- Record known blind spots and planned follow-up tests.

### Acceptance Criteria

- `pytest -q` executes locally and exits successfully.
- At least 20 policy contract tests pass deterministically.
- Every policy reason family (`0`, `2`, `3`, `4a`-`4e`, `5`-`8`, `99`) has at least one direct assertion.
- No test performs outbound network calls.
- A new contributor can run the suite from docs in under 5 minutes.

### Risks and Mitigations

- Risk: Current code coupling makes direct unit tests difficult.
- Mitigation: test at plugin decision-layer with request mocks and targeted monkeypatching.

- Risk: Ambiguous historical behavior in edge paths.
- Mitigation: capture current observed behavior as baseline; mark unclear cases as pending decisions.

### Execution Order

1. Create fixtures + harness.
2. Implement core reason-code tests (`0`, `5`, `7`, `8`).
3. Add `4x` IP intelligence tests with mocked lookup.
4. Add doc and runbook.
5. Gate future refactors on this suite.
