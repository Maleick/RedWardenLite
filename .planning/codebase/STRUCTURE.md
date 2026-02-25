# Codebase Structure

**Analysis Date:** 2026-02-25

## Directory Layout

```text
/opt/RedWardenLite
├── RedWardenLite.py
├── README.md
├── requirements.txt
├── example-config.yaml
├── lib/
├── plugins/
├── data/
├── ca-cert/
└── resources/
```

## Directory Purposes

- `lib/` - core runtime modules (request handling, option parsing, SSL setup, logging, plugin loading, utility helpers).
- `plugins/` - plugin interface and default redirector implementation.
- `data/` - static policy wordlists/CIDR lists consumed by redirector logic.
- `ca-cert/` - certificate/key material used for HTTPS interception defaults.
- `resources/` - documentation image assets.

## Key File Locations

- Service entrypoint: `RedWardenLite.py`.
- Main request orchestration: `lib/proxyhandler.py`.
- CLI + YAML configuration merging: `lib/optionsparser.py`.
- Plugin loading mechanism: `lib/pluginsloader.py`.
- Plugin contract: `plugins/IProxyPlugin.py`.
- Default policy/plugin implementation: `plugins/redirector.py`.
- IP intelligence helper: `lib/ipLookupHelper.py`.
- SSL setup/cleanup: `lib/sslintercept.py`.
- Example runtime config: `example-config.yaml`.

## Naming Conventions

- Snake case dominates functions/variables (for example `drop_request_without_expected_uri`).
- Module names are lowercase (for example `proxyhandler.py`, `pluginsloader.py`).
- Class names use `CamelCase` (`ProxyRequestHandler`, `PluginsLoader`, `ProxyPlugin`).
- Some legacy naming remains (`IProxyPlugin.py`, mixed acronyms and underscores in config keys).

## Where to Add New Code

- New proxy behavior rule: extend `plugins/redirector.py` or add a new plugin in `plugins/` implementing `IProxyPlugin`.
- New plugin-wide options: update `help()` in plugin and `lib/optionsparser.py` integration flow.
- Core transport/proxy behavior changes: `lib/proxyhandler.py`.
- New runtime utility helpers: `lib/` module(s) with imports from handler/plugin layers.
- New static rule data: `data/` with matching config references.

## Special Directories

- `ca-cert/` stores key/cert material and should be treated as sensitive runtime input.
- Repository root currently includes operational files generated/consumed at runtime (logs, sqlite files) depending on execution path.
- No dedicated `tests/` or CI configuration directory is present.

---

*Structure analysis: 2026-02-25*
*Update after module moves, new directories, or plugin additions*
