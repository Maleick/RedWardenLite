import json
from types import SimpleNamespace

import RedWardenLite
import lib.proxyhandler as proxyhandler
import tornado.web
from lib.observability import (
    build_request_event,
    emit_request_event,
    record_request_metrics,
    record_upstream_failure,
    render_prometheus_metrics,
    reset_registry,
)
from tornado.testing import AsyncHTTPTestCase


class RecordingLogger:
    def __init__(self):
        self.errors = []

    def err(self, text, **kwargs):
        self.errors.append(str(text))


def _sample_event(**overrides):
    event = {
        "timestamp": "2026-02-25T00:00:00Z",
        "method": "GET",
        "path": "/beacon",
        "status": 200,
        "action": "allow",
        "reason": "99",
        "duration_ms": 12,
        "transport_mode": "legacy",
        "runtime_profile": "compatible",
    }
    event.update(overrides)
    return event


def test_structured_event_schema_required_fields_and_path_defaults():
    request = SimpleNamespace(method="POST", uri="/collect?token=secret")

    event = build_request_event(
        request=request,
        status=204,
        action="drop",
        reason="4b",
        duration_ms=42.7,
        transport_mode="async",
        runtime_profile="strict",
        include_query=False,
    )

    required = {
        "timestamp",
        "method",
        "path",
        "status",
        "action",
        "reason",
        "duration_ms",
        "transport_mode",
        "runtime_profile",
    }
    assert required.issubset(set(event.keys()))
    assert event["method"] == "POST"
    assert event["path"] == "/collect"
    assert event["status"] == 204
    assert event["action"] == "drop"
    assert event["reason"] == "4b"
    assert event["transport_mode"] == "async"
    assert event["runtime_profile"] == "strict"


def test_structured_event_path_can_include_query_when_enabled():
    request = SimpleNamespace(method="GET", uri="/beacon?id=abc")
    event = build_request_event(
        request=request,
        status=200,
        action="allow",
        reason="99",
        duration_ms=9.3,
        transport_mode="legacy",
        runtime_profile="compatible",
        include_query=True,
    )

    assert event["path"] == "/beacon?id=abc"


def test_emit_request_event_writes_single_json_line(tmp_path):
    logger = RecordingLogger()
    event_file = tmp_path / "events.jsonl"
    options = {
        "observability_events_enabled": True,
        "observability_events_file": str(event_file),
    }

    assert emit_request_event(options, logger, _sample_event()) is True

    lines = event_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["action"] == "allow"
    assert parsed["reason"] == "99"
    assert parsed["path"] == "/beacon"


def test_emit_request_event_sink_failure_is_best_effort(tmp_path):
    logger = RecordingLogger()
    sink_dir = tmp_path / "events-dir"
    sink_dir.mkdir()
    options = {
        "observability_events_enabled": True,
        "observability_events_file": str(sink_dir),
    }

    assert emit_request_event(options, logger, _sample_event()) is False
    assert any("event-write-failed" in entry for entry in logger.errors)


def test_metrics_include_allow_and_drop_reason_and_histogram_series():
    reset_registry()
    options = {
        "observability_metrics_enabled": True,
        "observability_metrics_format": "prometheus",
    }

    record_request_metrics(
        options,
        _sample_event(action="allow", reason="99", transport_mode="legacy", duration_ms=50),
    )
    record_request_metrics(
        options,
        _sample_event(
            action="drop",
            reason="4b",
            transport_mode="async",
            runtime_profile="strict",
            duration_ms=250,
        ),
    )

    metrics = render_prometheus_metrics(options)

    assert "redwardenlite_requests_total" in metrics
    assert 'action="allow"' in metrics
    assert 'reason="99"' in metrics
    assert 'action="drop"' in metrics
    assert 'reason="4b"' in metrics
    assert "redwardenlite_request_duration_seconds_bucket" in metrics
    assert "redwardenlite_request_duration_seconds_count" in metrics
    assert "redwardenlite_request_duration_seconds_sum" in metrics
    assert "path=" not in metrics
    assert "query=" not in metrics


def test_metrics_include_upstream_failures_counter():
    reset_registry()
    options = {
        "observability_metrics_enabled": True,
        "observability_metrics_format": "prometheus",
    }

    record_upstream_failure(options, "async", "ConnectionError")
    metrics = render_prometheus_metrics(options)

    assert "redwardenlite_upstream_failures_total" in metrics
    assert 'transport_mode="async"' in metrics
    assert 'error_class="ConnectionError"' in metrics


def test_metrics_route_registered_before_catch_all():
    routes = RedWardenLite.build_proxy_routes(
        "http",
        "127.0.0.1",
        8080,
        opts={
            "observability_metrics_enabled": True,
            "observability_metrics_path": "metrics",
        },
    )

    assert routes[0][0] == r"/metrics$"
    assert routes[0][1].__name__ == "MetricsHandler"
    assert routes[1][1].__name__ == "ProxyRequestHandler"


class TestMetricsEndpoint(AsyncHTTPTestCase):
    def get_app(self):
        reset_registry()
        proxyhandler.options = {
            "observability_metrics_enabled": True,
            "observability_metrics_format": "prometheus",
        }
        record_request_metrics(
            proxyhandler.options,
            _sample_event(action="allow", reason="99", transport_mode="legacy", duration_ms=15),
        )
        return tornado.web.Application(
            [(r"/metrics", proxyhandler.MetricsHandler, dict(server_bind="127.0.0.1", server_port=8080))]
        )

    def test_metrics_endpoint_returns_prometheus_text(self):
        response = self.fetch("/metrics")
        assert response.code == 200
        assert response.headers["Content-Type"].startswith("text/plain")
        body = response.body.decode("utf-8")
        assert "redwardenlite_requests_total" in body
