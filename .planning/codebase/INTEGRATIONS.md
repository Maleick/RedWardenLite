# External Integrations

**Analysis Date:** 2026-02-25

## APIs & External Services

- Upstream destination backends are configured through `destination_url` in `example-config.yaml`; requests are forwarded via `requests.request(...)` in `lib/proxyhandler.py`.
- Optional redirect/proxy fallback targets are configured through `action_url` in `example-config.yaml`.
- Optional IP intelligence providers used by `lib/ipLookupHelper.py`:
- `http://ip-api.com/json/<ip>`
- `https://ipapi.co/<ip>/json/`
- `https://api.ipgeolocation.io/ipgeo` (API key optional)
- DNS resolution and reverse lookup via `socket.gethostbyname`/`socket.gethostbyaddr`.

## Data Storage

- Local SQLite-backed stores via `sqlitedict`:
- `.anti-replay.sqlite` for replay-hash tracking (`plugins/redirector.py`).
- `.peers.sqlite` for dynamic peer whitelist and throttling stats (`plugins/redirector.py`, `lib/proxyhandler.py`).
- Local JSON cache file `ip-lookups-cache.json` for IP metadata (`lib/ipLookupHelper.py`).
- Flat-file policy data loaded from `data/*.txt` (banned words and CIDRs).

## Authentication & Identity

- No built-in user authentication for clients connecting to the proxy listeners.
- Identity-like gating is policy-driven (header checks, expected methods/URIs, source IP rules) in `plugins/redirector.py`.
- TLS interception identity depends on provided/generated CA material (`ca-cert/`, `certs/`).

## Monitoring & Observability

- Console/file logging through `lib/proxylogger.py`.
- Optional access log output in Apache2-like or RedELK format (`example-config.yaml`: `access_log_format`).
- Drop/allow reason codes are emitted by redirector policy checks for forensic context.

## CI/CD & Deployment

- No CI pipeline config (`.github/workflows/`, Jenkins, etc.) present in repository.
- No container manifests (Dockerfile/compose) present.
- Deployment is host-based service execution of `python RedWardenLite.py -c <config>`.

## Environment Configuration

- Main configuration source: `example-config.yaml`.
- Runtime flags in `lib/optionsparser.py` can override YAML settings.
- Integration-sensitive fields include:
- `destination_url`, `action_url`, `proxy_pass`
- `ip_details_api_keys`, `ip_geolocation_requirements`
- `ssl_cacert`, `ssl_cakey`, `ssl_certdir`, logging paths

## Webhooks & Callbacks

- No webhook consumers or callback endpoints are implemented.
- Integrations are request/response oriented reverse-proxy calls rather than event subscriptions.

---

*Integrations analysis: 2026-02-25*
*Update after adding new external providers or deployment targets*
