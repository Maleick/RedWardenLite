# Phase 2: Async Transport Parity - Research

**Date:** 2026-02-25
**Scope:** Async upstream path introduction with parity and rollback guardrails

## Current Transport Baseline

- Primary upstream fetch currently occurs in `lib/proxyhandler.py` via blocking `requests.request(...)` inside `_my_handle_request`.
- Tornado handlers are `async def`, but they currently call synchronous `my_handle_request()`.
- Existing behavior relies on current response shaping and plugin side effects after upstream fetch.

## Constraints Identified

1. Default behavior must stay legacy-safe.
- Legacy transport semantics in `_my_handle_request` are currently production baseline.
- Any new transport path must be explicit opt-in.

2. Minimal-risk integration point.
- Best insertion point is upstream fetch block in `_my_handle_request` where `fetchurl`, headers, and request body are already prepared.
- Transport mode selection should be isolated from policy plugins to avoid semantic drift.

3. Parity compare must be non-enforcing at runtime.
- Runtime flow should keep primary response untouched and only log/report mismatch events.
- CI hard-fail should be achieved via tests/validation rules, not by changing runtime response semantics.

## Planned Design Direction

- Add explicit transport config defaults in `RedWardenLite.py` and config parsing support in `lib/optionsparser.py`.
- Keep legacy path as baseline implementation.
- Add async path scaffold via asynchronous execution wrapper around upstream fetch, with request-level fallback to legacy on async error.
- Introduce parity helper module to compare status/headers/body and apply static allowlist filtering.
- Emit parity artifacts to `artifacts/parity/` in JSON + Markdown formats.

## Validation Targets

- NET-01: transport mode selection + async fallback behavior.
- NET-02: parity compare + allowlist filtering + artifact emission.
- NET-03: config-driven rollback path + documented smoke verification.

## Out of Scope for This Phase

- Live runtime control plane for mode switching.
- Automatic rollback by mismatch threshold.
- Auto-updating allowlist generation.
- Deep incident forensics playbook.
