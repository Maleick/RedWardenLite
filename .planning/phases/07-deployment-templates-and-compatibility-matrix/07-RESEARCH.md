# Phase 7: Deployment Templates and Compatibility Matrix — Research Notes

## Goal

Make deployment and upgrade paths repeatable with repository-owned templates and broaden CI validation across supported Python versions.

## Existing Baseline

- No deployment template directory currently exists in the repository.
- Current CI uses a single Python version (`3.11`) in `.github/workflows/tests.yml`.
- Existing docs focus on behavior, transport, runtime hardening, and observability; deployment workflow guidance is minimal.
- Test suite is deterministic and fast (`71` passing tests), making matrix expansion practical.

## Requirement Mapping

### DPLY-01: Deployable templates for host + container
- Add `deploy/systemd` unit template with config path and working directory conventions.
- Add `deploy/container` workflow assets (`Dockerfile`, `docker-compose.yml`, optional env example).
- Keep defaults aligned with existing compatibility mode and explicit config file mounting.

### DPLY-02: Upgrade-safe smoke verification workflow
- Add contributor-focused runbook with explicit post-deploy smoke commands.
- Include start/health checks, endpoint checks, and rollback checklist.
- Ensure commands are deterministic and usable without bespoke infra.

### CI-01: Multi-version Python matrix
- Expand CI strategy to test contract gates on multiple supported CPython versions.
- Preserve hard-fail behavior and suite ordering from current workflow.
- Keep install/test command parity across matrix entries.

## Integration Focus

- Add deployment assets under a dedicated `deploy/` hierarchy.
- Add a deployment runbook describing:
  - template usage
  - smoke verification
  - rollback steps
- Add deterministic tests that validate template artifacts exist and include required directives.
- Update CI matrix in `.github/workflows/tests.yml` and keep observability/runtime/transport gates.

## Constraints

- No runtime behavior drift in request handling/policy semantics.
- No secret values baked into templates or docs.
- Keep templates generic and contributor-first, not environment-specific orchestration.
