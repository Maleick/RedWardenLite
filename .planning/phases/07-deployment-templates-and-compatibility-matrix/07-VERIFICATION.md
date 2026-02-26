---
phase: 07-deployment-templates-and-compatibility-matrix
verified: "2026-02-26T11:20:00Z"
status: passed
score: 3/3 must-haves verified
---

# Phase 7: deployment-templates-and-compatibility-matrix — Verification

## Observable Truths
| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Deploy templates exist for host service and container workflow | passed | `deploy/systemd/redwardenlite.service`, `deploy/container/Dockerfile`, `deploy/container/docker-compose.yml`, `tests/test_deployment_templates.py::test_deployment_template_files_exist` |
| 2 | Upgrade-safe smoke verification workflow is contributor-runnable | passed | `docs/deployment-templates.md` smoke and rollback sections + `tests/test_deployment_templates.py::test_runbook_includes_smoke_and_rollback_steps` |
| 3 | CI executes contract gates across multi-version Python matrix | passed | `.github/workflows/tests.yml` matrix strategy with `3.10/3.11/3.12` and preserved gate steps |

## Required Artifacts
| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `deploy/systemd/redwardenlite.service` | host service template | passed | includes `ExecStart` and config path conventions |
| `deploy/container/Dockerfile` | container build template | passed | installs requirements and runs config-based command |
| `deploy/container/docker-compose.yml` | compose workflow template | passed | includes config mount and artifacts volume |
| `docs/deployment-templates.md` | deployment + smoke runbook | passed | includes host/container flow, smoke checks, rollback, matrix note |
| `tests/test_deployment_templates.py` | deterministic deploy contract tests | passed | validates templates and runbook command anchors |
| `.github/workflows/tests.yml` | multi-version CI matrix | passed | matrix Python versions with hard-fail suite order |

## Requirements Coverage
| Requirement | Status | Blocking Issue |
|-------------|--------|----------------|
| DPLY-01 | passed | |
| DPLY-02 | passed | |
| CI-01 | passed | |

## Result
All Phase 7 must-haves verified.

Validation runs:

- `. .venv/bin/activate && python -m pytest -q tests/test_deployment_templates.py tests/test_observability_contracts.py tests/test_transport_runtime.py tests/test_transport_parity.py` -> `30 passed`
- `. .venv/bin/activate && python -m pytest -q` -> `76 passed`

Verification status: **passed**.
