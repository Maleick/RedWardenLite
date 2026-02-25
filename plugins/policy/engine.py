from plugins.policy.checks import (
    blacklist_reverse,
    expectation_checks,
    header_checks,
    ipgeo_checks,
    whitelist,
)
from plugins.policy.types import DecisionResult


class PolicyEngine:
    """Deterministic ordered policy evaluation preserving redirector contract."""

    def __init__(self, plugin):
        self.plugin = plugin

    def evaluate(self, peer_ip, ts, req, req_body):
        resp_json = {
            "drop_type": self.plugin.proxyOptions["drop_action"],
            "action_url": self.plugin.proxyOptions["action_url"],
        }

        ordered_runners = (
            whitelist.run,
            blacklist_reverse.run,
            header_checks.run,
            expectation_checks.run,
            ipgeo_checks.run,
        )

        for runner in ordered_runners:
            outcome = runner(self.plugin, peer_ip, ts, req, req_body, True, resp_json)
            if outcome is None:
                continue

            matched_status, payload = outcome
            return self._to_decision(matched_status, payload)

        # Defensive fallback. Current flow should always return from ipgeo checks.
        return DecisionResult(
            allow=True,
            action="allow",
            reason="99",
            message="",
            ipgeo={},
            metadata={
                "matched_status": False,
                "drop_type": resp_json.get("drop_type"),
                "action_url": resp_json.get("action_url"),
            },
        )

    @staticmethod
    def _to_decision(matched_status, payload):
        if isinstance(payload, dict):
            action = payload.get("action", "allow" if not matched_status else "drop")
            reason = str(payload.get("reason", "99"))
            message = str(payload.get("message", ""))
            ipgeo = payload.get("ipgeo", {})
            drop_type = payload.get("drop_type")
            action_url = payload.get("action_url")
            extra_metadata = payload.get("metadata", {})
        else:
            action = "allow" if not matched_status else "drop"
            reason = "99" if action == "allow" else "unknown"
            message = ""
            ipgeo = {}
            drop_type = None
            action_url = None
            extra_metadata = {}

        metadata = {
            "matched_status": bool(matched_status),
            "drop_type": drop_type,
            "action_url": action_url,
        }
        if isinstance(extra_metadata, dict):
            metadata.update(extra_metadata)

        return DecisionResult(
            allow=(action == "allow"),
            action=action,
            reason=reason,
            message=message,
            ipgeo=ipgeo if isinstance(ipgeo, dict) else {},
            metadata=metadata,
        )
