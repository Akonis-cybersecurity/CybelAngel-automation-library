from typing import List

from cybelangel_modules.actions.base import CybelangelAction

VALID_STATUSES = {"draft", "open", "in_progress", "resolved", "discarded"}


class UpdateMultipleStatuses(CybelangelAction):
    def run(self, arguments: dict) -> dict:
        updates: List[dict] = arguments["updates"]
        for item in updates:
            if item.get("status") not in VALID_STATUSES:
                raise ValueError(
                    f"Invalid status '{item.get('status')}'. Must be one of: {sorted(VALID_STATUSES)}"
                )

        client = self._client()
        resp = client.post("/v1/reports/status", json={"updates": updates}, timeout=30)
        resp.raise_for_status()
        return resp.json() if resp.content else {"status": "updated"}
