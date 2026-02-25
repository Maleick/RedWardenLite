# Phase 2: Async Transport Parity - Context

**Gathered:** 2026-02-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 2 introduces an async upstream fetch path with parity guardrails and rollback-by-config while preserving existing external proxy behavior by default.

</domain>

<decisions>
## Implementation Decisions

### Activation and Rollout
- Async transport remains behind explicit configuration control.
- `transport_mode` supports `legacy`, `async`, and `auto`.
- Default behavior remains legacy unless explicitly configured otherwise.
- `auto` mode is only active when explicitly configured; runtime may choose path dynamically.
- Toggle mechanism is config-only (no runtime admin switch).
- If async fetch errors, fallback to legacy for that request and log structured reason.
- Parity checks run in shadow mode and do not change live response behavior.

### Parity Contract
- Status parity must match exactly.
- Header parity is strict over a filtered set that excludes hop-by-hop and known volatile headers.
- Body parity is byte-exact after content-decoding normalization.
- Allowed differences are controlled by a static allowlist stored in-repo.

### Mismatch Handling and Reporting
- On parity mismatch, serve primary path response and record mismatch evidence.
- CI should hard-fail on non-allowlisted mismatches.
- Parity output format is both JSON and Markdown.
- Default parity artifact path is `artifacts/parity/`.

### Rollback Semantics
- Canonical rollback is config toggle back to legacy with restart.
- Rollback trigger policy is manual operator decision; request-level async errors already fallback to legacy.
- Rollback readiness requires executable smoke command and runbook guidance.
- Runbook depth is contributor-first (enable/verify/rollback + concise triage).

### Claude's Discretion
- Test fixture naming and helper structure.
- Exact report field formatting for JSON/Markdown parity artifacts.
- Minor implementation ergonomics that do not change locked semantics.

</decisions>

<specifics>
## Specific Ideas

- Add transport/parity config surface with default-safe values.
- Keep legacy synchronous requests path as behavioral baseline.
- Build parity as non-enforcing shadow check with explicit allowlist filtering.

</specifics>

<deferred>
## Deferred Ideas

- Runtime hot-switch transport control plane.
- Auto-learning parity allowlist updates.
- Automatic mismatch-threshold rollback.
- Deep incident forensics runbook.

</deferred>

---

*Phase: 02-async-transport-parity*
*Context gathered: 2026-02-25*
