from cybelangel_modules.actions.base import CybelangelAction


class UpdateInventoryAssetStatus(CybelangelAction):
    def run(self, arguments: dict) -> dict:
        asset_id = arguments["asset_id"]
        status = arguments["status"]
        client = self._client()
        resp = client.put(f"/v1/adm/assets/{asset_id}/status", json={"status": status}, timeout=30)
        resp.raise_for_status()
        return resp.json() if resp.content else {"status": "updated"}
