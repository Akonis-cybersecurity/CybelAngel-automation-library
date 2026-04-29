from cybelangel_modules.actions.base import CybelangelAction


class GetReportById(CybelangelAction):
    def run(self, arguments: dict) -> dict:
        report_id = arguments["report_id"]
        client = self._client()
        resp = client.get(f"/v2/reports/{report_id}", timeout=30)
        resp.raise_for_status()
        return resp.json()
