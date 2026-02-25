def run(plugin, peer_ip, ts, req, req_body, return_json, resp_json):
    out = plugin._whitelist_ip_check(peer_ip, ts, req, return_json, resp_json)
    if out is not None:
        return out

    out = plugin._dynamic_peer_whitelisting_check(peer_ip, ts, req, return_json, resp_json)
    if out is not None:
        return out

    return None
