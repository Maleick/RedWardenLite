import asyncio

import pytest

from lib.transport_runtime import fetch_with_fallback, normalize_transport_mode, select_primary_transport, shadow_transport


def test_normalize_transport_mode_defaults_to_legacy_for_invalid_values():
    assert normalize_transport_mode(None) == "legacy"
    assert normalize_transport_mode("invalid") == "legacy"
    assert normalize_transport_mode("ASYNC") == "async"


def test_select_primary_transport_respects_explicit_modes():
    assert select_primary_transport("legacy", "GET", 0) == "legacy"
    assert select_primary_transport("async", "POST", 1024) == "async"


def test_select_primary_transport_auto_is_dynamic():
    assert select_primary_transport("auto", "GET", 0) == "async"
    assert select_primary_transport("auto", "HEAD", 0) == "async"
    assert select_primary_transport("auto", "POST", 10) == "legacy"


def test_shadow_transport_is_opposite_of_primary():
    assert shadow_transport("legacy") == "async"
    assert shadow_transport("async") == "legacy"


def test_fetch_with_fallback_uses_legacy_when_async_errors():
    calls = []

    async def fetcher(mode):
        calls.append(mode)
        if mode == "async":
            raise RuntimeError("async failed")
        return {"mode": mode}

    result = asyncio.run(fetch_with_fallback("async", fetcher, fallback_enabled=True))

    assert result["transport_used"] == "legacy"
    assert result["result"] == {"mode": "legacy"}
    assert "async failed" in result["fallback_error"]
    assert calls == ["async", "legacy"]


def test_fetch_with_fallback_raises_when_fallback_disabled():
    async def fetcher(mode):
        if mode == "async":
            raise RuntimeError("async failed")
        return {"mode": mode}

    with pytest.raises(RuntimeError, match="async failed"):
        asyncio.run(fetch_with_fallback("async", fetcher, fallback_enabled=False))


def test_fetch_with_fallback_uses_legacy_directly_for_legacy_mode():
    calls = []

    async def fetcher(mode):
        calls.append(mode)
        return {"mode": mode}

    result = asyncio.run(fetch_with_fallback("legacy", fetcher, fallback_enabled=True))

    assert result["transport_used"] == "legacy"
    assert result["result"] == {"mode": "legacy"}
    assert result["fallback_error"] is None
    assert calls == ["legacy"]
