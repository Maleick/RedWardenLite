import uuid
from pathlib import Path
from types import SimpleNamespace

import lib.proxyhandler as proxyhandler
from lib.plugin_contracts import normalize_plugin_isolation_mode
from lib.pluginsloader import PluginsLoader


class CaptureLogger:
    def __init__(self):
        self.events = []

    def info(self, text, **kwargs):
        self.events.append(("info", str(text)))

    def dbg(self, text, **kwargs):
        self.events.append(("debug", str(text)))

    def err(self, text, **kwargs):
        self.events.append(("error", str(text)))

    def fatal(self, text, **kwargs):
        raise RuntimeError(str(text))

    def contains(self, needle):
        return any(needle in message for _, message in self.events)


def _write_plugin(tmp_path, module_name, metadata=None):
    plugin_path = Path(tmp_path) / "{}.py".format(module_name)
    metadata_line = ""
    if metadata is not None:
        metadata_line = "    PLUGIN_METADATA = {}\n".format(repr(metadata))

    plugin_code = (
        "from plugins.IProxyPlugin import IProxyPlugin\n"
        "class ProxyPlugin(IProxyPlugin):\n"
        "{}"
        "    @staticmethod\n"
        "    def get_name():\n"
        "        return '{}'\n"
        "    def help(self, parser):\n"
        "        return None\n"
        "    def request_handler(self, req, req_body):\n"
        "        return req_body\n"
        "    def response_handler(self, req, req_body, res, res_body):\n"
        "        return res_body\n"
    ).format(metadata_line, module_name)

    plugin_path.write_text(plugin_code, encoding="utf-8")
    return plugin_path


def _load_plugin(plugin_path, **overrides):
    options = {
        "plugins": [str(plugin_path)],
        "plugin_class_name": "ProxyPlugin",
        "debug": False,
        "plugin_api_version": "1.0",
        "plugin_require_capabilities": True,
    }
    options.update(overrides)

    logger = CaptureLogger()
    loader = PluginsLoader(logger, options)
    return loader, logger


def _runtime_handler(plugins, mode):
    handler = proxyhandler.ProxyRequestHandler.__new__(proxyhandler.ProxyRequestHandler)
    handler.plugins = plugins
    handler.logger = CaptureLogger()
    handler.options = {
        "debug": False,
        "plugin_isolation_enabled": True,
        "plugin_isolation_failure_mode": mode,
    }
    return handler


def _request():
    return SimpleNamespace(
        headers={"Host": "edge.example"},
        uri="/collect",
        connection=SimpleNamespace(no_keep_alive=False),
    )


def _response():
    return SimpleNamespace(headers={})


def test_loader_accepts_valid_declared_metadata(tmp_path):
    module_name = "plugin_{}".format(uuid.uuid4().hex[:8])
    plugin_path = _write_plugin(
        tmp_path,
        module_name,
        metadata={
            "schema_version": "1",
            "plugin_name": module_name,
            "plugin_version": "1.2.3",
            "core_api_version": "1.0",
            "capabilities": ["request_handler", "response_handler"],
        },
    )

    loader, _ = _load_plugin(plugin_path)
    metadata = loader.get_plugin_metadata()[module_name]

    assert module_name in loader.get_plugins()
    assert metadata["metadata_source"] == "declared"
    assert metadata["core_api_version"] == "1.0"


def test_loader_rejects_missing_metadata_when_required(tmp_path):
    module_name = "plugin_{}".format(uuid.uuid4().hex[:8])
    plugin_path = _write_plugin(tmp_path, module_name, metadata=None)

    try:
        _load_plugin(plugin_path, plugin_require_capabilities=True)
        assert False, "Expected TypeError for missing plugin metadata."
    except TypeError as exc:
        assert "missing required" in str(exc)


def test_loader_allows_legacy_plugin_when_metadata_enforcement_disabled(tmp_path):
    module_name = "plugin_{}".format(uuid.uuid4().hex[:8])
    plugin_path = _write_plugin(tmp_path, module_name, metadata=None)

    loader, _ = _load_plugin(plugin_path, plugin_require_capabilities=False)
    metadata = loader.get_plugin_metadata()[module_name]

    assert module_name in loader.get_plugins()
    assert metadata["metadata_source"] == "legacy-fallback"


def test_loader_rejects_incompatible_api_major_version(tmp_path):
    module_name = "plugin_{}".format(uuid.uuid4().hex[:8])
    plugin_path = _write_plugin(
        tmp_path,
        module_name,
        metadata={
            "schema_version": "1",
            "plugin_name": module_name,
            "plugin_version": "1.0.0",
            "core_api_version": "2.0",
            "capabilities": ["request_handler"],
        },
    )

    try:
        _load_plugin(plugin_path, plugin_api_version="1.0")
        assert False, "Expected TypeError for incompatible plugin API."
    except TypeError as exc:
        assert "incompatible" in str(exc)


def test_runtime_request_handler_fail_closed_returns_drop_exception():
    class CrashPlugin:
        def request_handler(self, req, req_body):
            raise RuntimeError("boom")

    handler = _runtime_handler({"crash": CrashPlugin()}, mode="fail_closed")
    modified, payload = proxyhandler.ProxyRequestHandler.request_handler(handler, _request(), b"abc")

    assert modified is False
    assert "DropConnectionException" in str(type(payload))
    assert handler.logger.contains("FAIL-CLOSED")


def test_runtime_request_handler_fail_open_preserves_request_flow():
    class CrashPlugin:
        def request_handler(self, req, req_body):
            raise RuntimeError("boom")

    handler = _runtime_handler({"crash": CrashPlugin()}, mode="fail_open")
    modified, payload = proxyhandler.ProxyRequestHandler.request_handler(handler, _request(), b"abc")

    assert modified is False
    assert payload == b"abc"
    assert handler.logger.contains("FAIL-OPEN")


def test_runtime_response_handler_fail_closed_returns_drop_exception():
    class CrashPlugin:
        def response_handler(self, req, req_body, res, res_body):
            raise RuntimeError("boom")

    handler = _runtime_handler({"crash": CrashPlugin()}, mode="fail_closed")
    modified, payload = proxyhandler.ProxyRequestHandler.response_handler(
        handler, _request(), b"req", _response(), b"res"
    )

    assert modified is False
    assert "DropConnectionException" in str(type(payload))
    assert handler.logger.contains("FAIL-CLOSED")


def test_runtime_response_handler_fail_open_preserves_response_flow():
    class CrashPlugin:
        def response_handler(self, req, req_body, res, res_body):
            raise RuntimeError("boom")

    handler = _runtime_handler({"crash": CrashPlugin()}, mode="fail_open")
    modified, payload = proxyhandler.ProxyRequestHandler.response_handler(
        handler, _request(), b"req", _response(), b"res"
    )

    assert modified is False
    assert payload == b"res"
    assert handler.logger.contains("FAIL-OPEN")


def test_isolation_mode_normalization_defaults_to_fail_closed():
    assert normalize_plugin_isolation_mode("fail_open") == "fail_open"
    assert normalize_plugin_isolation_mode("unknown-mode") == "fail_closed"


def test_plugin_contract_runbook_includes_schema_and_isolation_modes():
    runbook = (
        Path(__file__).resolve().parents[1] / "docs" / "plugin-contracts.md"
    ).read_text(encoding="utf-8")

    assert "Metadata Schema" in runbook
    assert "plugin_api_version" in runbook
    assert "fail_closed" in runbook
    assert "fail_open" in runbook
