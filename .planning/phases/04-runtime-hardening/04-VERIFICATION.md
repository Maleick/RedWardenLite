---
phase: 04-runtime-hardening
verified: "2026-02-25T21:08:00Z"
status: passed
score: 3/3 must-haves verified
---

# Phase 4: runtime-hardening — Verification

## Observable Truths
| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Strict profile enforces secure upstream TLS verification default | passed | `lib/runtime_hardening.py` effective options + `tests/test_runtime_hardening.py::test_strict_mode_enables_upstream_tls_verification_by_default` + `lib/proxyhandler.py` verify propagation |
| 2 | Strict profile denies unsafe bind/TLS combinations with aggregate failure and explicit override acknowledgement requirements | passed | `tests/test_runtime_hardening.py::{test_strict_mode_aggregates_multiple_public_http_listener_violations,test_strict_mode_override_without_ack_fails,test_strict_mode_override_with_ack_allows_startup_and_warns}` |
| 3 | Startup validation UX provides actionable human output and optional JSON output with single failure exit code | passed | `tests/test_runtime_hardening.py::{test_format_report_human_contains_path_reason_and_safe_example,test_format_report_json_is_machine_readable}` + `RUNTIME_HARDENING_EXIT_CODE` |

## Required Artifacts
| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `lib/runtime_hardening.py` | strict profile evaluation, denylist, report formatting | passed | Implements profile normalization, findings aggregation, effective options, and report rendering |
| `lib/proxyhandler.py` | startup hardening integration + strict TLS verify path | passed | Applies hardening report at init and passes effective TLS verify into upstream fetch |
| `lib/optionsparser.py` | runtime hardening CLI/config args | passed | Adds profile, unsafe override, ack, and validation output options |
| `RedWardenLite.py` | runtime hardening defaults | passed | Defaults align to compatible-first rollout |
| `example-config.yaml` | runtime hardening config docs | passed | Includes profile/override/ack/output settings |
| `tests/test_runtime_hardening.py` | SEC behavior tests | passed | Covers profile, denylist, override, and report modes |
| `docs/runtime-hardening.md` | contributor-first runbook | passed | Includes enable/verify/rollback/triage flow |
| `.github/workflows/tests.yml` | explicit runtime hardening CI gate | passed | Adds `tests/test_runtime_hardening.py` hard-fail step |

## Key Link Verification
| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `lib/proxyhandler.py` | `lib/runtime_hardening.py` | startup init validation + effective settings application | passed | runtime hardening applied before plugin/loading flow continues |
| `lib/runtime_hardening.py` | transport fetch behavior | effective `runtime_tls_verify_upstream` | passed | strict profile toggles verified upstream TLS behavior in fetch path |
| `.github/workflows/tests.yml` | `tests/test_runtime_hardening.py` | explicit CI gate step | passed | hard-fail on PR and push |

## Requirements Coverage
| Requirement | Status | Blocking Issue |
|-------------|--------|----------------|
| SEC-01 | passed | |
| SEC-02 | passed | |
| SEC-03 | passed | |

## Result
All Phase 4 must-haves verified.

Validation runs:

- `. .venv/bin/activate && python -m pytest -q tests/test_runtime_hardening.py tests/test_transport_runtime.py tests/test_transport_parity.py` -> `23 passed`
- `. .venv/bin/activate && python -m pytest -q` -> `59 passed`

Verification status: **passed**.
