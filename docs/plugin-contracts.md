# Plugin Contracts Runbook

## Purpose

Phase 9 introduces explicit plugin compatibility contracts and deterministic plugin runtime isolation boundaries.

## Config Surface

- `plugin_api_version: "<major.minor>"`
- `plugin_require_capabilities: true|false`
- `plugin_isolation_enabled: true|false`
- `plugin_isolation_failure_mode: fail_closed | fail_open`

Defaults:

- `plugin_api_version: "1.0"`
- `plugin_require_capabilities: true`
- `plugin_isolation_enabled: true`
- `plugin_isolation_failure_mode: fail_closed`

## Metadata Schema

Each plugin must declare metadata via `PLUGIN_METADATA` (or `get_metadata()`):

- `schema_version`
- `plugin_name`
- `plugin_version`
- `core_api_version`
- `capabilities` (list of capability strings)

Loader validates schema and compatibility at plugin load time.

## Compatibility Rules

1. `plugin_name` must match plugin module name.
2. `plugin_version` must be non-empty.
3. `capabilities` must contain at least one capability.
4. `core_api_version` must be compatible with runtime `plugin_api_version` (major version match).

If validation fails:

- plugin load is rejected deterministically
- startup logs explicit compatibility error context

## Runtime Isolation Semantics

When plugin handler execution fails:

- `fail_closed`: request/response path is dropped with explicit plugin isolation error logging.
- `fail_open`: proxy continues using unmodified request/response state for that plugin boundary.

## Verification Commands

```bash
. .venv/bin/activate
python -m pytest -q tests/test_plugin_contracts.py
python -m pytest -q
```

## CI Gate

CI runs plugin contract tests as a hard-fail gate on both `push` and `pull_request` before the full suite.
