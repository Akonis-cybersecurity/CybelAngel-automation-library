from cybelangel_modules.actions.base import CybelangelAction

VALID_STATUSES = {"draft", "open", "in_progress", "resolved", "discarded"}


class UpdateReportStatus(CybelangelAction):
    def run(self, arguments: dict) -> dict:
        report_id = arguments["report_id"]
        status = arguments["status"]
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {sorted(VALID_STATUSES)}")

        client = self._client()
        resp = client.put(f"/v1/reports/{report_id}/status", json={"status": status}, timeout=30)
        resp.raise_for_status()
        return resp.json() if resp.content else {"status": "updated"}
