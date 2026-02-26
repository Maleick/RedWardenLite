import ipaddress
import json
from urllib.parse import urlparse

from lib.transport_runtime import as_bool


VALID_RUNTIME_PROFILES = {"compatible", "strict"}
VALID_VALIDATION_OUTPUTS = {"human", "json"}
RUNTIME_HARDENING_EXIT_CODE = 2


def normalize_runtime_profile(value):
    lowered = str(value or "compatible").strip().lower()
    if lowered not in VALID_RUNTIME_PROFILES:
        return "compatible"
    return lowered


def normalize_validation_output(value):
    lowered = str(value or "human").strip().lower()
    if lowered not in VALID_VALIDATION_OUTPUTS:
        return "human"
    return lowered


def _normalize_bind_host(bind_value):
    text = str(bind_value or "0.0.0.0").strip()
    if "://" in text:
        parsed = urlparse(text)
        host = parsed.hostname or parsed.netloc or parsed.path
        return str(host or "0.0.0.0").strip().lower()
    return text.lower()


def collect_listener_specs(options):
    listeners = []
    bind_default = _normalize_bind_host(options.get("bind", "0.0.0.0"))
    ports = options.get("port", [])
    if not ports:
        ports = [8080]

    for index, entry in enumerate(ports):
        bind = bind_default
        scheme = "http"
        raw = str(entry)
        port_value = 0

        if isinstance(entry, int):
            port_value = entry
        else:
            parse_value = raw.strip()

            if ":" in parse_value and not parse_value.split(":", 1)[0].isdigit():
                bind_part, parse_value = parse_value.split(":", 1)
                bind = _normalize_bind_host(bind_part)

            if "/" in parse_value:
                parse_value, scheme_part = parse_value.split("/", 1)
                scheme = str(scheme_part or "http").strip().lower()

            try:
                port_value = int(parse_value.strip())
            except (TypeError, ValueError):
                port_value = 0

        listeners.append(
            {
                "index": index,
                "raw": raw,
                "bind": bind,
                "scheme": scheme or "http",
                "port": port_value,
            }
        )

    return listeners


def is_public_bind(bind_host):
    host = str(bind_host or "").strip().lower().strip("[]")
    if host in {"127.0.0.1", "localhost", "::1"}:
        return False

    if host in {"0.0.0.0", "::"}:
        return True

    try:
        ip = ipaddress.ip_address(host)
        if ip.is_loopback or ip.is_private or ip.is_link_local:
            return False
        return True
    except ValueError:
        pass

    if host.endswith(".localhost") or host.endswith(".local"):
        return False

    return True


def _finding(identifier, path, reason, safe_example):
    return {
        "id": identifier,
        "path": path,
        "reason": reason,
        "safe_example": safe_example,
    }


def _normalize_ack_tokens(raw_tokens):
    if isinstance(raw_tokens, (list, tuple, set)):
        values = raw_tokens
    else:
        values = str(raw_tokens or "").split(",")

    tokens = set()
    for value in values:
        token = str(value or "").strip().lower()
        if token:
            tokens.add(token)

    return tokens


def _finding_ack_token(finding):
    return "{}@{}".format(
        str(finding.get("id", "")).strip(),
        str(finding.get("path", "")).strip(),
    ).lower()


def _is_finding_acknowledged(finding, ack_tokens):
    finding_id = str(finding.get("id", "")).strip().lower()
    return finding_id in ack_tokens or _finding_ack_token(finding) in ack_tokens


def _collect_strict_unsafe_findings(options):
    findings = []
    listeners = collect_listener_specs(options)

    for listener in listeners:
        if listener["scheme"] == "http" and is_public_bind(listener["bind"]):
            findings.append(
                _finding(
                    "SEC-02-public-http-listener",
                    "port[{}]".format(listener["index"]),
                    'Public listener uses cleartext HTTP on bind "{}" ({}).'.format(
                        listener["bind"], listener["raw"]
                    ),
                    "Set listener to https (for example: 443/https) or bind HTTP listener to localhost/private address.",
                )
            )

    return findings


def evaluate_runtime_hardening(options):
    profile_raw = options.get("runtime_profile", "compatible")
    output_raw = options.get("runtime_hardening_validation_output", "human")

    profile = normalize_runtime_profile(profile_raw)
    output_mode = normalize_validation_output(output_raw)
    allow_unsafe = as_bool(options.get("runtime_hardening_allow_unsafe", False), False)
    unsafe_ack = str(options.get("runtime_hardening_unsafe_ack", "") or "").strip()
    unsafe_ack_ids = options.get("runtime_hardening_unsafe_ack_ids", [])
    unsafe_ack_tokens = _normalize_ack_tokens(unsafe_ack_ids)

    warnings = []
    violations = []

    if str(profile_raw).strip().lower() != profile:
        warnings.append(
            _finding(
                "profile-normalized",
                "runtime_profile",
                'Unsupported runtime profile "{}"; defaulting to "{}".'.format(profile_raw, profile),
                "Use runtime_profile: compatible or runtime_profile: strict.",
            )
        )

    if str(output_raw).strip().lower() != output_mode:
        warnings.append(
            _finding(
                "validation-output-normalized",
                "runtime_hardening_validation_output",
                'Unsupported validation output "{}"; defaulting to "{}".'.format(output_raw, output_mode),
                "Use runtime_hardening_validation_output: human or json.",
            )
        )

    effective_tls_verify = profile == "strict"

    unsafe_findings = _collect_strict_unsafe_findings(options)

    if profile == "compatible":
        warnings.append(
            _finding(
                "compatible-mode-active",
                "runtime_profile",
                "Runtime hardening is running in compatible mode; strict denylist enforcement is not active.",
                "Set runtime_profile: strict to enforce startup hardening checks.",
            )
        )
        for finding in unsafe_findings:
            warnings.append(
                _finding(
                    "compatible-warning-{}".format(finding["id"]),
                    finding["path"],
                    "This setting would fail startup in strict mode: {}".format(finding["reason"]),
                    finding["safe_example"],
                )
            )

    else:
        if unsafe_findings:
            if allow_unsafe:
                if not unsafe_ack:
                    violations.append(
                        _finding(
                            "SEC-02-unsafe-override-missing-ack",
                            "runtime_hardening_unsafe_ack",
                            "Unsafe override is enabled without explicit acknowledgement.",
                            'Set runtime_hardening_unsafe_ack to a non-empty acknowledgement (for example: "accepted-risk-2026-02-25").',
                        )
                    )
                else:
                    unacknowledged = [
                        finding for finding in unsafe_findings if not _is_finding_acknowledged(finding, unsafe_ack_tokens)
                    ]

                    if unacknowledged:
                        missing_tokens = [
                            "{}@{}".format(item["id"], item["path"]) for item in unacknowledged
                        ]
                        violations.append(
                            _finding(
                                "SECX-01-unsafe-override-missing-check-ack",
                                "runtime_hardening_unsafe_ack_ids",
                                "Unsafe override is enabled without per-check acknowledgement for: {}.".format(
                                    ", ".join(missing_tokens)
                                ),
                                'Set runtime_hardening_unsafe_ack_ids to include each finding id/path (for example: ["SEC-02-public-http-listener@port[0]"]).',
                            )
                        )
                    else:
                        warnings.append(
                            _finding(
                                "SEC-02-unsafe-override-active",
                                "runtime_hardening_allow_unsafe",
                                "Unsafe strict-mode findings were bypassed by explicit override acknowledgement.",
                                "Disable runtime_hardening_allow_unsafe after remediation to restore strict enforcement.",
                            )
                        )
                        for finding in unsafe_findings:
                            warnings.append(
                                _finding(
                                    "overridden-{}".format(finding["id"]),
                                    finding["path"],
                                    finding["reason"],
                                    finding["safe_example"],
                                )
                            )
            else:
                violations.extend(unsafe_findings)

    fail = len(violations) > 0

    return {
        "profile": profile,
        "output_mode": output_mode,
        "allow_unsafe": allow_unsafe,
        "unsafe_ack": unsafe_ack,
        "unsafe_ack_ids": sorted(unsafe_ack_tokens),
        "effective": {
            "runtime_profile": profile,
            "runtime_hardening_validation_output": output_mode,
            "runtime_tls_verify_upstream": effective_tls_verify,
        },
        "warnings": warnings,
        "violations": violations,
        "fail": fail,
        "exit_code": RUNTIME_HARDENING_EXIT_CODE if fail else 0,
    }


def apply_runtime_hardening_effective(options, report):
    effective = report.get("effective", {})
    for key, value in effective.items():
        options[key] = value


def format_runtime_hardening_report(report):
    output_mode = normalize_validation_output(report.get("output_mode", "human"))
    if output_mode == "json":
        return json.dumps(report, sort_keys=True)

    violations = report.get("violations", [])
    warnings = report.get("warnings", [])

    lines = []
    if report.get("fail", False):
        lines.append(
            "Runtime hardening validation failed with {} issue(s).".format(len(violations))
        )
    else:
        lines.append("Runtime hardening validation passed.")

    if violations:
        lines.append("")
        lines.append("Violations:")
        for finding in violations:
            lines.append("- [{}] {}".format(finding["id"], finding["path"]))
            lines.append("  Reason: {}".format(finding["reason"]))
            lines.append("  Safe example: {}".format(finding["safe_example"]))

    if warnings:
        lines.append("")
        lines.append("Warnings:")
        for finding in warnings:
            lines.append("- [{}] {}".format(finding["id"], finding["path"]))
            lines.append("  Reason: {}".format(finding["reason"]))
            lines.append("  Safe example: {}".format(finding["safe_example"]))

    return "\n".join(lines)
