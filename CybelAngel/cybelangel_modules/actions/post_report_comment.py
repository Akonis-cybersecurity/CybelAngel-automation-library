from cybelangel_modules.actions.base import CybelangelAction


class PostReportComment(CybelangelAction):
    def run(self, arguments: dict) -> dict:
        report_id = arguments["report_id"]
        comment = arguments["comment"]
        client = self._client()
        resp = client.post(f"/v1/reports/{report_id}/comments", json={"comment": comment}, timeout=30)
        resp.raise_for_status()
        return resp.json() if resp.content else {"status": "created"}
