# Technology Stack

**Analysis Date:** 2026-02-25

## Languages

**Primary:**
- Python 3.x - Core proxy runtime in `RedWardenLite.py`, `lib/*.py`, and `plugins/*.py`.

**Secondary:**
- YAML - Runtime policy/config in `example-config.yaml`.
- Bash/OpenSSL commands - Certificate generation and management in `lib/sslintercept.py`.

## Runtime

**Environment:**
- CPython 3 (project shebangs are `#!/usr/bin/python3` for runtime modules).
- Tornado asynchronous web server/event loop for HTTP(S) listeners.
- OpenSSL binary required for MITM certificate generation/signing.

**Package Manager:**
- `pip` with dependencies listed in `requirements.txt`.
- Lockfile: none (`requirements.txt` is dependency-name based and not version pinned).

## Frameworks

**Core:**
- Tornado - HTTP(S) listener lifecycle and request handling (`RedWardenLite.py`, `lib/proxyhandler.py`).
- Requests - Upstream reverse-proxy fetch operations (`lib/proxyhandler.py`).

**Testing:**
- No automated test framework found in repository.

**Build/Dev:**
- No build step; interpreted Python runtime.
- CLI/config parsing via `argparse` + YAML in `lib/optionsparser.py`.

## Key Dependencies

**Critical:**
- `tornado` - Front-door proxy server and handler dispatch.
- `requests` - Upstream request forwarding.
- `PyYaml` - Config and plugin policy parsing.
- `sqlitedict` - Anti-replay and dynamic whitelist persistence.
- `brotli` - Response decompression and recompression support.

**Infrastructure:**
- Python stdlib (`ssl`, `socket`, `http.client`, `subprocess`, `asyncio`).
- OpenSSL CLI for certificate and key generation.

## Configuration

**Environment:**
- Primary runtime config via `example-config.yaml` (`destination_url`, `policy`, SSL paths, logging paths).
- CLI flags parsed in `lib/optionsparser.py` can override file-based values.
- Data lists loaded from `data/banned_ips.txt`, `data/banned_words.txt`, `data/banned_words_override.txt`.

**Build:**
- No packaging/build config (`pyproject.toml`, `setup.py`) found.

## Platform Requirements

**Development:**
- Linux/macOS environment with Python 3 and OpenSSL available.
- Filesystem write access for runtime artifacts (`.anti-replay.sqlite`, `.peers.sqlite`, cert output directories).

**Production:**
- Long-running host with reachable listener ports configured in `port` (for example `80/http`, `443/https`).
- TLS certificate/key files or permission to generate interception certificates.

---

*Stack analysis: 2026-02-25*
*Update after major dependency changes*
