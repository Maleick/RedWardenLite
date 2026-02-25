import socket

from sqlitedict import SqliteDict

from plugins import redirector


FIXED_TS = "2026-02-25/12:00:00"


class StaticLookup:
    def __init__(self, details):
        self.details = details

    def lookup(self, _ip):
        return self.details


class StaticDeterminant:
    def __init__(self, determine_result=True, meta_result=(True, "")):
        self.determine_result = determine_result
        self.meta_result = meta_result

    def determine(self, _details):
        return self.determine_result

    def validateIpGeoMetadata(self, _details, _banned, _override):
        return self.meta_result


def inspect_with_json(plugin, req):
    peer_ip = redirector.ProxyPlugin.get_peer_ip(req)
    status, payload = plugin._client_request_inspect(peer_ip, FIXED_TS, req, b"", object(), b"", {})
    assert isinstance(payload, dict)
    assert "reason" in payload
    return status, payload


def geo_details(organization="Acme Cloud"):
    return {
        "organization": [organization],
        "continent": "North america",
        "continent_code": "NA",
        "country": "United States",
        "country_code": "US",
        "city": "Chicago",
        "timezone": "America/Chicago",
    }


def test_reason_0_logged_for_clean_allowed_request(plugin_factory, request_factory):
    plugin, logger = plugin_factory()
    req = request_factory(uri="/beacon")
    plugin._request_handler(req, b"")
    assert logger.contains("r:0", level="info")


def test_reason_99_for_clean_request_in_json_mode(plugin_factory, request_factory):
    plugin, _ = plugin_factory()
    req = request_factory()
    status, payload = inspect_with_json(plugin, req)
    assert status is False
    assert payload["action"] == "allow"
    assert payload["reason"] == "99"


def test_reason_1_whitelisted_ip_allows(plugin_factory, request_factory):
    plugin, _ = plugin_factory(option_overrides={"whitelisted_ip_addresses": ["198.51.100.0/24"]})
    req = request_factory(ip="198.51.100.77")
    status, payload = inspect_with_json(plugin, req)
    assert status is True
    assert payload["action"] == "allow"
    assert payload["reason"] == "1"


def test_reason_2_dynamic_whitelist_allows(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "policy": {"allow_dynamic_peer_whitelisting": True},
            "add_peers_to_whitelist_if_they_sent_valid_requests": {
                "number_of_valid_http_get_requests": 1,
                "number_of_valid_http_post_requests": 1,
            },
        }
    )
    req = request_factory(ip="198.51.100.77")

    with SqliteDict(redirector.ProxyPlugin.DynamicWhitelistFile, autocommit=True) as db:
        db["whitelisted_ips"] = [req.client_address[0]]

    status, payload = inspect_with_json(plugin, req)
    assert status is True
    assert payload["action"] == "allow"
    assert payload["reason"] == "2"


def test_reason_2_drop_http_banned_header_name(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={"policy": {"drop_http_banned_header_names": True}},
        banned_agents=["curl"],
    )
    req = request_factory(headers={"X-Curl-Agent": "safe"})
    status, payload = inspect_with_json(plugin, req)
    assert status is True
    assert payload["action"] == "drop"
    assert payload["reason"] == "2"


def test_reason_2_drop_header_name_substring_match(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={"policy": {"drop_http_banned_header_names": True}},
        banned_agents=["scan"],
    )
    req = request_factory(headers={"X-Scanner-Tag": "safe"})
    status, payload = inspect_with_json(plugin, req)
    assert status is True
    assert payload["action"] == "drop"
    assert payload["reason"] == "2"


def test_reason_3_drop_http_banned_header_value(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={"policy": {"drop_http_banned_header_value": True}},
        banned_agents=["curl"],
    )
    req = request_factory(headers={"X-Client": "safe curl/8.5"})
    status, payload = inspect_with_json(plugin, req)
    assert status is True
    assert payload["action"] == "drop"
    assert payload["reason"] == "3"


def test_reason_3_header_value_override_allows(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={"policy": {"drop_http_banned_header_value": True}},
        banned_agents=["curl"],
        override_banned_agents=["curl"],
    )
    req = request_factory(headers={"X-Client": "curl/8.5"})
    status, payload = inspect_with_json(plugin, req)
    assert status is False
    assert payload["action"] == "allow"
    assert payload["reason"] == "99"


def test_reason_4a_blacklisted_ip_drop(plugin_factory, request_factory):
    plugin, _ = plugin_factory(option_overrides={"ban_blacklisted_ip_addresses": True})
    plugin.banned_ips = {"198.51.100.0/24": "blocked test range"}
    req = request_factory(ip="198.51.100.77")
    status, payload = inspect_with_json(plugin, req)
    assert status is True
    assert payload["action"] == "drop"
    assert payload["reason"] == "4a"


def test_reason_4a_blacklisted_ip_override_allows(plugin_factory, request_factory, monkeypatch):
    plugin, _ = plugin_factory(
        option_overrides={"ban_blacklisted_ip_addresses": True},
        override_banned_agents=["trusted"],
    )
    plugin.banned_ips = {"198.51.100.0/24": "blocked test range"}
    req = request_factory(ip="198.51.100.77")

    monkeypatch.setattr(socket, "gethostbyaddr", lambda _ip: ("trusted-edge.example", [], []))

    status, payload = inspect_with_json(plugin, req)
    assert status is False
    assert payload["action"] == "allow"
    assert payload["reason"] == "99"


def test_reason_4b_reverse_lookup_banned_word_drop(plugin_factory, request_factory, monkeypatch):
    plugin, _ = plugin_factory(
        option_overrides={"policy": {"drop_dangerous_ip_reverse_lookup": True}},
        banned_agents=["scanner"],
    )
    req = request_factory(ip="198.51.100.77")

    monkeypatch.setattr(socket, "gethostbyaddr", lambda _ip: ("scanner.edge.example", [], []))

    status, payload = inspect_with_json(plugin, req)
    assert status is True
    assert payload["action"] == "drop"
    assert payload["reason"] == "4b"


def test_reason_4b_reverse_lookup_override_allows(plugin_factory, request_factory, monkeypatch):
    plugin, _ = plugin_factory(
        option_overrides={"policy": {"drop_dangerous_ip_reverse_lookup": True}},
        banned_agents=["scanner"],
        override_banned_agents=["scanner"],
    )
    req = request_factory(ip="198.51.100.77")

    monkeypatch.setattr(socket, "gethostbyaddr", lambda _ip: ("scanner.edge.example", [], []))

    status, payload = inspect_with_json(plugin, req)
    assert status is False
    assert payload["action"] == "allow"
    assert payload["reason"] == "99"


def test_reason_4c_ip_lookup_organization_drop(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={"verify_peer_ip_details": True},
        banned_agents=["scanner"],
    )
    plugin.ipLookupHelper = StaticLookup(geo_details(organization="Acme Scanner Team"))
    plugin.ipGeolocationDeterminer = StaticDeterminant(determine_result=True)

    req = request_factory(ip="198.51.100.77")
    status, payload = inspect_with_json(plugin, req)
    assert status is True
    assert payload["action"] == "drop"
    assert payload["reason"] == "4c"


def test_reason_4d_ip_geolocation_mismatch_drop(plugin_factory, request_factory):
    plugin, _ = plugin_factory(option_overrides={"verify_peer_ip_details": True})
    plugin.ipLookupHelper = StaticLookup(geo_details())
    plugin.ipGeolocationDeterminer = StaticDeterminant(determine_result=False)

    req = request_factory(ip="198.51.100.77")
    status, payload = inspect_with_json(plugin, req)
    assert status is True
    assert payload["action"] == "drop"
    assert payload["reason"] == "4d"


def test_reason_4e_ip_geo_metadata_keyword_drop(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "verify_peer_ip_details": True,
            "policy": {"drop_ipgeo_metadata_containing_banned_keywords": True},
        }
    )
    plugin.ipLookupHelper = StaticLookup(geo_details())
    plugin.ipGeolocationDeterminer = StaticDeterminant(
        determine_result=True,
        meta_result=(False, "firewall"),
    )

    req = request_factory(ip="198.51.100.77")
    status, payload = inspect_with_json(plugin, req)
    assert status is True
    assert payload["action"] == "drop"
    assert payload["reason"] == "4e"


def test_reason_5_missing_expected_header_drop(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "policy": {"drop_request_without_expected_header": True},
            "expected_headers": ["x-required-header"],
        }
    )
    req = request_factory()
    status, payload = inspect_with_json(plugin, req)
    assert status is True
    assert payload["action"] == "drop"
    assert payload["reason"] == "5"


def test_reason_5_expected_header_present_allows(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "policy": {"drop_request_without_expected_header": True},
            "expected_headers": ["x-required-header"],
        }
    )
    req = request_factory(headers={"x-required-header": "present"})
    status, payload = inspect_with_json(plugin, req)
    assert status is False
    assert payload["action"] == "allow"
    assert payload["reason"] == "99"


def test_reason_6_expected_header_value_mismatch_drop(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "policy": {"drop_request_without_expected_header_value": True},
            "expected_headers_value": {"user-agent": "trusted-agent"},
        }
    )
    req = request_factory(headers={"user-agent": "curl/8.5", "Host": "edge.example"})
    status, payload = inspect_with_json(plugin, req)
    assert status is True
    assert payload["action"] == "drop"
    assert payload["reason"] == "6"


def test_reason_6_expected_host_value_sets_override_and_allows(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "policy": {"drop_request_without_expected_header_value": True},
            "expected_headers_value": {"host": "backend.internal:443"},
        }
    )
    req = request_factory(headers={"host": "backend.internal:443", "Host": "backend.internal:443"})

    status, payload = inspect_with_json(plugin, req)
    assert status is False
    assert payload["action"] == "allow"
    assert payload["reason"] == "99"
    assert req.headers[redirector.proxy2_metadata_headers["override_host_header"]] == "backend.internal:443"


def test_reason_6_expected_host_value_mismatch_drops_without_override(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "policy": {"drop_request_without_expected_header_value": True},
            "expected_headers_value": {"host": "backend.internal:443"},
        }
    )
    req = request_factory(headers={"host": "edge.example:443", "Host": "edge.example:443"})

    status, payload = inspect_with_json(plugin, req)
    assert status is True
    assert payload["action"] == "drop"
    assert payload["reason"] == "6"
    assert redirector.proxy2_metadata_headers["override_host_header"] not in req.headers


def test_reason_7_unexpected_http_method_drop(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "policy": {"drop_request_without_expected_http_method": True},
            "expected_http_methods": ["GET"],
        }
    )
    req = request_factory(method="POST")
    status, payload = inspect_with_json(plugin, req)
    assert status is True
    assert payload["action"] == "drop"
    assert payload["reason"] == "7"


def test_reason_7_expected_http_method_allows(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "policy": {"drop_request_without_expected_http_method": True},
            "expected_http_methods": ["GET", "POST"],
        }
    )
    req = request_factory(method="POST")
    status, payload = inspect_with_json(plugin, req)
    assert status is False
    assert payload["action"] == "allow"
    assert payload["reason"] == "99"


def test_reason_8_unexpected_uri_drop(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "policy": {"drop_request_without_expected_uri": True},
            "expected_uri": ["/allowed/*"],
        }
    )
    req = request_factory(uri="/forbidden/path")
    status, payload = inspect_with_json(plugin, req)
    assert status is True
    assert payload["action"] == "drop"
    assert payload["reason"] == "8"


def test_reason_8_expected_uri_pattern_allows(plugin_factory, request_factory):
    plugin, _ = plugin_factory(
        option_overrides={
            "policy": {"drop_request_without_expected_uri": True},
            "expected_uri": ["/allowed/*"],
        }
    )
    req = request_factory(uri="/allowed/path")
    status, payload = inspect_with_json(plugin, req)
    assert status is False
    assert payload["action"] == "allow"
    assert payload["reason"] == "99"
