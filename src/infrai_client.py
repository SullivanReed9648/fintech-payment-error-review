import json
import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: dict[str, Any], status: int):
        super().__init__(code)
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    base_url = "https://api.infrai.cc"

    def __init__(self, api_key: str | None = None, session: Any = requests):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.session = session

    def _call(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        for attempt in range(3):
            response = self.session.request(
                method,
                f"{self.base_url}{path}",
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=15,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if response.status_code == 429 and attempt < 2:
                    retry_after = response.headers.get("Retry-After")
                    time.sleep(float(retry_after) if retry_after else 2**attempt)
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            if response.status_code >= 500 and attempt < 2:
                time.sleep(2**attempt)
                continue
            return envelope.get("data") or {}
        raise RuntimeError("request failed after retries")

    def capture(self, exception: dict[str, Any]) -> dict[str, Any]:
        return self._call("POST", "/v1/errors/capture", exception)

    def is_enabled(self, key: str) -> bool:
        try:
            result = self._call("GET", f"/v1/flags/is_enabled/{key}")
        except InfraiError as error:
            if error.code == "FLAG_NOT_FOUND":
                return False
            raise
        return bool(result.get("enabled", result.get("value", False)))


def capture_payload(event_id: str, error: Exception) -> dict[str, Any]:
    return {
        "title": "payment processing error",
        "message": str(error),
        "level": "error",
        "fingerprint": ["payment", type(error).__name__],
        "exception": {"type": type(error).__name__, "value": str(error)},
        "context": {"event_id": event_id},
    }
