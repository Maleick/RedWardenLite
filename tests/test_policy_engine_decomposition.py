from plugins import redirector
from plugins.policy.types import DecisionResult


FIXED_TS = "2026-02-25/12:00:00"


def inspect_with_json(plugin, req):
    peer_ip = redirector.ProxyPlugin.get_peer_ip(req)
    status, payload = plugin._client_request_inspect(peer_ip, FIXED_TS, req, b"", object(), b"", {})
    assert isinstance(payload, dict)
    return status, payload


def test_policy_engine_returns_structured_drop_decision(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "policy": {"drop_request_without_expected_header": True},
            "expected_headers": ["x-required"],
        }
    )
    req = request_factory()
    peer_ip = redirector.ProxyPlugin.get_peer_ip(req)

    decision = plugin.policy_engine.evaluate(peer_ip, FIXED_TS, req, b"")

    assert isinstance(decision, DecisionResult)
    assert decision.allow is False
    assert decision.action == "drop"
    assert decision.reason == "5"
    assert decision.metadata["matched_status"] is True


def test_policy_engine_host_override_is_decision_metadata_only(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "policy": {"drop_request_without_expected_header_value": True},
            "expected_headers_value": {"host": "backend.internal:443"},
        }
    )
    req = request_factory(headers={"host": "backend.internal:443", "Host": "backend.internal:443"})
    peer_ip = redirector.ProxyPlugin.get_peer_ip(req)

    decision = plugin.policy_engine.evaluate(peer_ip, FIXED_TS, req, b"")

    assert decision.allow is True
    assert decision.action == "allow"
    assert decision.reason == "99"
    assert decision.metadata["matched_status"] is False
    assert decision.metadata["override_host_header"] == "backend.internal:443"
    assert redirector.proxy2_metadata_headers["override_host_header"] not in req.headers


def test_action_executor_applies_host_override_metadata(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "policy": {"drop_request_without_expected_header_value": True},
            "expected_headers_value": {"host": "backend.internal:443"},
        }
    )
    req = request_factory(headers={"host": "backend.internal:443", "Host": "backend.internal:443"})
    peer_ip = redirector.ProxyPlugin.get_peer_ip(req)
    decision = plugin.policy_engine.evaluate(peer_ip, FIXED_TS, req, b"")

    status, payload = plugin.action_executor.execute(decision, peer_ip, FIXED_TS, req)

    assert status is False
    assert payload is False
    assert req.headers[redirector.proxy2_metadata_headers["override_host_header"]] == "backend.internal:443"


def test_action_executor_keeps_peer_info_side_effect_parity(plugin_factory, request_factory, monkeypatch):
    plugin, _ = plugin_factory()
    req = request_factory()
    peer_ip = redirector.ProxyPlugin.get_peer_ip(req)

    printed = []
    monkeypatch.setattr(plugin, "_print_peer_info", lambda _ip: printed.append(_ip))
    monkeypatch.setattr(plugin, "drop_reason", lambda _msg: None)
    monkeypatch.setattr(plugin, "report", lambda _drop, *_args, **_kwargs: _drop)

    no_print_decision = DecisionResult(
        allow=False,
        action="drop",
        reason="5",
        message="drop 5",
        metadata={"matched_status": True},
    )
    print_decision = DecisionResult(
        allow=False,
        action="drop",
        reason="2",
        message="drop 2",
        metadata={"matched_status": True},
    )

    plugin.action_executor.execute(no_print_decision, peer_ip, FIXED_TS, req)
    plugin.action_executor.execute(print_decision, peer_ip, FIXED_TS, req)

    assert printed == [peer_ip]


def test_policy_engine_preserves_check_ordering(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "policy": {
                "drop_http_banned_header_names": True,
                "drop_request_without_expected_header": True,
            },
            "expected_headers": ["x-required-header"],
        },
        banned_agents=["curl"],
    )
    req = request_factory(headers={"X-Curl-Agent": "safe"})

    status, payload = inspect_with_json(plugin, req)

    assert status is True
    assert payload["action"] == "drop"
    assert payload["reason"] == "2"
