# Phase 7: Deployment Templates and Compatibility Matrix - Context

**Gathered:** 2026-02-26
**Status:** Ready for planning

## Phase Boundary

Phase 7 delivers repeatable deployment and verification scaffolding for RedWardenLite using host-service and container templates, plus CI compatibility expansion across supported Python versions. This phase does not change policy semantics, request handling contracts, or plugin interface behavior.

## Implementation Decisions

### Deployment Template Scope
- Provide two first-class deployment paths:
  - systemd service template for host-based operation
  - container workflow template (Dockerfile + compose baseline)
- Templates must use explicit config-file mounting/path conventions.
- Templates should default to compatibility-safe runtime profile unless explicitly overridden.

### Upgrade-Safe Smoke Verification
- Add a contributor-first smoke workflow that is executable after upgrade/deploy.
- Smoke flow must include:
  - process health/start checks
  - endpoint reachability checks (`/metrics` and representative proxy path)
  - rollback trigger/checklist if smoke fails
- Commands should be deterministic and shell-copyable.

### CI Compatibility Matrix Policy
- Expand CI Python strategy from single-version to multi-version matrix in this phase.
- Matrix must keep hard-fail contract gates and preserve existing suite ordering.
- Compatibility expansion is limited to supported CPython versions for this codebase.

### Operational UX Expectations
- Documentation should prioritize contributor/operator clarity over exhaustive platform permutations.
- Template docs should include minimal required variables and file paths for quick adoption.

### Claude's Discretion
- Exact template file layout under repository (`deploy/` structure and naming).
- Specific smoke command formatting and sequencing details.
- Exact Python versions selected in CI matrix, provided compatibility intent is met.

## Deferred Ideas

- Kubernetes/Helm deployment packaging.
- Blue/green and canary rollout automation.
- Multi-arch image publishing pipeline.
- End-to-end environment provisioning automation.

---

*Phase: 07-deployment-templates-and-compatibility-matrix*
*Context gathered: 2026-02-26*
