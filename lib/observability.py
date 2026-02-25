import json
import os
import threading
from collections import defaultdict
from datetime import datetime, timezone
from urllib.parse import urlparse

from lib.transport_runtime import as_bool, normalize_transport_mode


DEFAULT_OBSERVABILITY_EVENT_FILE = "artifacts/observability/events.jsonl"
DEFAULT_OBSERVABILITY_METRICS_PATH = "/metrics"
DEFAULT_OBSERVABILITY_METRICS_FORMAT = "prometheus"

DEFAULT_HISTOGRAM_BUCKETS = (
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
)


def normalize_observability_path(path):
    value = str(path or DEFAULT_OBSERVABILITY_METRICS_PATH).strip()
    if not value:
        value = DEFAULT_OBSERVABILITY_METRICS_PATH
    if not value.startswith("/"):
        value = "/" + value
    return value


def normalize_runtime_profile(value):
    lowered = str(value or "compatible").strip().lower()
    if lowered not in ("compatible", "strict"):
        return "compatible"
    return lowered


def _normalize_label(value, default="unknown"):
    text = str(value or "").strip()
    if not text:
        return default
    return text


def _escape_label_value(value):
    return str(value).replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def extract_event_path(uri, include_query=False):
    parsed = urlparse(str(uri or "/"))
    path = parsed.path or "/"
    if include_query and parsed.query:
        path += "?" + parsed.query
    return path


def build_request_event(
        request,
        status,
        action,
        reason,
        duration_ms,
        transport_mode,
        runtime_profile,
        include_query=False):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": _normalize_label(getattr(request, "method", "UNKNOWN"), "UNKNOWN").upper(),
        "path": extract_event_path(getattr(request, "uri", "/"), include_query),
        "status": int(status or 0),
        "action": _normalize_label(action, "allow").lower(),
        "reason": _normalize_label(reason, "99"),
        "duration_ms": int(max(0, round(float(duration_ms or 0.0)))),
        "transport_mode": normalize_transport_mode(transport_mode),
        "runtime_profile": normalize_runtime_profile(runtime_profile),
    }


class ObservabilityRegistry:
    def __init__(self, buckets=None):
        self._lock = threading.Lock()
        self._buckets = tuple(sorted(buckets or DEFAULT_HISTOGRAM_BUCKETS))
        self._requests_total = defaultdict(int)
        self._upstream_failures_total = defaultdict(int)
        self._latency = {}

    def observe_request(self, method, action, reason, transport_mode, runtime_profile, duration_seconds):
        method_v = _normalize_label(method, "UNKNOWN").upper()
        action_v = _normalize_label(action, "allow").lower()
        reason_v = _normalize_label(reason, "99")
        transport_v = normalize_transport_mode(transport_mode)
        profile_v = normalize_runtime_profile(runtime_profile)
        key = (method_v, action_v, reason_v, transport_v, profile_v)
        latency_key = (method_v, action_v, transport_v, profile_v)
        value = max(0.0, float(duration_seconds or 0.0))

        with self._lock:
            self._requests_total[key] += 1
            if latency_key not in self._latency:
                self._latency[latency_key] = {
                    "count": 0,
                    "sum": 0.0,
                    "buckets": [0] * (len(self._buckets) + 1),
                }

            stats = self._latency[latency_key]
            stats["count"] += 1
            stats["sum"] += value

            for idx, bucket in enumerate(self._buckets):
                if value <= bucket:
                    stats["buckets"][idx] += 1

            stats["buckets"][-1] += 1

    def increment_upstream_failure(self, transport_mode, error_class):
        key = (
            normalize_transport_mode(transport_mode),
            _normalize_label(error_class, "Exception"),
        )
        with self._lock:
            self._upstream_failures_total[key] += 1

    def render_prometheus(self):
        with self._lock:
            lines = []

            lines.append("# HELP redwardenlite_requests_total Completed request outcomes by method/action/reason.")
            lines.append("# TYPE redwardenlite_requests_total counter")
            for key in sorted(self._requests_total.keys()):
                method, action, reason, transport_mode, runtime_profile = key
                labels = (
                    'method="{}",action="{}",reason="{}",transport_mode="{}",runtime_profile="{}"'.format(
                        _escape_label_value(method),
                        _escape_label_value(action),
                        _escape_label_value(reason),
                        _escape_label_value(transport_mode),
                        _escape_label_value(runtime_profile),
                    )
                )
                lines.append(
                    "redwardenlite_requests_total{{{}}} {}".format(labels, self._requests_total[key])
                )

            lines.append(
                "# HELP redwardenlite_upstream_failures_total Upstream transport failures by transport/error class."
            )
            lines.append("# TYPE redwardenlite_upstream_failures_total counter")
            for key in sorted(self._upstream_failures_total.keys()):
                transport_mode, error_class = key
                labels = 'transport_mode="{}",error_class="{}"'.format(
                    _escape_label_value(transport_mode),
                    _escape_label_value(error_class),
                )
                lines.append(
                    "redwardenlite_upstream_failures_total{{{}}} {}".format(
                        labels, self._upstream_failures_total[key]
                    )
                )

            lines.append(
                "# HELP redwardenlite_request_duration_seconds Request duration histogram by method/action/transport/profile."
            )
            lines.append("# TYPE redwardenlite_request_duration_seconds histogram")

            for key in sorted(self._latency.keys()):
                method, action, transport_mode, runtime_profile = key
                stats = self._latency[key]
                base_labels = 'method="{}",action="{}",transport_mode="{}",runtime_profile="{}"'.format(
                    _escape_label_value(method),
                    _escape_label_value(action),
                    _escape_label_value(transport_mode),
                    _escape_label_value(runtime_profile),
                )

                for idx, bucket in enumerate(self._buckets):
                    labels = base_labels + ',le="{}"'.format("{:g}".format(bucket))
                    lines.append(
                        "redwardenlite_request_duration_seconds_bucket{{{}}} {}".format(
                            labels, stats["buckets"][idx]
                        )
                    )

                labels_inf = base_labels + ',le="+Inf"'
                lines.append(
                    "redwardenlite_request_duration_seconds_bucket{{{}}} {}".format(
                        labels_inf, stats["buckets"][-1]
                    )
                )
                lines.append(
                    "redwardenlite_request_duration_seconds_count{{{}}} {}".format(base_labels, stats["count"])
                )
                lines.append(
                    "redwardenlite_request_duration_seconds_sum{{{}}} {}".format(base_labels, stats["sum"])
                )

            return "\n".join(lines) + "\n"


_REGISTRY = ObservabilityRegistry()


def get_registry():
    return _REGISTRY


def reset_registry():
    global _REGISTRY
    _REGISTRY = ObservabilityRegistry()


def observability_events_enabled(options):
    return as_bool(options.get("observability_events_enabled", True), True)


def observability_metrics_enabled(options):
    return as_bool(options.get("observability_metrics_enabled", True), True)


def emit_request_event(options, logger, event):
    if not observability_events_enabled(options):
        return False

    out_file = str(options.get("observability_events_file", DEFAULT_OBSERVABILITY_EVENT_FILE) or "").strip()
    if not out_file:
        out_file = DEFAULT_OBSERVABILITY_EVENT_FILE

    try:
        out_dir = os.path.dirname(out_file)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        with open(out_file, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")

        return True
    except Exception as exc:
        if logger is not None:
            logger.err("[OBSERVABILITY event-write-failed] {}".format(exc))
        return False


def record_request_metrics(options, event):
    if not observability_metrics_enabled(options):
        return

    duration_seconds = float(event.get("duration_ms", 0)) / 1000.0
    get_registry().observe_request(
        method=event.get("method", "UNKNOWN"),
        action=event.get("action", "allow"),
        reason=event.get("reason", "99"),
        transport_mode=event.get("transport_mode", "legacy"),
        runtime_profile=event.get("runtime_profile", "compatible"),
        duration_seconds=duration_seconds,
    )


def record_upstream_failure(options, transport_mode, error_class):
    if not observability_metrics_enabled(options):
        return

    get_registry().increment_upstream_failure(transport_mode, error_class)


def render_prometheus_metrics(options):
    if not observability_metrics_enabled(options):
        return ""

    fmt = str(options.get("observability_metrics_format", DEFAULT_OBSERVABILITY_METRICS_FORMAT)).strip().lower()
    if fmt != "prometheus":
        return ""

    return get_registry().render_prometheus()
