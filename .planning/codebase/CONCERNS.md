# Codebase Concerns

**Analysis Date:** 2026-02-25

## Tech Debt

- Core request flow is concentrated in very large modules:
- `lib/proxyhandler.py` (~1265 lines)
- `plugins/redirector.py` (~1510 lines)
- Heavy reliance on global mutable state across modules (`options`, `logger`, plugin globals).
- Mixed legacy and modern coding styles increase maintenance overhead.

## Known Bugs

- `lib/optionsparser.py` contains error paths that reference `self.logger` inside standalone functions, which can fail if those branches execute.
- `lib/proxyhandler.py:response_handler` has a `raise` before fallback logic in an exception block, making subsequent code unreachable.
- Runtime artifacts (`.anti-replay.sqlite`, `.peers.sqlite`, `ip-lookups-cache.json`) are written in working directory and may persist unexpectedly across runs.

## Security Considerations

- TLS verification is globally disabled in multiple paths (`verify=False` in requests; unverified SSL context), which weakens upstream authenticity checks.
- Repository includes key/cert material under `ca-cert/` and operational handling around private key files; accidental key reuse/exposure risk should be managed.
- Service can act as an open proxy depending on bind/port/policy choices if deployed without network controls.
- Dynamic plugin loading from filesystem paths increases risk surface if plugin sources are not trusted.

## Performance Bottlenecks

- Tornado request handler uses blocking `requests` I/O in hot path, limiting concurrency under load.
- Frequent sqlite and file writes (logging, peer tracking, replay tracking, lookup cache) can become I/O bottlenecks.
- Optional external IP metadata lookups can add latency and provider throttling behavior.

## Fragile Areas

- Complex header mutation logic (`override_host_header`, encoding overrides, metadata strip headers) is easy to regress.
- Drop/allow behavior is distributed across many policy checks with early returns in `plugins/redirector.py`.
- Exception-driven control flow between plugin and handler layers is tightly coupled and difficult to reason about.

## Scaling Limits

- Architecture is host-local and process-bound; no built-in horizontal coordination for replay/whitelist state.
- Multi-process mode uses local process forks without shared distributed state.
- No queueing/backpressure controls for high-volume proxy workloads.

## Dependencies at Risk

- `requirements.txt` has unpinned versions, so dependency upgrades may introduce runtime drift.
- Third-party API dependencies (`ip-api.com`, `ipapi.co`, `ipgeolocation.io`) are availability and rate-limit sensitive.
- OpenSSL CLI dependency is assumed available on host for MITM cert operations.

## Missing Critical Features

- Automated tests and CI quality gates are absent.
- No health-check endpoint or structured metrics export for service observability.
- No explicit auth/rate-limit layer to protect administrative or high-risk deployment modes.

## Test Coverage Gaps

- No automated regression coverage for policy reason-code matrix (0..8 and 4a/4b/4c/4d/4e).
- No automated compatibility tests for HTTP encodings (`gzip`, `deflate`, `br`) and CONNECT handling.
- No failure-injection tests around upstream timeouts, DNS failures, malformed headers, and plugin exceptions.

---

*Concerns analysis: 2026-02-25*
*Update after hardening, refactors, and test adoption*
