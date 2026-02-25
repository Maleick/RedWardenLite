# Phase 4: Runtime Hardening - Context

**Gathered:** 2026-02-25
**Status:** Ready for planning

## Phase Boundary

Phase 4 delivers secure-by-default runtime hardening controls for startup/runtime safety: strict profile activation, unsafe bind/TLS combination rejection, and startup config validation with actionable failure messaging. This phase does not add new proxy features, plugin interfaces, or control-plane capabilities.

## Implementation Decisions

### Profile Activation and Scope
- Runtime profile model is a single explicit enum: `compatible | strict`.
- Default profile remains `compatible` to preserve backward compatibility.
- Strict profile scope in this phase is limited to `SEC-01`, `SEC-02`, and `SEC-03` only.
- In `compatible` profile, unsafe settings emit migration warnings and startup continues.

### Unsafe Bind/TLS Policy
- Strict mode uses an explicit denylist of unsafe bind/TLS combinations.
- Strict-mode bypass is a single global override (`runtime_hardening_allow_unsafe`).
- Unsafe override requires explicit acknowledgement string (`runtime_hardening_unsafe_ack`), non-empty.
- Multiple strict-mode findings are aggregated and reported together; startup fails once.

### Validation and Failure UX
- Default startup validation failure output is human-readable grouped summary.
- Optional structured output mode is JSON (`runtime_hardening_validation_output: json`).
- Startup hardening/validation failures use one stable non-zero exit code.
- Every failure entry includes setting path, why it failed, and a safe replacement example.

### Rollout and Gating
- Rollout posture is opt-in strict with migration warnings in compatible mode.
- Runbook depth is contributor-first (enable/verify/rollback + concise triage).
- CI enforcement remains hard-fail on both `push` and `pull_request`.
- If strict validation fails, there is no automatic fallback to compatible mode.

### Claude's Discretion
- Exact runtime warning/error wording as long as required fields are present.
- Test fixture names and helper structure for runtime hardening tests.
- Minor CLI help text ergonomics and docs section ordering.

## Specific Ideas

- Config surface additions should align with established option naming style in codebase.
- Runtime hardening behavior should preserve unrelated transport and policy semantics.
- Compatibility warnings should guide operators toward strict-mode migration without blocking startup.

## Deferred Ideas

- Strict-by-default rollout.
- Per-check unsafe override granularity.
- Risk-score-based unsafe policy decisions.
- Automatic strict-to-compatible runtime fallback.
- Operator-deep forensic runbook expansion.

---

*Phase: 04-runtime-hardening*
*Context gathered: 2026-02-25*
