import time
from datetime import datetime, timezone
from typing import Any, Optional

import requests


TOKEN_URL = "https://auth.cybelangel.com/oauth/token"
BASE_URL = "https://platform.cybelangel.com/api"
TOKEN_AUDIENCE = "https://platform.cybelangel.com/"
TOKEN_VALIDITY_SECONDS = 3600
TOKEN_REFRESH_BUFFER_SECONDS = 300  # refresh 5 min before expiry

RETRY_DELAYS = [60, 120, 240]  # seconds for 429 backoff


class CybelangelAuthError(Exception):
    pass


class CybelangelAPIError(Exception):
    pass


class CybelangelRateLimitError(Exception):
    pass


class CybelangelClient:
    def __init__(self, client_id: str, client_secret: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._token: Optional[str] = None
        self._token_expires_at: float = 0.0
        self._session = requests.Session()

    def _is_token_valid(self) -> bool:
        margin = TOKEN_REFRESH_BUFFER_SECONDS
        return self._token is not None and time.time() < (self._token_expires_at - margin)

    def _fetch_token(self) -> None:
        payload = {
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "audience": TOKEN_AUDIENCE,
            "grant_type": "client_credentials",
        }
        resp = self._session.post(TOKEN_URL, json=payload, timeout=30)
        if resp.status_code != 200:
            raise CybelangelAuthError(f"Failed to obtain OAuth2 token: HTTP {resp.status_code}")
        data = resp.json()
        self._token = data["access_token"]
        expires_in = data.get("expires_in", TOKEN_VALIDITY_SECONDS)
        self._token_expires_at = time.time() + expires_in

    def _ensure_token(self) -> str:
        if not self._is_token_valid():
            self._fetch_token()
        assert self._token is not None
        return self._token

    def _auth_headers(self) -> dict:
        return {"Authorization": f"Bearer {self._ensure_token()}"}

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = path if path.startswith("http") else f"{BASE_URL}{path}"
        headers = self._auth_headers()
        headers.update(kwargs.pop("headers", {}))

        for attempt, delay in enumerate(RETRY_DELAYS + [None]):  # type: ignore[list-item]
            resp = self._session.request(method, url, headers=headers, **kwargs)
            if resp.status_code == 429:
                if delay is None:
                    raise CybelangelRateLimitError(f"Rate limit exceeded after {len(RETRY_DELAYS)} retries")
                time.sleep(delay)
                headers = self._auth_headers()
                continue
            return resp

        raise CybelangelRateLimitError("Exhausted retries")  # unreachable but satisfies type checker

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> requests.Response:
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> requests.Response:
        return self._request("PUT", path, **kwargs)
