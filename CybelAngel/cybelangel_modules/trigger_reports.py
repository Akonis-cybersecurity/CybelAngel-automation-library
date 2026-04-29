import json
import time
from datetime import datetime, timezone

from sekoia_automation.connector import Connector
from sekoia_automation.storage import PersistentJSON

from cybelangel_modules import CybelangelModule
from cybelangel_modules.client import CybelangelClient
from cybelangel_modules.models import ReportsTriggerConfiguration

CURSOR_KEY = "reports_cursor"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


class ReportsTrigger(Connector):
    module: CybelangelModule
    configuration: ReportsTriggerConfiguration

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

    def _fetch_reports(self, client: CybelangelClient, start_date: str, end_date: str) -> list:
        params: dict = {}
        if start_date:
            params["start-date"] = start_date
        params["end-date"] = end_date

        resp = client.get("/v2/reports", params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return data
        return data.get("reports", data.get("data", []))

    def run(self) -> None:
        client = self._client()

        while self.running:
            try:
                now = datetime.now(timezone.utc)
                end_date = now.strftime(DATE_FORMAT)
                cursor = self._get_cursor()
                start_date = cursor if cursor else ""

                reports = self._fetch_reports(client, start_date, end_date)

                if reports:
                    # sort ascending by created_at and update cursor
                    def _created_at(r: dict) -> str:
                        return r.get("created_at", "")

                    reports_sorted = sorted(reports, key=_created_at)
                    max_created_at = max(_created_at(r) for r in reports_sorted)

                    batch = [json.dumps(r) for r in reports_sorted]
                    self.push_events_to_intakes(events=batch)
                    self.log(message=f"ReportsTrigger: pushed {len(batch)} events", level="info")

                    self._set_cursor(max_created_at)
                else:
                    # advance cursor even when no results to avoid re-querying same window
                    self._set_cursor(end_date)
                    self.log(message="ReportsTrigger: no new reports", level="info")

            except Exception as exc:
                self.log_exception(exc, message="ReportsTrigger: error fetching reports")

            time.sleep(self.configuration.frequency)
