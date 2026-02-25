from plugins.IProxyPlugin import proxy2_metadata_headers


class ActionExecutor:
    """Centralized side-effect execution for policy decisions."""

    def __init__(self, plugin):
        self.plugin = plugin

    def execute(self, decision, peer_ip, ts, req):
        matched_status = bool(decision.metadata.get("matched_status", False))
        user_agent = req.headers.get("User-Agent")
        override_host = decision.metadata.get("override_host_header")

        if override_host:
            req.headers[proxy2_metadata_headers["override_host_header"]] = override_host

        # Reason 99 / unmatched path should preserve existing contract: no early return.
        if not matched_status:
            return False, False

        if decision.action == "drop":
            if decision.message:
                self.plugin.drop_reason(decision.message)
            if decision.reason in {"2", "3", "4a", "4b"}:
                self.plugin._print_peer_info(peer_ip)
            return True, self.plugin.report(True, ts, peer_ip, req.uri, user_agent, decision.reason)

        if decision.action == "allow":
            if decision.message and decision.reason in ("1", "2"):
                self.plugin.logger.info(decision.message, color="green")
            return True, self.plugin.report(False, ts, peer_ip, req.uri, user_agent, decision.reason)

        # Fallback for unrecognized actions.
        return matched_status, self.plugin.report(
            not decision.allow,
            ts,
            peer_ip,
            req.uri,
            user_agent,
            decision.reason,
        )
