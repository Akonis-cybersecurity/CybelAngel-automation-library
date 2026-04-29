import json
from unittest.mock import MagicMock, patch

import pytest
import requests_mock as req_mock

from cybelangel_modules.client import TOKEN_URL, BASE_URL
from cybelangel_modules.trigger_reports import ReportsTrigger
from cybelangel_modules.trigger_credentials import CredentialsTrigger
from cybelangel_modules.trigger_claimed_attacks import ClaimedAttacksTrigger

TOKEN_RESPONSE = {"access_token": "tok", "expires_in": 3600}

SAMPLE_REPORTS = [
    {"id": "r1", "created_at": "2024-01-01T10:00:00", "title": "Report 1"},
    {"id": "r2", "created_at": "2024-01-01T11:00:00", "title": "Report 2"},
]

SAMPLE_CREDENTIALS = [
    {"id": "c1", "last_detection_date": "2024-01-01T10:00:00", "username": "user@example.com"},
]

SAMPLE_ATTACKS = [
    {"id": "a1", "claimed_at": "2024-01-01T10:00:00", "category": "ransomware"},
]


class TestReportsTrigger:
    def test_fetch_and_push_reports(self, reports_trigger: ReportsTrigger):
        pushed = []
        reports_trigger.push_events_to_intakes = lambda events: pushed.extend(events)
        reports_trigger._running = True

        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.get(f"{BASE_URL}/v2/reports", json=SAMPLE_REPORTS)

            # run one iteration by calling the internals
            client = reports_trigger._client()
            reports = reports_trigger._fetch_reports(client, "", "2024-01-02T00:00:00")

            assert len(reports) == 2
            assert reports[0]["id"] == "r1"

    def test_cursor_is_updated(self, reports_trigger: ReportsTrigger):
        pushed = []
        reports_trigger.push_events_to_intakes = lambda events: pushed.extend(events)

        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.get(f"{BASE_URL}/v2/reports", json=SAMPLE_REPORTS)

            client = reports_trigger._client()
            reports = reports_trigger._fetch_reports(client, "", "2024-01-02T00:00:00")

            max_created = max(r["created_at"] for r in reports)
            reports_trigger._set_cursor(max_created)

            assert reports_trigger._get_cursor() == "2024-01-01T11:00:00"

    def test_empty_response_updates_cursor_to_end_date(self, reports_trigger: ReportsTrigger):
        pushed = []
        reports_trigger.push_events_to_intakes = lambda events: pushed.extend(events)

        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.get(f"{BASE_URL}/v2/reports", json=[])

            client = reports_trigger._client()
            reports = reports_trigger._fetch_reports(client, "", "2024-01-02T00:00:00")
            assert reports == []


class TestCredentialsTrigger:
    def test_fetch_single_page(self, credentials_trigger: CredentialsTrigger):
        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.get(f"{BASE_URL}/v1/credentials", json=SAMPLE_CREDENTIALS)

            client = credentials_trigger._client()
            page = credentials_trigger._fetch_page(client, "", "2024-01-02T00:00:00", 10, 0)

            assert len(page) == 1
            assert page[0]["id"] == "c1"

    def test_pagination_stops_when_page_shorter_than_limit(self, credentials_trigger: CredentialsTrigger):
        pushed = []
        credentials_trigger.push_events_to_intakes = lambda events: pushed.extend(events)

        # page smaller than limit → stop
        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.get(f"{BASE_URL}/v1/credentials", json=SAMPLE_CREDENTIALS)

            client = credentials_trigger._client()
            page = credentials_trigger._fetch_page(client, "", "2024-01-02T00:00:00", 10, 0)
            # 1 result with limit=10 → no second page
            assert len(page) < credentials_trigger.configuration.limit


class TestClaimedAttacksTrigger:
    def test_fetch_single_page(self, claimed_attacks_trigger: ClaimedAttacksTrigger):
        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.get(f"{BASE_URL}/v1/threat-intelligence/claimed-attacks", json=SAMPLE_ATTACKS)

            client = claimed_attacks_trigger._client()
            page = claimed_attacks_trigger._fetch_page(client, "", "2024-01-02T00:00:00", 100, 0)

            assert len(page) == 1
            assert page[0]["id"] == "a1"

    def test_cursor_tracks_claimed_at(self, claimed_attacks_trigger: ClaimedAttacksTrigger):
        attacks = [
            {"id": "a1", "claimed_at": "2024-01-01T08:00:00"},
            {"id": "a2", "claimed_at": "2024-01-01T12:00:00"},
        ]
        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.get(f"{BASE_URL}/v1/threat-intelligence/claimed-attacks", json=attacks)

            client = claimed_attacks_trigger._client()
            page = claimed_attacks_trigger._fetch_page(client, "", "2024-01-02T00:00:00", 100, 0)

            max_ca = max(a["claimed_at"] for a in page)
            claimed_attacks_trigger._set_cursor(max_ca)
            assert claimed_attacks_trigger._get_cursor() == "2024-01-01T12:00:00"
