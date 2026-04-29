from cybelangel_modules.actions.base import CybelangelAction


class CreateRemediationRequest(CybelangelAction):
    def run(self, arguments: dict) -> dict:
        report_id = arguments["report_id"]
        payload = {k: v for k, v in arguments.items() if k != "report_id"}
        client = self._client()
        resp = client.post(f"/v1/reports/{report_id}/remediation", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json() if resp.content else {"status": "created"}
