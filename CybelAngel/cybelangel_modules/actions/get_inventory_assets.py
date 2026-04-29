from cybelangel_modules.actions.base import CybelangelAction


class GetInventoryAssets(CybelangelAction):
    def run(self, arguments: dict) -> dict:
        params = {k: v for k, v in arguments.items() if v is not None}
        client = self._client()
        resp = client.get("/v1/adm/assets", params=params, timeout=60)
        resp.raise_for_status()
        return resp.json()
