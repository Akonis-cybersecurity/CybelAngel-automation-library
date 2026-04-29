import time

import pytest
import requests_mock as req_mock

from cybelangel_modules.client import (
    CybelangelClient,
    CybelangelAuthError,
    CybelangelRateLimitError,
    TOKEN_URL,
    BASE_URL,
)

TOKEN_RESPONSE = {"access_token": "test-token-abc", "expires_in": 3600}


def test_client_fetches_token_on_first_request():
    with req_mock.Mocker() as m:
        m.post(TOKEN_URL, json=TOKEN_RESPONSE)
        m.get(f"{BASE_URL}/v2/reports", json={"reports": []})

        client = CybelangelClient(client_id="cid", client_secret="csecret")
        resp = client.get("/v2/reports")

        assert resp.status_code == 200
        assert m.call_count == 2  # token + API call


def test_client_reuses_cached_token():
    with req_mock.Mocker() as m:
        m.post(TOKEN_URL, json=TOKEN_RESPONSE)
        m.get(f"{BASE_URL}/v2/reports", json={"reports": []})

        client = CybelangelClient(client_id="cid", client_secret="csecret")
        client.get("/v2/reports")
        client.get("/v2/reports")

        # token should only be fetched once
        token_calls = [r for r in m.request_history if r.url == TOKEN_URL]
        assert len(token_calls) == 1


def test_client_raises_on_auth_failure():
    with req_mock.Mocker() as m:
        m.post(TOKEN_URL, status_code=401)

        client = CybelangelClient(client_id="bad", client_secret="bad")
        with pytest.raises(CybelangelAuthError):
            client.get("/v2/reports")


def test_client_retries_on_429():
    with req_mock.Mocker() as m:
        m.post(TOKEN_URL, json=TOKEN_RESPONSE)
        # first two calls → 429, third → 200
        m.get(f"{BASE_URL}/v2/reports", [
            {"status_code": 429},
            {"status_code": 429},
            {"json": {"reports": []}, "status_code": 200},
        ])

        client = CybelangelClient(client_id="cid", client_secret="csecret")

        # patch sleep so test doesn't actually wait
        import cybelangel_modules.client as client_module
        original_sleep = client_module.time.sleep
        slept = []
        client_module.time.sleep = lambda s: slept.append(s)

        try:
            resp = client.get("/v2/reports")
            assert resp.status_code == 200
            assert slept == [60, 120]  # first two retry delays
        finally:
            client_module.time.sleep = original_sleep


def test_client_raises_rate_limit_after_exhausting_retries():
    with req_mock.Mocker() as m:
        m.post(TOKEN_URL, json=TOKEN_RESPONSE)
        m.get(f"{BASE_URL}/v2/reports", status_code=429)

        client = CybelangelClient(client_id="cid", client_secret="csecret")

        import cybelangel_modules.client as client_module
        client_module.time.sleep = lambda s: None

        with pytest.raises(CybelangelRateLimitError):
            client.get("/v2/reports")
