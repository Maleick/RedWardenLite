# Phase 9: Plugin Capability Contracts and Isolation Boundaries — Research Notes

## Goal

Formalize plugin compatibility contracts and enforce deterministic runtime isolation semantics for plugin execution failures.

## Existing Baseline

- Plugins are loaded by `lib/pluginsloader.py` using module import + class lookup (`plugin_class_name`).
- Interface inheritance (`IProxyPlugin`) is checked, but no formal capability/version metadata is validated.
- Runtime plugin execution in `lib/proxyhandler.py` has inconsistent exception handling:
  - request path catches limited exception classes and often continues
  - response path has fragile exception branch behavior
- No dedicated plugin contract test suite or CI gate exists.

## Requirement Mapping

### EXT-01: Formal plugin capability/version compatibility metadata
- Add repository-owned metadata schema and loader-time validator.
- Validate plugin metadata deterministically at load boundaries.
- Ensure built-in `redirector` plugin declares explicit metadata.

### EXT-02: Stronger plugin isolation boundaries
- Add explicit runtime isolation controls around plugin request/response handlers.
- Ensure deterministic fail-closed/fail-open behavior and explicit logging semantics.
- Keep behavior-lockdown suites and existing plugin-facing proxy semantics stable.

## Integration Focus

- Metadata schema + validation:
  - `lib/pluginsloader.py`
  - `plugins/IProxyPlugin.py` (contract helper access)
  - `plugins/redirector.py` (built-in metadata declaration)
- Runtime isolation execution boundaries:
  - `lib/proxyhandler.py`
- Config/CLI surface:
  - `RedWardenLite.py`
  - `lib/optionsparser.py`
  - `example-config.yaml`
- Tests + CI:
  - new `tests/test_plugin_contracts.py`
  - `.github/workflows/tests.yml`
- Runbook:
  - new `docs/plugin-contracts.md`

## Constraints

- No policy ordering changes.
- No proxy endpoint/transport behavior regressions.
- Keep tests deterministic/offline and independent of external plugin registries.
- Keep default behavior secure and explicit (deterministic isolation + strict metadata checks).
