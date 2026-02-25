from dataclasses import dataclass, field

from plugins import redirector


@dataclass
class DummyResponse:
    status: int = 200
    response_version: str = "HTTP/1.1"
    reason: str = "OK"
    headers: dict = field(default_factory=dict)


def test_drop_action_reset_returns_drop_connection_exception(plugin_factory, request_factory):
    plugin, _ = plugin_factory(option_overrides={"drop_action": "reset"})
    req = request_factory()

    plugin.is_request = True
    result = plugin._drop_action(req, b"payload", None, None)

    assert isinstance(result, redirector.DropConnectionException)


def test_drop_action_redirect_returns_dont_fetch_for_request(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "drop_action": "redirect",
            "action_url": ["https://sink.example"],
        }
    )
    req = request_factory()

    plugin.is_request = True
    result = plugin._drop_action(req, b"payload", None, None)

    assert isinstance(result, redirector.DontFetchResponseException)


def test_drop_action_redirect_sets_response_redirect_for_responses(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "drop_action": "redirect",
            "action_url": ["https://sink.example"],
        }
    )
    req = request_factory(uri="/blocked/path")
    res = DummyResponse()

    plugin.is_request = False
    result = plugin._drop_action(req, b"", res, b"original")

    assert isinstance(result, bytes)
    assert res.status == 301
    assert res.reason == "Moved Permanently"
    assert res.headers["Location"] == "https://sink.example"


def test_drop_action_proxy_returns_request_body(plugin_factory, request_factory):
    plugin, _ = plugin_factory(option_overrides={"drop_action": "proxy"})
    req = request_factory()
    body = b"payload"

    plugin.is_request = True
    result = plugin._drop_action(req, body, None, None)

    assert result == body


def test_request_handler_sets_no_keep_alive_when_request_drops(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "drop_action": "reset",
            "policy": {"drop_request_without_expected_header": True},
            "expected_headers": ["x-required"],
        }
    )
    req = request_factory()

    result = plugin._request_handler(req, b"")

    assert isinstance(result, redirector.DropConnectionException)
    assert req.connection.no_keep_alive is True


def test_request_handler_keeps_connection_alive_when_request_is_allowed(plugin_factory, request_factory):
    plugin, _ = plugin_factory()
    req = request_factory(uri="/beacon")

    result = plugin._request_handler(req, b"")

    assert result is None
    assert req.connection.no_keep_alive is False
    assert req.redirected_to_c2 is True
    assert redirector.proxy2_metadata_headers["override_host_header"] in req.headers


def test_request_handler_proxy_drop_redirects_and_disables_keep_alive(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "drop_action": "proxy",
            "action_url": ["https://decoy.example"],
            "policy": {"drop_request_without_expected_header": True},
            "expected_headers": ["x-required"],
        }
    )
    req = request_factory(uri="/stage")

    result = plugin._request_handler(req, b"")

    assert result is None
    assert req.connection.no_keep_alive is True
    assert req.redirected_to_c2 is True
    assert req.uri.startswith("https://decoy.example/")
    assert req.headers[redirector.proxy2_metadata_headers["override_host_header"]] == "decoy.example"
