import inspect


VALID_TRANSPORT_MODES = {"legacy", "async", "auto"}


def as_bool(value, default=True):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0

    lowered = str(value).strip().lower()
    if lowered in {"1", "true", "yes", "on"}:
        return True
    if lowered in {"0", "false", "no", "off"}:
        return False

    return default


def normalize_transport_mode(mode):
    lowered = str(mode or "legacy").strip().lower()
    if lowered not in VALID_TRANSPORT_MODES:
        return "legacy"
    return lowered


def select_primary_transport(mode, method, content_length=0):
    normalized = normalize_transport_mode(mode)
    if normalized != "auto":
        return normalized

    safe_methods = {"GET", "HEAD", "OPTIONS", "PROPFIND"}
    method_upper = str(method or "GET").upper()

    try:
        body_len = int(content_length or 0)
    except (TypeError, ValueError):
        body_len = 0

    if method_upper in safe_methods and body_len == 0:
        return "async"
    return "legacy"


def shadow_transport(primary):
    if normalize_transport_mode(primary) == "async":
        return "legacy"
    return "async"


async def _maybe_await(value):
    if inspect.isawaitable(value):
        return await value
    return value


async def fetch_with_fallback(primary_transport, fetcher, fallback_enabled=True, log_failure=None):
    primary = normalize_transport_mode(primary_transport)

    if primary == "legacy":
        result = await _maybe_await(fetcher("legacy"))
        return {
            "transport_used": "legacy",
            "result": result,
            "fallback_error": None,
        }

    try:
        result = await _maybe_await(fetcher("async"))
        return {
            "transport_used": "async",
            "result": result,
            "fallback_error": None,
        }
    except Exception as exc:
        if not fallback_enabled:
            raise

        if callable(log_failure):
            log_failure(exc)

        result = await _maybe_await(fetcher("legacy"))
        return {
            "transport_used": "legacy",
            "result": result,
            "fallback_error": str(exc),
        }
