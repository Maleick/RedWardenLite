# Architecture

**Analysis Date:** 2026-02-25

## Pattern Overview

- Primary pattern: event-driven reverse proxy with a plugin pipeline.
- Runtime model: Tornado request handlers process inbound traffic and then forward upstream using synchronous `requests` calls.
- Extensibility model: plugin interface (`plugins/IProxyPlugin.py`) loaded dynamically by `lib/pluginsloader.py`.
- Policy engine lives in the default `plugins/redirector.py` plugin and decides allow/drop/redirect/proxy behavior.

## Layers

- Bootstrap layer:
- `RedWardenLite.py` initializes options, logger, plugin loader, SSL interception setup, and server sockets.
- Core proxy layer:
- `lib/proxyhandler.py` handles HTTP methods/CONNECT, request normalization, upstream fetch, response encoding, and plugin hooks.
- Plugin layer:
- `plugins/redirector.py` implements request validation, threat heuristics, destination routing, and drop actions.
- Support layer:
- `lib/optionsparser.py`, `lib/proxylogger.py`, `lib/sslintercept.py`, `lib/utils.py`, `lib/ipLookupHelper.py`.

## Data Flow

1. Process starts in `RedWardenLite.py:main()`.
2. CLI/YAML options are merged in `lib/optionsparser.py`.
3. Plugins are loaded/instantiated in `lib/pluginsloader.py`.
4. Tornado accepts request in `ProxyRequestHandler` (`lib/proxyhandler.py`).
5. `request_handler()` invokes each plugin request hook; redirector sets routing/drop metadata.
6. If allowed, proxy fetches upstream response via `requests.request(...)`.
7. `response_handler()` invokes plugin response hooks and adjusts headers/body encoding.
8. Final response is written to the client and access logs are emitted.

## Key Abstractions

- `ProxyRequestHandler` (`lib/proxyhandler.py`) - central request orchestration.
- `IProxyPlugin` (`plugins/IProxyPlugin.py`) - extension contract for request/response hooks.
- `PluginsLoader` (`lib/pluginsloader.py`) - plugin discovery/import/instantiation.
- `SSLInterception` (`lib/sslintercept.py`) - certificate/key preparation and cleanup.
- `IPLookupHelper` + `IPGeolocationDeterminant` (`lib/ipLookupHelper.py`) - external IP metadata resolution and matching.

## Entry Points

- `RedWardenLite.py` -> `main()` (main service executable).
- Tornado HTTP verb handlers in `ProxyRequestHandler` (`get`, `post`, `head`, `options`, `put`, `delete`, `patch`, `propfind`, `connect`).
- Standalone utility entrypoint in `lib/ipLookupHelper.py` -> `main(argv)`.

## Error Handling

- Broad `try/except` blocks are used heavily across request and plugin paths.
- Plugin control flow uses custom exceptions (`DropConnectionException`, `DontFetchResponseException`, `AlterHostHeader`).
- Some failures log and continue (best effort), while fatal bootstrap issues call `logger.fatal()` and exit.

## Cross-Cutting Concerns

- Logging and access accounting in `lib/proxylogger.py` and `lib/proxyhandler.py`.
- Header sanitization and metadata-header stripping in `lib/utils.py` and `RemoveXProxy2HeadersTransform`.
- TLS interception and certificate lifecycle in `lib/sslintercept.py` and `ProxyRequestHandler.generate_ssl_certificate()`.
- Request safety checks (anti-replay, banned words, IP intelligence, expected headers/methods/URIs) in `plugins/redirector.py`.

---

*Architecture analysis: 2026-02-25*
*Update after major request-flow or plugin-interface changes*
