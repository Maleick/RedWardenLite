# Phase 1: Contract Foundation - Research

**Date:** 2026-02-25
**Scope:** Gap closure for reason-code plus core side-effect contracts

## Baseline Inventory

- Reason-code matrix exists in `tests/test_policy_reason_codes.py` and currently covers `0,1,2,3,4a,4b,4c,4d,4e,5,6,7,8,99`.
- CI workflow exists in `.github/workflows/tests.yml` with `push` and `pull_request` triggers and a single Python version.
- Behavior-lockdown runbook exists in `docs/testing-behavior-lockdown.md`.

## Gaps Against Locked Context

1. Core side-effect contracts are only partially locked.
- Missing explicit tests for `drop_action` observable outcomes across `reset`, `redirect`, and `proxy` paths.
- Missing explicit keep-alive/drop behavior assertions around request drop/allow handling.

2. Host-header override semantics need explicit negative-path locking.
- Positive path is covered (`host` match sets override metadata header).
- Missing explicit mismatch-path assertion that reason `6` drops and does not set override metadata.

3. Contributor-first runbook can be made more explicit.
- Current runbook includes run commands and extension notes.
- Missing clearly sectioned local setup, one-command verification, failure triage checklist, and add-scenario checklist flow.

## Implementation Approach

- Preserve current behavior; add deterministic offline tests only.
- Keep CI policy semantics unchanged (`push` + `pull_request`, hard-fail on pytest).
- Refine runbook wording and structure for contributor-first usage.

## Out of Scope for This Phase

- Extended encoding/decompression/header-strip side-effect matrix.
- Multi-version Python CI matrix.
- Operator-deep incident forensics.
