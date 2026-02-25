import copy
from dataclasses import dataclass, field

import pytest

from plugins import redirector


BASE_POLICY = {
    "allow_proxy_pass": False,
    "allow_dynamic_peer_whitelisting": False,
    "drop_http_banned_header_names": False,
    "drop_http_banned_header_value": False,
    "drop_dangerous_ip_reverse_lookup": False,
    "drop_ipgeo_metadata_containing_banned_keywords": False,
    "drop_request_without_expected_header": False,
    "drop_request_without_expected_header_value": False,
    "drop_request_without_expected_http_method": False,
    "drop_request_without_expected_uri": False,
}


BASE_OPTIONS = {
    "config": "",
    "redir_config": "",
    "verbose": False,
    "debug": False,
    "report_only": False,
    "drop_action": "redirect",
    "action_url": ["https://example.org"],
    "destination_url": ["http://127.0.0.1:8080"],
    "proxy_pass": {},
    "ban_blacklisted_ip_addresses": False,
    "verify_peer_ip_details": False,
    "ip_details_api_keys": {},
    "ip_geolocation_requirements": {},
    "expected_headers": [],
    "expected_headers_value": {},
    "expected_http_methods": [],
    "expected_uri": [],
    "whitelisted_ip_addresses": [],
    "add_peers_to_whitelist_if_they_sent_valid_requests": {},
    "throttle_down_peer_logging": {},
    "policy": BASE_POLICY,
}


class RecordingLogger:
    def __init__(self):
        self.options = {"verbose": False, "debug": False}
        self.events = []

    def info(self, txt, forced=False, **kwargs):
        self.events.append(("info", str(txt)))

    def dbg(self, txt, **kwargs):
        self.events.append(("debug", str(txt)))

    def err(self, txt, **kwargs):
        self.events.append(("error", str(txt)))

    def fatal(self, txt, **kwargs):
        raise RuntimeError(str(txt))

    def contains(self, needle, level=None):
        for entry_level, entry_text in self.events:
            if level is not None and entry_level != level:
                continue
            if needle in entry_text:
                return True
        return False


class NullLookup:
    def lookup(self, _ip):
        return {}


class AllowAllDeterminant:
    def determine(self, _details):
        return True

    def validateIpGeoMetadata(self, _details, _banned, _override):
        return (True, "")


@dataclass
class DummyConnection:
    no_keep_alive: bool = False


@dataclass
class DummyRequest:
    method: str = "GET"
    uri: str = "/"
    headers: dict = field(default_factory=dict)
    client_address: list = field(default_factory=lambda: ["198.51.100.77"])
    connection: DummyConnection = field(default_factory=DummyConnection)
    suppress_log_entry: bool = False
    redirected_to_c2: bool = False
    server_port: int = 80
    is_ssl: bool = False


def merge_nested(target, updates):
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            merge_nested(target[key], value)
        else:
            target[key] = value


@pytest.fixture
def request_factory():
    def _factory(method="GET", uri="/", headers=None, ip="198.51.100.77"):
        merged = {
            "Host": "edge.example",
            "User-Agent": "Mozilla/5.0",
        }
        if headers:
            merged.update(headers)
        return DummyRequest(method=method, uri=uri, headers=merged, client_address=[ip])

    return _factory


@pytest.fixture
def plugin_factory(tmp_path, monkeypatch):
    def _factory(option_overrides=None, banned_agents=None, override_banned_agents=None):
        monkeypatch.setattr(
            redirector.ProxyPlugin,
            "DynamicWhitelistFile",
            str(tmp_path / ".peers.sqlite"),
            raising=False,
        )
        monkeypatch.setattr(
            redirector.ProxyPlugin,
            "RequestsHashesDatabaseFile",
            str(tmp_path / ".anti-replay.sqlite"),
            raising=False,
        )
        monkeypatch.setattr(redirector, "BANNED_AGENTS", list(banned_agents or []))
        monkeypatch.setattr(redirector, "OVERRIDE_BANNED_AGENTS", list(override_banned_agents or []))
        monkeypatch.setattr(redirector, "alreadyPrintedPeers", set())

        options = copy.deepcopy(BASE_OPTIONS)
        if option_overrides:
            merge_nested(options, option_overrides)

        logger = RecordingLogger()
        plugin = redirector.ProxyPlugin(logger, options)
        plugin.ipLookupHelper = NullLookup()
        plugin.ipGeolocationDeterminer = AllowAllDeterminant()

        return plugin, logger

    return _factory
