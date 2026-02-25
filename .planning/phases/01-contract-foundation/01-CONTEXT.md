# Phase 1: Contract Foundation - Context

**Gathered:** 2026-02-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 delivers contract foundation for behavior-lockdown quality gates (reason codes plus core side effects) and does not add new product capabilities.

</domain>

<decisions>
## Implementation Decisions

### Contract Coverage Strategy
- Use existing tests, CI workflow, and runbook as baseline and close only remaining gaps.
- Lock behavior on both allow/drop reason outcomes and core side-effect contracts.
- Keep tests deterministic and offline.

### Core Side-Effect Contract Scope
- Lock `drop_action` externally observable outcomes for `reset`, `redirect`, and `proxy`.
- Lock connection behavior expectations where policy dictates keep-alive versus connection drop.
- Lock host-header override semantics, including `expected_headers_value` host handling.
- Defer extended encoding/decompression/header-strip edge contracts beyond this core scope.

### CI Gate Policy
- Enforce hard-fail behavior on `pytest` failures.
- Require gate on both `pull_request` and `push`.
- Keep current single Python-version gate for this phase; matrix expansion is deferred.

### Runbook Scope
- Contributor-first runbook focus:
  - local setup and one-command verification
  - targeted versus full-suite commands
  - failure triage checklist
  - adding new contract scenario checklist
- Defer operator-deep incident forensics to later phases.

### Claude's Discretion
- Test organization and fixture naming.
- Exact wording and format of runbook sections.
- Minor CI step ergonomics, as long as gate semantics remain unchanged.

</decisions>

<specifics>
## Specific Ideas

- Gap-closure execution mode for this pass.
- Auto chain is full sequence: discuss -> plan -> execute.
- Side-effect contract focus includes drop action behavior, keep-alive/drop semantics, and host-header override behavior.

</specifics>

<deferred>
## Deferred Ideas

- Extended side-effect contracts for encoding/decompression/header-strip edge matrix.
- Multi-version Python CI matrix.
- Operator-deep incident and forensic procedures.

</deferred>

---

*Phase: 01-contract-foundation*
*Context gathered: 2026-02-25*
