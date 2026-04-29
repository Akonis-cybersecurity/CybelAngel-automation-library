from cybelangel_modules.actions.base import CybelangelAction


class GetReportAttachments(CybelangelAction):
    def run(self, arguments: dict) -> dict:
        report_id = arguments["report_id"]
        client = self._client()
        resp = client.get(f"/v1/reports/{report_id}/attachments", timeout=30)
        resp.raise_for_status()
        return resp.json()
