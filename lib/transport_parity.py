import gzip
import hashlib
import json
import os
import re
import zlib
from datetime import datetime, timezone
from io import BytesIO

import brotli


HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}

KNOWN_VOLATILE_HEADERS = {
    "date",
    "server",
    "via",
    "x-request-id",
    "x-amzn-trace-id",
    "x-forwarded-for",
    "x-forwarded-proto",
    "cf-ray",
    "cf-cache-status",
    "age",
}


def _to_bytes(value):
    if value is None:
        return b""
    if isinstance(value, bytes):
        return value
    return str(value).encode(errors="ignore")


def _get_header(headers, key, default=""):
    if not headers:
        return default

    key_l = key.lower()
    for header_key, header_value in headers.items():
        if str(header_key).lower() == key_l:
            return header_value
    return default


def decode_body(data, encoding):
    body = _to_bytes(data)
    enc = str(encoding or "identity").lower().strip()

    if enc in ("", "identity"):
        return body
    if enc in ("gzip", "x-gzip"):
        try:
            with gzip.GzipFile(fileobj=BytesIO(body)) as gz_file:
                return gz_file.read()
        except Exception:
            return body
    if enc == "deflate":
        try:
            return zlib.decompress(body)
        except zlib.error:
            try:
                return zlib.decompress(body, -zlib.MAX_WBITS)
            except Exception:
                return body
    if enc == "br":
        try:
            return brotli.decompress(body)
        except Exception:
            return body

    return body


def normalize_headers(headers, extra_ignored=None):
    ignored = {h.lower() for h in HOP_BY_HOP_HEADERS}
    ignored.update({h.lower() for h in KNOWN_VOLATILE_HEADERS})
    ignored.update({str(h).lower() for h in (extra_ignored or [])})

    normalized = {}
    for key, value in (headers or {}).items():
        lowered = str(key).lower()
        if lowered in ignored:
            continue

        if isinstance(value, (list, tuple)):
            normalized[lowered] = ",".join(str(item) for item in value)
        else:
            normalized[lowered] = str(value)

    return normalized


def compare_transport_results(primary, shadow, header_ignore=None):
    mismatches = []

    p_status = int(primary.get("status", 0))
    s_status = int(shadow.get("status", 0))

    if p_status != s_status:
        mismatches.append(
            {
                "type": "status",
                "id": f"status:{p_status}!={s_status}",
                "primary": p_status,
                "shadow": s_status,
            }
        )

    primary_headers = normalize_headers(primary.get("headers", {}), header_ignore)
    shadow_headers = normalize_headers(shadow.get("headers", {}), header_ignore)

    for header in sorted(set(primary_headers) | set(shadow_headers)):
        p_val = primary_headers.get(header)
        s_val = shadow_headers.get(header)
        if p_val != s_val:
            mismatches.append(
                {
                    "type": "header",
                    "id": f"header:{header}",
                    "header": header,
                    "primary": p_val,
                    "shadow": s_val,
                }
            )

    p_encoding = _get_header(primary.get("headers", {}), "content-encoding", "identity")
    s_encoding = _get_header(shadow.get("headers", {}), "content-encoding", "identity")

    p_body = decode_body(primary.get("body", b""), p_encoding)
    s_body = decode_body(shadow.get("body", b""), s_encoding)

    if p_body != s_body:
        p_hash = hashlib.sha256(p_body).hexdigest()
        s_hash = hashlib.sha256(s_body).hexdigest()
        mismatches.append(
            {
                "type": "body",
                "id": "body:sha256",
                "primary_sha256": p_hash,
                "shadow_sha256": s_hash,
                "primary_len": len(p_body),
                "shadow_len": len(s_body),
            }
        )

    return {
        "match": len(mismatches) == 0,
        "mismatches": mismatches,
        "primary_status": p_status,
        "shadow_status": s_status,
    }


def load_allowlist_patterns(path):
    if not path or not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as handle:
        loaded = json.load(handle)

    if isinstance(loaded, dict):
        loaded = loaded.get("patterns", [])

    if isinstance(loaded, str):
        loaded = [loaded]

    if not isinstance(loaded, list):
        return []

    patterns = []
    for value in loaded:
        if not isinstance(value, str):
            continue
        stripped = value.strip()
        if stripped:
            patterns.append(stripped)

    return patterns


def apply_allowlist(mismatches, patterns):
    if not patterns:
        return [], list(mismatches)

    allowlisted = []
    unresolved = []

    for mismatch in mismatches:
        mismatch_id = mismatch.get("id", "")
        is_allowed = any(re.search(pattern, mismatch_id) for pattern in patterns)
        if is_allowed:
            allowlisted.append(mismatch)
        else:
            unresolved.append(mismatch)

    return allowlisted, unresolved


def write_parity_artifacts(artifact_dir, event):
    os.makedirs(artifact_dir, exist_ok=True)

    jsonl_path = os.path.join(artifact_dir, "parity-events.jsonl")
    summary_path = os.path.join(artifact_dir, "parity-summary.md")

    with open(jsonl_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")

    events = []
    with open(jsonl_path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    total = len(events)
    mismatched = sum(1 for item in events if item.get("unresolved_count", 0) > 0)
    allowlisted = sum(1 for item in events if item.get("allowlisted_count", 0) > 0)

    with open(summary_path, "w", encoding="utf-8") as handle:
        handle.write("# Transport Parity Summary\n\n")
        generated = datetime.now(timezone.utc).isoformat()
        handle.write(f"Generated: {generated}\n\n")
        handle.write(f"- Total parity events: {total}\n")
        handle.write(f"- Events with unresolved mismatches: {mismatched}\n")
        handle.write(f"- Events with allowlisted mismatches: {allowlisted}\n\n")

        handle.write("## Recent Events\n\n")
        handle.write("| Timestamp | Method | Path | Primary | Shadow | Unresolved |\n")
        handle.write("|-----------|--------|------|---------|--------|------------|\n")
        for item in events[-20:]:
            ts = item.get("timestamp", "-")
            method = item.get("method", "-")
            path = item.get("path", "-")
            primary = item.get("primary_transport", "-")
            shadow = item.get("shadow_transport", "-")
            unresolved_count = item.get("unresolved_count", 0)
            handle.write(
                f"| {ts} | {method} | {path} | {primary} | {shadow} | {unresolved_count} |\n"
            )

    return {
        "jsonl": jsonl_path,
        "summary": summary_path,
    }
