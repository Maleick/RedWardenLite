import json

from lib.runtime_hardening import (
    RUNTIME_HARDENING_EXIT_CODE,
    apply_runtime_hardening_effective,
    collect_listener_specs,
    evaluate_runtime_hardening,
    format_runtime_hardening_report,
    is_public_bind,
)


def _base_options(**overrides):
    base = {
        "runtime_profile": "compatible",
        "runtime_hardening_allow_unsafe": False,
        "runtime_hardening_unsafe_ack": "",
        "runtime_hardening_validation_output": "human",
        "bind": "http://0.0.0.0",
        "port": [8080],
    }
    base.update(overrides)
    return base


def test_compatible_mode_warns_and_continues():
    report = evaluate_runtime_hardening(_base_options())

    assert report["profile"] == "compatible"
    assert report["fail"] is False
    assert report["exit_code"] == 0
    assert report["effective"]["runtime_tls_verify_upstream"] is False
    warning_ids = {item["id"] for item in report["warnings"]}
    assert "compatible-mode-active" in warning_ids


def test_strict_mode_enables_upstream_tls_verification_by_default():
    report = evaluate_runtime_hardening(_base_options(runtime_profile="strict", bind="127.0.0.1"))

    assert report["profile"] == "strict"
    assert report["effective"]["runtime_tls_verify_upstream"] is True


def test_strict_mode_aggregates_multiple_public_http_listener_violations():
    report = evaluate_runtime_hardening(
        _base_options(
            runtime_profile="strict",
            bind="http://0.0.0.0",
            port=["80/http", "8080/http"],
        )
    )

    assert report["fail"] is True
    assert report["exit_code"] == RUNTIME_HARDENING_EXIT_CODE
    assert len(report["violations"]) == 2
    assert all(item["id"] == "SEC-02-public-http-listener" for item in report["violations"])


def test_strict_mode_override_without_ack_fails():
    report = evaluate_runtime_hardening(
        _base_options(
            runtime_profile="strict",
            runtime_hardening_allow_unsafe=True,
            runtime_hardening_unsafe_ack="",
            bind="http://0.0.0.0",
            port=["80/http"],
        )
    )

    assert report["fail"] is True
    violation_ids = {item["id"] for item in report["violations"]}
    assert "SEC-02-unsafe-override-missing-ack" in violation_ids


def test_strict_mode_override_with_ack_allows_startup_and_warns():
    report = evaluate_runtime_hardening(
        _base_options(
            runtime_profile="strict",
            runtime_hardening_allow_unsafe=True,
            runtime_hardening_unsafe_ack="accepted-risk-2026-02-25",
            bind="http://0.0.0.0",
            port=["80/http"],
        )
    )

    assert report["fail"] is False
    warning_ids = {item["id"] for item in report["warnings"]}
    assert "SEC-02-unsafe-override-active" in warning_ids
    assert "overridden-SEC-02-public-http-listener" in warning_ids


def test_validation_output_normalization_defaults_to_human_with_warning():
    report = evaluate_runtime_hardening(
        _base_options(
            runtime_hardening_validation_output="xml",
        )
    )

    assert report["output_mode"] == "human"
    warning_ids = {item["id"] for item in report["warnings"]}
    assert "validation-output-normalized" in warning_ids


def test_format_report_human_contains_path_reason_and_safe_example():
    report = evaluate_runtime_hardening(
        _base_options(runtime_profile="strict", bind="http://0.0.0.0", port=["80/http"])
    )
    rendered = format_runtime_hardening_report(report)

    assert "Runtime hardening validation failed" in rendered
    assert "Reason:" in rendered
    assert "Safe example:" in rendered
    assert "port[0]" in rendered


def test_format_report_json_is_machine_readable():
    report = evaluate_runtime_hardening(
        _base_options(
            runtime_profile="strict",
            runtime_hardening_validation_output="json",
            bind="http://0.0.0.0",
            port=["80/http"],
        )
    )
    rendered = format_runtime_hardening_report(report)
    parsed = json.loads(rendered)

    assert parsed["output_mode"] == "json"
    assert parsed["fail"] is True
    assert parsed["violations"][0]["path"] == "port[0]"


def test_apply_runtime_hardening_effective_updates_options():
    options = _base_options(runtime_profile="strict", bind="127.0.0.1")
    report = evaluate_runtime_hardening(options)

    apply_runtime_hardening_effective(options, report)

    assert options["runtime_profile"] == "strict"
    assert options["runtime_tls_verify_upstream"] is True


def test_listener_collection_and_public_bind_detection():
    listeners = collect_listener_specs(
        _base_options(
            bind="http://127.0.0.1",
            port=["80/http", "443/https", "10.0.0.1:8080/http"],
        )
    )

    assert listeners[0]["scheme"] == "http"
    assert listeners[1]["scheme"] == "https"
    assert listeners[2]["bind"] == "10.0.0.1"
    assert is_public_bind("0.0.0.0") is True
    assert is_public_bind("127.0.0.1") is False
    assert is_public_bind("10.0.0.1") is False
