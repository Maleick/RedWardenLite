# Coding Conventions

**Analysis Date:** 2026-02-25

## Naming Patterns

- Modules and most functions use snake_case (`parse_options`, `drop_check`, `connect_relay`).
- Classes use CamelCase (`ProxyRequestHandler`, `PluginsLoader`, `IPLookupHelper`).
- Config keys are lowercase snake_case in YAML (`drop_request_without_expected_http_method`).
- Plugin metadata headers are centralized in lowercase-key dictionaries (`proxy2_metadata_headers`).

## Code Style

- Codebase favors pragmatic, script-style Python over strict style-guide enforcement.
- Global mutable state is common (`options`, `logger`, `pluginsloaded`, `sslintercept`).
- Extensive inline comments and operational notes explain security policy behavior.
- String formatting is mixed (`f"..."`, `format(...)`, and concatenation coexist).

## Import Organization

- Standard library and third-party imports are often mixed in the same block.
- Core modules import each other directly (for example `lib/proxyhandler.py` imports `lib.*` and plugin modules).
- Dynamic plugin import uses `__import__` + `sys.path` manipulation in `lib/pluginsloader.py`.

## Error Handling

- Broad `try/except` guards are preferred around network/IO/plugin operations.
- Plugin flow intentionally uses exceptions as control signals:
- `DropConnectionException`
- `DontFetchResponseException`
- `ProxyPlugin.AlterHostHeader`
- Debug mode toggles whether some exceptions are re-raised or only logged.

## Logging

- Unified logging facade: `ProxyLogger` in `lib/proxylogger.py`.
- Severity-oriented methods: `info`, `dbg`, `trace`, `err`, `fatal`.
- Plugin instances receive an injected prefixed logger (`PluginsLoader.InjectedLogger`).
- Request lifecycle logs are emitted in `lib/proxyhandler.py` and policy logs in `plugins/redirector.py`.

## Comments

- Comments are used heavily to explain intent, policy reason codes, and operational caveats.
- Many comments retain historical context from upstream RedWarden behavior.
- Comment density is highest in config and redirector policy sections.

## Function Design

- Functions tend to be imperative and side-effect heavy (mutating request/response objects in-place).
- Large multi-responsibility methods exist in hot paths (`_my_handle_request`, `drop_check`, `_client_request_inspect`).
- Helper methods inside large modules encapsulate policy checks but remain tightly coupled to shared object state.

## Module Design

- `lib/proxyhandler.py` is a central orchestrator module with high coupling.
- `plugins/redirector.py` embeds both policy configuration handling and runtime decision logic.
- Utility modules (`lib/utils.py`, `lib/sslintercept.py`) provide focused functionality but rely on global/shared configuration patterns.
- No formal lint/format tooling configuration was found; conventions are maintained manually.

---

*Conventions analysis: 2026-02-25*
*Update after style standardization or refactors*
