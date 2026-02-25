# Architecture Research

**Domain:** Brownfield policy-proxy architecture
**Date:** 2026-02-25

## Standard Architecture

### System Overview

Recommended near-term architecture keeps current runtime topology but introduces clearer boundaries:

- **Edge Listener Layer** (`RedWardenLite.py`, Tornado setup)
- **Request Orchestration Layer** (`lib/proxyhandler.py`)
- **Policy Evaluation Layer** (`plugins/redirector.py` split over time)
- **State/Lookup Layer** (`sqlitedict` stores + `ipLookupHelper`)
- **Observability Layer** (existing logs + structured counters)

This preserves deployment familiarity while reducing coupling risk.

### Component Responsibilities

- **Listener:** socket bind, protocol mode setup, worker process model.
- **Handler:** request normalization, plugin hook orchestration, upstream fetch pipeline.
- **Policy Engine:** pure decision checks, reason-code generation, action directives.
- **Actions:** translate decision into drop/redirect/proxy behavior.
- **Telemetry:** emit decision and latency signals without altering outcome.

## Recommended Project Structure

```text
lib/
  proxyhandler.py
  policy/
    checks.py
    actions.py
    context.py
  observability/
    metrics.py
    events.py
plugins/
  redirector.py (facade + compatibility layer)
```

### Structure Rationale

- Incremental extraction enables safer diffs than replacing the plugin wholesale.
- Facade keeps existing plugin contract stable during decomposition.

## Architectural Patterns

### Pattern 1: Compatibility Facade

Keep `ProxyPlugin` as the public entry point, delegate internal checks to extracted modules. This allows one-change-at-a-time migration while preserving behavior.

### Pattern 2: Decision-then-Action Separation

Split "should we drop?" from "how do we drop?" so tests validate decisions independently from transport side effects.

### Pattern 3: Feature-Flagged Transport Evolution

Introduce async upstream fetch behind explicit flags and parity instrumentation before default switch.

## Data Flow

### Request Flow

Client request -> Tornado handler -> policy checks -> action selection -> upstream fetch/response -> client response -> telemetry/logs.

### State Management

- Runtime short-lived request state in handler/plugin objects.
- Persistent lightweight state in sqlite dict files for replay and dynamic peer tracking.

### Key Data Flows

- **Policy signal flow:** checks produce reason codes and action intent.
- **Observability flow:** request metadata + outcome -> counters/log entries.

## Scaling Considerations

- Current blocking upstream calls constrain concurrency under load.
- File-backed state/logging can become I/O bottlenecks with traffic spikes.
- Async transport path and selective telemetry batching are highest-return improvements.

### Scaling Priorities

1. Preserve correctness via contracts.
2. Reduce blocking upstream path.
3. Add low-cost metrics for saturation visibility.

## Anti-Patterns

### Anti-Pattern 1: Mixed Decision + Side-Effect Logic in Monolithic Methods

Hard to test and easy to regress; favors accidental coupling.

### Anti-Pattern 2: Cross-cutting Behavior Changes Without Contract Coverage

Creates brittle releases and unclear rollback paths.

## Integration Points

### External Services

- Upstream destination hosts
- Optional IP metadata providers (`ip-api.com`, `ipapi.co`, `ipgeolocation.io`)

### Internal Boundaries

- Plugin API contract (`IProxyPlugin`) must remain stable during refactor.
- Config parsing and policy evaluation should evolve with compatibility protections.

## Sources

- `.planning/codebase/ARCHITECTURE.md`
- `lib/proxyhandler.py`, `plugins/redirector.py`
- Tornado docs: https://www.tornadoweb.org/
