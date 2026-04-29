from sekoia_automation.action import Action

from cybelangel_modules import CybelangelModule
from cybelangel_modules.client import CybelangelClient


class CybelangelAction(Action):
    module: CybelangelModule

    def _client(self) -> CybelangelClient:
        cfg = self.module.configuration
        secret = cfg.client_secret
        secret_val = secret.get_secret_value() if hasattr(secret, "get_secret_value") else secret
        return CybelangelClient(client_id=cfg.client_id, client_secret=secret_val)
