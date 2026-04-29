import base64

from cybelangel_modules.actions.base import CybelangelAction


class GetReportPdf(CybelangelAction):
    def run(self, arguments: dict) -> dict:
        report_id = arguments["report_id"]
        client = self._client()
        resp = client.get(f"/v1/reports/{report_id}/pdf", timeout=60)
        resp.raise_for_status()
        return {"content_base64": base64.b64encode(resp.content).decode("utf-8"), "content_type": "application/pdf"}
