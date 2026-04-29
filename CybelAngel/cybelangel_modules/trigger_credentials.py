import json
import time
from datetime import datetime, timezone

from sekoia_automation.connector import Connector
from sekoia_automation.storage import PersistentJSON

from cybelangel_modules import CybelangelModule
from cybelangel_modules.client import CybelangelClient
from cybelangel_modules.models import CredentialsTriggerConfiguration

CURSOR_KEY = "credentials_cursor"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


class CredentialsTrigger(Connector):
    module: CybelangelModule
    configuration: CredentialsTriggerConfiguration

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

    def _fetch_page(self, client: CybelangelClient, start: str, end: str, limit: int, skip: int) -> list:
        params: dict = {
            "limit": limit,
            "skip": skip,
            "order": "asc",
            "sort_by": "last_detection_date",
        }
        if start:
            params["start"] = start
        if end:
            params["end"] = end

        resp = client.get("/v1/credentials", params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return data
        return data.get("credentials", data.get("data", []))

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
                max_detection_date = cursor
                total_pushed = 0

                while self.running:
                    page = self._fetch_page(client, start_date, end_date, limit, skip)
                    if not page:
                        break

                    batch = [json.dumps(c) for c in page]
                    self.push_events_to_intakes(events=batch)
                    total_pushed += len(batch)

                    # track max last_detection_date seen
                    for cred in page:
                        dt = cred.get("last_detection_date", "")
                        if dt and (not max_detection_date or dt > max_detection_date):
                            max_detection_date = dt

                    if len(page) < limit:
                        break
                    skip += limit

                if max_detection_date:
                    self._set_cursor(max_detection_date)

                self.log(message=f"CredentialsTrigger: pushed {total_pushed} events", level="info")

            except Exception as exc:
                self.log_exception(exc, message="CredentialsTrigger: error fetching credentials")

            time.sleep(self.configuration.frequency)
