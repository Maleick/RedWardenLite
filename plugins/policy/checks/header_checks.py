def run(plugin, peer_ip, ts, req, req_body, return_json, resp_json):
    return plugin._drop_http_banned_header_names_check(peer_ip, ts, req, return_json, resp_json)
