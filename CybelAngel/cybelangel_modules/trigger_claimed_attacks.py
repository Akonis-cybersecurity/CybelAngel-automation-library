import json
import time
from datetime import datetime, timezone

from sekoia_automation.connector import Connector
from sekoia_automation.storage import PersistentJSON

from cybelangel_modules import CybelangelModule
from cybelangel_modules.client import CybelangelClient
from cybelangel_modules.models import ClaimedAttacksTriggerConfiguration

CURSOR_KEY = "claimed_attacks_cursor"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


class ClaimedAttacksTrigger(Connector):
    module: CybelangelModule
    configuration: ClaimedAttacksTriggerConfiguration

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._context = PersistentJSON("context.json", self._data_path)

    def _client(self) -> CybelangelClient:
        cfg = self.module.configuration
        secret = cfg.client_secret
        secret_val = secret.get_secret_value() if hasattr(secret, "get_secret_value") else secret
        return CybelangelClient(client_id=cfg.client_id, client_secret=secret_val)

    def _get_cursor(self) -> str:
        with self._context as ctx:
            return ctx.get(CURSOR_KEY, "")

    def _set_cursor(self, value: str) -> None:
        with self._context as ctx:
            ctx[CURSOR_KEY] = value

    def _fetch_page(self, client: CybelangelClient, start_date: str, end_date: str, limit: int, skip: int) -> list:
        params: dict = {
            "limit": limit,
            "skip": skip,
            "sort_order": "asc",
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        resp = client.get("/v1/threat-intelligence/claimed-attacks", params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return data
        return data.get("claimed_attacks", data.get("data", data.get("results", [])))

    def run(self) -> None:
        client = self._client()

        while self.running:
            try:
                now = datetime.now(timezone.utc)
                end_date = now.strftime(DATE_FORMAT)
                cursor = self._get_cursor()
                start_date = cursor if cursor else ""

                limit = self.configuration.limit
                skip = 0
                max_claimed_at = cursor
                total_pushed = 0

                while self.running:
                    page = self._fetch_page(client, start_date, end_date, limit, skip)
                    if not page:
                        break

                    batch = [json.dumps(attack) for attack in page]
                    self.push_events_to_intakes(events=batch)
                    total_pushed += len(batch)

                    # track max claimed_at seen
                    for attack in page:
                        ca = attack.get("claimed_at", "")
                        if ca and (not max_claimed_at or ca > max_claimed_at):
                            max_claimed_at = ca

                    if len(page) < limit:
                        break
                    skip += limit

                if max_claimed_at:
                    self._set_cursor(max_claimed_at)

                self.log(message=f"ClaimedAttacksTrigger: pushed {total_pushed} events", level="info")

            except Exception as exc:
                self.log_exception(exc, message="ClaimedAttacksTrigger: error fetching claimed attacks")

            time.sleep(self.configuration.frequency)
