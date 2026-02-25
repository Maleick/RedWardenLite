# Requirements: RedWardenLite Evolution

**Defined:** 2026-02-25
**Core Value:** Legitimate traffic must pass reliably while non-conformant or suspicious traffic is blocked predictably with auditable policy reasons.

## v1 Requirements

### Platform Stability

- [x] **PLAT-01**: Policy reason-code behavior is covered by automated regression tests for all active drop/allow rule families
- [x] **PLAT-02**: CI runs the behavior-lockdown suite on every pull request and push
- [x] **PLAT-03**: Operators and contributors have a documented runbook for behavior-lockdown verification

### Transport

- [x] **NET-01**: Async upstream fetch path can be enabled behind an explicit configuration flag
- [x] **NET-02**: Async and legacy fetch paths can be compared with parity checks for status, headers, and body behavior
- [x] **NET-03**: Legacy transport path remains immediately recoverable via configuration rollback

### Policy Engine

- [x] **POL-01**: Redirector policy checks are decomposed into maintainable units without changing externally observable outcomes
- [x] **POL-02**: Decision logic and action side effects are separated so policy outcomes are independently testable
- [x] **POL-03**: Existing plugin interface behavior remains backward compatible for current deployments

### Security Hardening

- [ ] **SEC-01**: Strict runtime mode enforces upstream TLS verification by default
- [ ] **SEC-02**: Strict runtime mode prevents unsafe listener/bind settings unless explicitly overridden
- [ ] **SEC-03**: Configuration validation fails fast on insecure or conflicting security options

### Observability

- [ ] **OBS-01**: Structured logs emit stable fields for request outcome and reason code
- [ ] **OBS-02**: Metrics expose request totals, allow/drop counts by reason, upstream failure counts, and latency
- [ ] **OBS-03**: Operational telemetry supports incident triage without enabling verbose debug logging

## v2 Requirements

### Configuration UX

- **CFG-01**: Provide opinionated config profiles (safe-default, lab-debug, high-throughput)
- **CFG-02**: Add guided migration hints when configuration schema evolves

### Delivery Ergonomics

- **DPLY-01**: Publish container and service templates for standard deployment patterns
- **DPLY-02**: Add packaging guidance for environment-specific operations

### Advanced Extensibility

- **EXT-01**: Formalize plugin capability/version compatibility metadata
- **EXT-02**: Add stronger plugin isolation controls

## Out of Scope

| Feature | Reason |
|---------|--------|
| Full language/runtime rewrite | High migration risk relative to near-term value |
| New control-plane web UI | Not required to deliver core proxy modernization goals |
| Cross-region distributed state control | Operationally heavy and not required for this milestone |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PLAT-01 | Phase 1 | Complete |
| PLAT-02 | Phase 1 | Complete |
| PLAT-03 | Phase 1 | Complete |
| NET-01 | Phase 2 | Complete |
| NET-02 | Phase 2 | Complete |
| NET-03 | Phase 2 | Complete |
| POL-01 | Phase 3 | Complete |
| POL-02 | Phase 3 | Complete |
| POL-03 | Phase 3 | Complete |
| SEC-01 | Phase 4 | Pending |
| SEC-02 | Phase 4 | Pending |
| SEC-03 | Phase 4 | Pending |
| OBS-01 | Phase 5 | Pending |
| OBS-02 | Phase 5 | Pending |
| OBS-03 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-25*
*Last updated: 2026-02-25 after Phase 3 completion*
