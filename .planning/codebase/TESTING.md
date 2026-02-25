# Testing Patterns

**Analysis Date:** 2026-02-25

## Test Framework

- No automated test framework is configured in this repository.
- No `pytest`, `unittest` suites, or CI test workflow files were found.
- Validation currently appears to rely on manual runtime checks and traffic simulation.

## Test File Organization

- No `tests/` directory or test modules matching `test_*.py`/`*_test.py` were found.
- No fixture directories or data builders are defined for automated test execution.

## Test Structure

- Current validation style is operational/manual:
- Run `python RedWardenLite.py -c example-config.yaml`.
- Send representative HTTP/HTTPS traffic through bound ports.
- Inspect allow/drop behavior and logs for expected reason codes.

## Mocking

- No mocking framework usage found.
- External calls (`requests`, DNS, IP geolocation APIs, sqlite writes) are currently unmocked in repo-level tests.

## Fixtures and Factories

- No reusable fixture/factory infrastructure exists.
- Static sample inputs are primarily in:
- `example-config.yaml`
- `data/banned_ips.txt`
- `data/banned_words.txt`
- `data/banned_words_override.txt`

## Coverage

- No coverage tooling/configuration is present.
- Existing `.gitignore` contains generic coverage patterns, but repository has no active coverage reports.

## Test Types

- Unit tests: absent.
- Integration tests: absent.
- End-to-end tests: absent.
- Manual smoke/regression testing through live proxy execution: implied by README usage.

## Common Patterns

- Manual scenario validation should include:
- Valid request pass-through to `destination_url`.
- Invalid request handling (`drop_action`: reset/redirect/proxy).
- Policy gates (`expected_headers`, `expected_http_methods`, `expected_uri`).
- Replay protection toggles (`mitigate_replay_attack`).
- IP lookup behavior with `verify_peer_ip_details` enabled.
- HTTPS interception startup with provided/generated certificate material.

---

*Testing analysis: 2026-02-25*
*Update after introducing automated tests or CI gates*
