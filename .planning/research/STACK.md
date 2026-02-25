# Stack Research

**Domain:** Brownfield security reverse proxy hardening (RedWardenLite)
**Milestone Context:** Subsequent milestone (existing proxy implementation)
**Date:** 2026-02-25

## Recommended Stack

### Core Technologies

- **Python 3.11+** — Keep primary runtime for compatibility with existing code and operator workflows.
- **Tornado 6.x** — Retain listener/server framework to avoid disruptive transport rewrite.
- **Requests (current) + Async bridge path** — Preserve behavior while introducing a parity-gated async upstream path.

### Supporting Libraries

- **sqlitedict** — Keep for anti-replay and dynamic peer state in current milestone.
- **PyYAML** — Continue as configuration source of truth.
- **pytest** — Contract/regression tests for policy reason behavior.
- **prometheus_client (recommended addition)** — Export simple counters/histograms for operations.
- **structlog or stdlib JSON logging (recommended addition)** — Structured logs without changing existing operator messages abruptly.

### Development Tools

- **GitHub Actions** — Automated `pytest` gate for regressions.
- **ruff + black (recommended future addition)** — Optional consistency tooling after behavior contracts are stable.

## Installation

```bash
# Core
python -m pip install -r requirements.txt

# Supporting
python -m pip install pytest

# Dev dependencies (recommended)
python -m pip install prometheus-client
```

## Alternatives Considered

- **Full migration to `httpx` + asyncio end-to-end now**: deferred to avoid large behavior-surface change before stronger contract coverage.
- **Replacing Tornado with another ASGI stack immediately**: deferred due migration risk and limited near-term value.

## What NOT to Use

- **Large framework rewrites in this milestone** — would mix modernization and migration risk.
- **Unbounded dependency expansion** — keep footprint small and operator-friendly.
- **Breaking config schema changes without compatibility shim** — existing deployments rely on current keys.

## Stack Patterns by Variant

- **Conservative variant:** Keep current runtime/libs; focus on behavior tests + observability.
- **Balanced variant (recommended):** Add async fetch path behind flag + parity tests + structured metrics.
- **Aggressive variant:** Runtime/framework migration plus modular rewrite (not recommended for current phase).

## Version Compatibility

- Python: target 3.11+ in CI while keeping local compatibility where possible.
- Tornado: stay on 6.x line.
- Requests/sqlitedict/PyYAML: maintain compatibility with current requirements and lock behavior before major upgrades.

## Sources

- Tornado docs: https://www.tornadoweb.org/
- Python docs: https://docs.python.org/3/
- Requests docs: https://requests.readthedocs.io/
- Existing codebase map: `.planning/codebase/STACK.md`, `.planning/codebase/ARCHITECTURE.md`
