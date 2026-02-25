def run(plugin, peer_ip, ts, req, req_body, return_json, resp_json):
    out = plugin._ban_blacklisted_ip_addresses_check(peer_ip, ts, req, return_json, resp_json)
    if out is not None:
        return out

    out = plugin._drop_dangerous_ip_reverse_lookup_check(peer_ip, ts, req, return_json, resp_json)
    if out is not None:
        return out

    return None
