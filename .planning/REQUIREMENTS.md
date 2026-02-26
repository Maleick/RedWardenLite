# Requirements: RedWardenLite Evolution

**Defined:** 2026-02-26
**Core Value:** Legitimate traffic must pass reliably while non-conformant or suspicious traffic is blocked predictably with auditable policy reasons.

## v1.1 Requirements

### Observability Hardening

- [x] **OBSX-01**: Metrics endpoint access can be restricted by explicit runtime configuration suitable for production deployment.
- [x] **OBSX-02**: Structured event sink lifecycle (path/retention/rotation expectations) is documented and verifiable through contributor commands.
- [x] **OBSX-03**: Event emission supports configurable sampling controls without breaking existing schema contracts.

### Delivery and Compatibility

- [ ] **DPLY-01**: Project ships deployable templates for standard host operation (systemd and container workflow).
- [ ] **DPLY-02**: Upgrade-safe smoke verification workflow is documented and runnable by contributors.
- [ ] **CI-01**: CI runs contract suites across a supported multi-version Python matrix.

### Operations and Runtime Safety

- [ ] **OPS-01**: Contributor runbooks include operator-deep triage and forensic collection steps for policy, transport, and observability incidents.
- [ ] **OPS-02**: Incident evidence bundle procedure is documented with deterministic artifact expectations.
- [ ] **SECX-01**: Strict runtime unsafe override controls support finer-grained per-check acknowledgement semantics.
- [ ] **SECX-02**: Strict-mode migration guidance includes explicit remediation examples for each denied check.

## v2 Requirements

### Extensibility

- **EXT-01**: Formal plugin capability/version compatibility metadata.
- **EXT-02**: Stronger plugin isolation and execution boundary controls.

### Distributed Operations

- **DIST-01**: Multi-node policy state distribution and coordination model.
- **DIST-02**: Centralized fleet-level telemetry aggregation and retention controls.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Runtime control-plane web UI | Not required to deliver v1.1 operational maturity goals |
| Full protocol expansion beyond HTTP/HTTPS proxy | Current customer value is served by existing protocol scope |
| Automatic rollback orchestration | Deferred until incident telemetry and deployment templates are hardened |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| OBSX-01 | Phase 6 | Complete |
| OBSX-02 | Phase 6 | Complete |
| OBSX-03 | Phase 6 | Complete |
| DPLY-01 | Phase 7 | Pending |
| DPLY-02 | Phase 7 | Pending |
| CI-01 | Phase 7 | Pending |
| OPS-01 | Phase 8 | Pending |
| OPS-02 | Phase 8 | Pending |
| SECX-01 | Phase 8 | Pending |
| SECX-02 | Phase 8 | Pending |

**Coverage:**
- v1.1 requirements: 10 total
- Mapped to phases: 10
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-26*
*Last updated: 2026-02-26 after Phase 6 completion*
