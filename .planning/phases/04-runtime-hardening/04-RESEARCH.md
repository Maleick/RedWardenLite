# Phase 4: Runtime Hardening — Research Notes

## Goal

Implement strict runtime hardening with compatibility-preserving defaults and clear startup validation UX.

## Existing Runtime Shape

- Startup path is orchestrated through:
  - `RedWardenLite.py` -> `lib.proxyhandler.init()`
- Option parsing/config merge is centralized in:
  - `lib/optionsparser.py`
- Upstream HTTP fetch currently disables TLS verification:
  - `lib/proxyhandler.py` (`requests.request(..., verify=False)`)
- Current CI gate runs policy + transport suites and full pytest:
  - `.github/workflows/tests.yml`

## Locked Decisions to Encode

1. Profile model and default:
- `runtime_profile: compatible | strict`
- default `compatible`

2. Strict behavior:
- explicit denylist for unsafe bind/TLS combinations
- global unsafe override + explicit acknowledgement
- aggregate multiple violations and fail once

3. Validation UX:
- human-readable summary by default
- optional JSON report mode
- single stable non-zero exit code
- each finding includes path, reason, safe example

4. Rollout/gating:
- compatible mode warns and continues
- strict mode does not auto-fallback
- contributor-first runbook
- CI hard-fail remains on PR and push

## Implementation Focus

- Add runtime hardening validator module with deterministic outputs.
- Wire validator into startup before serving listeners.
- Make strict profile enforce upstream TLS verification default in transport fetch path.
- Add dedicated tests for hardening evaluation and reporting behavior.
- Keep existing policy/transport external contracts unchanged outside hardening controls.

## Risks and Mitigations

- Risk: startup-flow regressions due to early validation failures.
  - Mitigation: isolate failure to strict-mode checks and explicit override/ack behavior; keep compatible default.

- Risk: breaking existing tests due to changed upstream fetch defaults.
  - Mitigation: strict-only enforcement; compatible remains existing behavior.

- Risk: unclear operator remediation.
  - Mitigation: include path + reason + safe example in all startup findings and runbook.
