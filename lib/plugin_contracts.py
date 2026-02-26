DEFAULT_PLUGIN_API_VERSION = "1.0"
DEFAULT_PLUGIN_ISOLATION_MODE = "fail_closed"
VALID_PLUGIN_ISOLATION_MODES = {"fail_closed", "fail_open"}


def normalize_plugin_api_version(value):
    text = str(value or DEFAULT_PLUGIN_API_VERSION).strip()
    return text if text else DEFAULT_PLUGIN_API_VERSION


def normalize_plugin_isolation_mode(value):
    text = str(value or DEFAULT_PLUGIN_ISOLATION_MODE).strip().lower()
    if text not in VALID_PLUGIN_ISOLATION_MODES:
        return DEFAULT_PLUGIN_ISOLATION_MODE
    return text


def metadata_from_plugin_class(handler):
    metadata = None

    getter = getattr(handler, "get_metadata", None)
    if callable(getter):
        metadata = getter()

    if metadata is None:
        metadata = getattr(handler, "PLUGIN_METADATA", None)

    return metadata


def _parse_major(version):
    text = normalize_plugin_api_version(version)
    major_text = text.split(".", 1)[0]
    try:
        return int(major_text)
    except (TypeError, ValueError):
        return None


def _normalize_capabilities(raw):
    if not isinstance(raw, (list, tuple, set)):
        raise TypeError("plugin metadata field 'capabilities' must be a list.")

    values = []
    seen = set()
    for item in raw:
        text = str(item or "").strip()
        if not text:
            continue
        lowered = text.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        values.append(lowered)

    if not values:
        raise TypeError("plugin metadata field 'capabilities' must contain at least one capability.")

    return values


def _legacy_fallback_metadata(plugin_name, core_api_version):
    return {
        "schema_version": "1",
        "plugin_name": str(plugin_name).strip().lower(),
        "plugin_version": "legacy",
        "core_api_version": normalize_plugin_api_version(core_api_version),
        "capabilities": ["request_handler", "response_handler"],
        "metadata_source": "legacy-fallback",
    }


def validate_plugin_metadata(plugin_name, raw_metadata, core_api_version, require_metadata=True):
    normalized_plugin_name = str(plugin_name or "").strip().lower()
    if not normalized_plugin_name:
        raise TypeError("plugin name cannot be empty during metadata validation.")

    if raw_metadata is None:
        if require_metadata:
            raise TypeError(
                "plugin '{}' is missing required PLUGIN_METADATA/get_metadata contract.".format(
                    normalized_plugin_name
                )
            )
        return _legacy_fallback_metadata(normalized_plugin_name, core_api_version)

    if not isinstance(raw_metadata, dict):
        raise TypeError(
            "plugin '{}' metadata must be a dict.".format(normalized_plugin_name)
        )

    metadata_name = str(raw_metadata.get("plugin_name", "") or "").strip().lower()
    metadata_version = str(raw_metadata.get("plugin_version", "") or "").strip()
    metadata_api = normalize_plugin_api_version(
        raw_metadata.get("core_api_version", raw_metadata.get("api_version"))
    )
    capabilities = _normalize_capabilities(raw_metadata.get("capabilities", []))

    if not metadata_name:
        raise TypeError("plugin '{}' metadata is missing plugin_name.".format(normalized_plugin_name))
    if metadata_name != normalized_plugin_name:
        raise TypeError(
            "plugin '{}' metadata plugin_name '{}' does not match module name '{}'.".format(
                normalized_plugin_name, metadata_name, normalized_plugin_name
            )
        )
    if not metadata_version:
        raise TypeError("plugin '{}' metadata is missing plugin_version.".format(normalized_plugin_name))

    core_api_normalized = normalize_plugin_api_version(core_api_version)
    metadata_major = _parse_major(metadata_api)
    core_major = _parse_major(core_api_normalized)
    if metadata_major is not None and core_major is not None and metadata_major != core_major:
        raise TypeError(
            "plugin '{}' metadata core_api_version '{}' is incompatible with runtime plugin_api_version '{}'.".format(
                normalized_plugin_name, metadata_api, core_api_normalized
            )
        )

    return {
        "schema_version": str(raw_metadata.get("schema_version", "1") or "1").strip(),
        "plugin_name": metadata_name,
        "plugin_version": metadata_version,
        "core_api_version": metadata_api,
        "capabilities": capabilities,
        "metadata_source": "declared",
    }
