def run(plugin, peer_ip, ts, req, req_body, return_json, resp_json):
    out = plugin._drop_request_without_expected_header_check(peer_ip, ts, req, return_json, resp_json)
    if out is not None:
        return out

    out = plugin._drop_request_without_expected_header_value_check(peer_ip, ts, req, return_json, resp_json)
    if out is not None:
        return out

    out = plugin._drop_request_without_expected_http_method_check(peer_ip, ts, req, return_json, resp_json)
    if out is not None:
        return out

    out = plugin._drop_request_without_expected_uri_check(peer_ip, ts, req, return_json, resp_json)
    if out is not None:
        return out

    return None
